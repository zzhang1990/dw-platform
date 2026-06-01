"""StarRocks ETL refresh helpers.

Full-snapshot jobs load a shadow table first and only replace the serving table
after validation succeeds.
"""

from __future__ import annotations

import logging
import re
import uuid
from collections.abc import Callable, Sequence
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from scripts.utils.sql_batch import execute_batch_sqls

REFRESH_STRATEGY_FULL_SNAPSHOT_SWAP = "full_snapshot_swap"

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RUN_TOKEN_PATTERN = re.compile(r"[^a-z0-9_]")
_MAX_TABLE_NAME_LENGTH = 64


class Connection(Protocol):
    """Subset of SQLAlchemy Connection used by refresh jobs."""

    def exec_driver_sql(self, statement: str) -> Any:
        """Execute one SQL statement."""


class Engine(Protocol):
    """Subset of SQLAlchemy Engine used by refresh jobs."""

    def begin(self) -> AbstractContextManager[Connection]:
        """Open a transaction context."""


class RefreshValidationError(RuntimeError):
    """Raised when a shadow table is unsafe to publish."""


@dataclass(frozen=True)
class ValidationCheck:
    """A query whose scalar result is the number of invalid rows."""

    name: str
    query_builder: Callable[[str], str]
    max_invalid_rows: int = 0


@dataclass(frozen=True)
class SwapRefreshStatements:
    """Rendered SQL statements for one full-snapshot refresh."""

    database: str
    target_table: str
    shadow_table: str
    biz_date: str
    prepare_sqls: tuple[str, ...]
    load_sql: str
    row_count_sql: str
    swap_sql: str
    cleanup_sql: str


@dataclass(frozen=True)
class SwapRefreshResult:
    """Published full-snapshot metadata."""

    database: str
    target_table: str
    shadow_table: str
    biz_date: str
    row_count: int


def normalize_biz_date(value: str) -> str:
    """Normalize YYYYMMDD or YYYY-MM-DD to YYYYMMDD."""
    for date_format in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format).strftime("%Y%m%d")
        except ValueError:
            continue
    raise ValueError(f"业务日期格式错误: {value!r}，应为 YYYYMMDD 或 YYYY-MM-DD")


def biz_date_exclusive_upper_bound_sql(biz_date: str) -> str:
    """Return the SQL expression for the day after biz_date."""
    normalized = normalize_biz_date(biz_date)
    return f"DATE_ADD(STR_TO_DATE('{normalized}', '%Y%m%d'), INTERVAL 1 DAY)"


def biz_month_sql(biz_date: str) -> str:
    """Return the SQL expression for biz_date's calendar month."""
    normalized = normalize_biz_date(biz_date)
    return f"DATE_FORMAT(STR_TO_DATE('{normalized}', '%Y%m%d'), '%Y-%m')"


def validate_identifier(identifier: str) -> str:
    """Validate one database, table, or column identifier."""
    if not _IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"非法 SQL 标识符: {identifier!r}")
    return identifier


def quote_identifier(identifier: str) -> str:
    """Quote one validated SQL identifier."""
    return f"`{validate_identifier(identifier)}`"


def qualified_table(database: str, table: str) -> str:
    """Quote a database-qualified table name."""
    return f"{quote_identifier(database)}.{quote_identifier(table)}"


def create_shadow_table_name(
    target_table: str,
    biz_date: str,
    *,
    run_token: str | None = None,
) -> str:
    """Create a unique StarRocks-compatible shadow table name."""
    validate_identifier(target_table)
    normalized_date = normalize_biz_date(biz_date)
    token = run_token or uuid.uuid4().hex[:8]
    token = _RUN_TOKEN_PATTERN.sub("", token.lower())[:12]
    if not token:
        raise ValueError("run_token 清洗后不能为空")

    suffix = f"_{normalized_date}_{token}"
    target_length = _MAX_TABLE_NAME_LENGTH - len("tmp_") - len(suffix)
    return f"tmp_{target_table[:target_length]}{suffix}"


def duplicate_key_check(*columns: str) -> ValidationCheck:
    """Build a duplicate-grain validation check."""
    if not columns:
        raise ValueError("重复键校验至少需要一个字段")
    quoted_columns = ", ".join(quote_identifier(column) for column in columns)

    def build_query(shadow_table: str) -> str:
        return f"""
        SELECT COUNT(*)
        FROM (
            SELECT {quoted_columns}
            FROM {shadow_table}
            GROUP BY {quoted_columns}
            HAVING COUNT(*) > 1
        ) duplicate_keys
        """.strip()

    return ValidationCheck(name=f"duplicate_key({', '.join(columns)})", query_builder=build_query)


