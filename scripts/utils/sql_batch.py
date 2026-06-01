"""SQL batch splitting and execution helpers."""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Protocol


class Connection(Protocol):
    """Subset of SQLAlchemy Connection used by the batch executor."""

    def exec_driver_sql(self, statement: str) -> Any:
        """Execute one SQL statement."""


def _has_sql(sql: str) -> bool:
    without_block_comments = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    without_line_comments = re.sub(r"--.*($|\n)", "", without_block_comments)
    return bool(without_line_comments.strip())


def _has_balanced_quotes(sql: str) -> bool:
    without_block_comments = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    without_line_comments = re.sub(r"--.*($|\n)", "", without_block_comments)
    return without_line_comments.count("'") % 2 == 0


def split_batch_sql(batch_sql: str) -> list[str]:
    """Split semicolon-delimited SQL while preserving quoted semicolons."""
    statements: list[str] = []
    current = ""

    for fragment in batch_sql.split(";"):
        current = f"{current}{fragment}"
        if _has_balanced_quotes(current):
            if _has_sql(current):
                statements.append(current.strip())
            current = ""
        else:
            current = f"{current};"

    if _has_sql(current):
        raise ValueError("SQL contains an unmatched single quote")
    return statements


def execute_batch_sqls(
    conn: Connection,
    logger: logging.Logger,
    batch_sql: str,
    *,
    max_try_times: int = 3,
) -> int:
    """Split and execute SQL statements with bounded retries."""
    if max_try_times < 1:
        raise ValueError("max_try_times must be at least 1")

    statements = split_batch_sql(batch_sql)
    logger.info("start SQL batch: statements=%d", len(statements))
    batch_started_at = time.time()

    for index, statement in enumerate(statements, start=1):
        for attempt in range(1, max_try_times + 1):
            try:
                statement_started_at = time.time()
                result = conn.exec_driver_sql(statement)
                logger.info(
                    "SQL statement complete: index=%d, attempt=%d, rows=%d, seconds=%.3f",
                    index,
                    attempt,
                    result.rowcount,
                    time.time() - statement_started_at,
                )
                break
            except Exception:
                if attempt == max_try_times:
                    logger.exception("SQL statement failed: index=%d", index)
                    raise
                logger.warning("retry SQL statement: index=%d, attempt=%d", index, attempt)
                time.sleep(3)

    logger.info("SQL batch complete: seconds=%.3f", time.time() - batch_started_at)
    return 1