def build_swap_refresh_statements(
    *,
    database: str,
    target_table: str,
    biz_date: str,
    build_insert_sql: Callable[[str, str], str],
    run_token: str | None = None,
) -> SwapRefreshStatements:
    """Render the standard shadow-table refresh statements."""
    validate_identifier(database)
    validate_identifier(target_table)
    normalized_date = normalize_biz_date(biz_date)
    shadow_table = create_shadow_table_name(target_table, normalized_date, run_token=run_token)
    qualified_target = qualified_table(database, target_table)
    qualified_shadow = qualified_table(database, shadow_table)
    load_sql = build_insert_sql(qualified_shadow, normalized_date).strip()
    if qualified_shadow not in load_sql:
        raise ValueError("装载 SQL 必须写入公共框架生成的临时表")

    return SwapRefreshStatements(
        database=database,
        target_table=target_table,
        shadow_table=shadow_table,
        biz_date=normalized_date,
        prepare_sqls=(
            f"DROP TABLE IF EXISTS {qualified_shadow}",
            f"CREATE TABLE {qualified_shadow} LIKE {qualified_target}",
        ),
        load_sql=load_sql,
        row_count_sql=f"SELECT COUNT(*) FROM {qualified_shadow}",
        swap_sql=f"ALTER TABLE {qualified_target} SWAP WITH {quote_identifier(shadow_table)}",
        cleanup_sql=f"DROP TABLE IF EXISTS {qualified_shadow}",
    )


def render_swap_refresh_sql(
    *,
    database: str,
    target_table: str,
    biz_date: str,
    build_insert_sql: Callable[[str, str], str],
    validation_checks: Sequence[ValidationCheck] = (),
    run_token: str = "dryrun",
) -> str:
    """Render a refresh plan for review without connecting to StarRocks."""
    statements = build_swap_refresh_statements(
        database=database,
        target_table=target_table,
        biz_date=biz_date,
        build_insert_sql=build_insert_sql,
        run_token=run_token,
    )
    qualified_shadow = qualified_table(database, statements.shadow_table)
    check_sqls = [check.query_builder(qualified_shadow) for check in validation_checks]
    sqls = [
        *statements.prepare_sqls,
        statements.load_sql,
        statements.row_count_sql,
        *check_sqls,
        statements.swap_sql,
        statements.cleanup_sql,
    ]
    return ";\n\n".join(sql.rstrip().rstrip(";") for sql in sqls) + ";\n"


def _scalar_int(result: Any) -> int:
    if hasattr(result, "scalar_one"):
        return int(result.scalar_one())
    row = result.fetchone()
    if row is None:
        raise RuntimeError("校验 SQL 未返回结果")
    return int(row[0])


def _execute(conn: Connection, logger: logging.Logger, sql: str) -> Any:
    logger.info("execute sql: %s", sql)
    return conn.exec_driver_sql(sql)


def _cleanup_shadow_table(engine: Engine, logger: logging.Logger, cleanup_sql: str) -> None:
    try:
        with engine.begin() as cleanup_conn:
            _execute(cleanup_conn, logger, cleanup_sql)
    except Exception:
        logger.exception("临时表清理失败，请人工检查: %s", cleanup_sql)


def run_swap_refresh(
    engine: Engine,
    logger: logging.Logger,
    *,
    database: str,
    target_table: str,
    biz_date: str,
    build_insert_sql: Callable[[str, str], str],
    validation_checks: Sequence[ValidationCheck] = (),
    min_rows: int = 1,
    run_token: str | None = None,
) -> SwapRefreshResult:
    """Load, validate, and atomically publish one full snapshot."""
    if min_rows < 0:
        raise ValueError("min_rows 不能小于 0")

    statements = build_swap_refresh_statements(
        database=database,
        target_table=target_table,
        biz_date=biz_date,
        build_insert_sql=build_insert_sql,
        run_token=run_token,
    )
    qualified_shadow = qualified_table(database, statements.shadow_table)
    logger.info(
        "开始全量快照刷新: target=%s.%s, shadow=%s, biz_date=%s",
        database,
        target_table,
        statements.shadow_table,
        statements.biz_date,
    )

    try:
        with engine.begin() as conn:
            for sql in statements.prepare_sqls:
                _execute(conn, logger, sql)

            execute_batch_sqls(conn, logger, statements.load_sql)
            row_count = _scalar_int(_execute(conn, logger, statements.row_count_sql))
            logger.info("临时表行数校验: shadow=%s, rows=%d", statements.shadow_table, row_count)
            if row_count < min_rows:
                raise RefreshValidationError(
                    f"临时表 {statements.shadow_table} 仅有 {row_count} 行，低于发布阈值 {min_rows}"
                )

            for check in validation_checks:
                invalid_rows = _scalar_int(
                    _execute(conn, logger, check.query_builder(qualified_shadow))
                )
                logger.info("临时表质量校验: check=%s, invalid_rows=%d", check.name, invalid_rows)
                if invalid_rows > check.max_invalid_rows:
                    raise RefreshValidationError(
                        f"临时表 {statements.shadow_table} 未通过 {check.name} 校验："
                        f"{invalid_rows} > {check.max_invalid_rows}"
                    )

            _execute(conn, logger, statements.swap_sql)
            _execute(conn, logger, statements.cleanup_sql)
    except Exception:
        logger.exception(
            "全量快照刷新失败，正式表保持最近一次成功快照: target=%s.%s",
            database,
            target_table,
        )
        _cleanup_shadow_table(engine, logger, statements.cleanup_sql)
        raise

    logger.info(
        "全量快照刷新成功: target=%s.%s, rows=%d, biz_date=%s",
        database,
        target_table,
        row_count,
        statements.biz_date,
    )
    return SwapRefreshResult(
        database=database,
        target_table=target_table,
        shadow_table=statements.shadow_table,
        biz_date=statements.biz_date,
        row_count=row_count,
    )
