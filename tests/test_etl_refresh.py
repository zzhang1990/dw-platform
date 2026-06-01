from __future__ import annotations

import logging
import unittest
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch

from scripts.utils.etl_refresh import (
    RefreshValidationError,
    biz_date_exclusive_upper_bound_sql,
    duplicate_key_check,
    normalize_biz_date,
    run_swap_refresh,
)


class FakeResult:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def scalar_one(self) -> int:
        return self.value

    @property
    def rowcount(self) -> int:
        return self.value


class RecordingEngine:
    def __init__(
        self,
        *,
        row_count: int = 3,
        invalid_rows: int = 0,
        fail_on: str | None = None,
    ) -> None:
        self.row_count = row_count
        self.invalid_rows = invalid_rows
        self.fail_on = fail_on
        self.statements: list[str] = []

    @contextmanager
    def begin(self) -> Any:
        yield self

    def exec_driver_sql(self, statement: str) -> FakeResult:
        self.statements.append(statement)
        if self.fail_on and self.fail_on in statement:
            raise RuntimeError(f"forced failure: {self.fail_on}")
        if "duplicate_keys" in statement:
            return FakeResult(self.invalid_rows)
        if statement.startswith("SELECT COUNT(*)"):
            return FakeResult(self.row_count)
        return FakeResult(1)


def build_insert_sql(shadow_table: str, biz_date: str) -> str:
    upper_bound = biz_date_exclusive_upper_bound_sql(biz_date)
    return f"""
    INSERT INTO {shadow_table}
    SELECT *
    FROM demo_ods.ods_demo_order_receivable
    WHERE created_at < {upper_bound};
    """.strip()


class RunSwapRefreshTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger(self.id())

    def test_successfully_publishes_valid_shadow_table(self) -> None:
        engine = RecordingEngine(row_count=3)

        result = run_swap_refresh(
            engine,
            self.logger,
            database="demo_dwd",
            target_table="dwd_demo_order_receivable",
            biz_date="2026-05-31",
            build_insert_sql=build_insert_sql,
            validation_checks=(duplicate_key_check("receivable_id"),),
            run_token="run1",
        )

        self.assertEqual(result.biz_date, "20260531")
        self.assertEqual(result.row_count, 3)
        self.assertTrue(any("CREATE TABLE" in sql and "LIKE" in sql for sql in engine.statements))
        self.assertTrue(any("STR_TO_DATE('20260531'" in sql for sql in engine.statements))
        self.assertTrue(any("duplicate_keys" in sql for sql in engine.statements))
        self.assertTrue(any("SWAP WITH" in sql for sql in engine.statements))
        self.assertTrue(engine.statements[-1].startswith("DROP TABLE IF EXISTS"))

    def test_load_failure_cleans_shadow_table_without_swap(self) -> None:
        engine = RecordingEngine(fail_on="FROM demo_ods.ods_demo_order_receivable")

        with (
            patch("scripts.utils.sql_batch.time.sleep"),
            self.assertRaisesRegex(Exception, "forced failure"),
        ):
            run_swap_refresh(
                engine,
                self.logger,
                database="demo_dwd",
                target_table="dwd_demo_order_receivable",
                biz_date="20260531",
                build_insert_sql=build_insert_sql,
                run_token="run2",
            )

        self.assertFalse(any("SWAP WITH" in sql for sql in engine.statements))
        self.assertTrue(engine.statements[-1].startswith("DROP TABLE IF EXISTS"))

    def test_empty_shadow_table_is_not_published(self) -> None:
        engine = RecordingEngine(row_count=0)

        with self.assertRaises(RefreshValidationError):
            run_swap_refresh(
                engine,
                self.logger,
                database="demo_dwd",
                target_table="dwd_demo_order_receivable",
                biz_date="20260531",
                build_insert_sql=build_insert_sql,
                run_token="run3",
            )

        self.assertFalse(any("SWAP WITH" in sql for sql in engine.statements))
        self.assertTrue(engine.statements[-1].startswith("DROP TABLE IF EXISTS"))

    def test_duplicate_grain_is_not_published(self) -> None:
        engine = RecordingEngine(row_count=3, invalid_rows=1)

        with self.assertRaises(RefreshValidationError):
            run_swap_refresh(
                engine,
                self.logger,
                database="demo_dwd",
                target_table="dwd_demo_order_receivable",
                biz_date="20260531",
                build_insert_sql=build_insert_sql,
                validation_checks=(duplicate_key_check("receivable_id"),),
                run_token="run4",
            )

        self.assertFalse(any("SWAP WITH" in sql for sql in engine.statements))

    def test_same_business_date_can_be_published_repeatedly(self) -> None:
        engine = RecordingEngine(row_count=3)

        first = run_swap_refresh(
            engine,
            self.logger,
            database="demo_dwd",
            target_table="dwd_demo_order_receivable",
            biz_date="20260531",
            build_insert_sql=build_insert_sql,
            run_token="repeat1",
        )
        second = run_swap_refresh(
            engine,
            self.logger,
            database="demo_dwd",
            target_table="dwd_demo_order_receivable",
            biz_date="20260531",
            build_insert_sql=build_insert_sql,
            run_token="repeat2",
        )

        self.assertNotEqual(first.shadow_table, second.shadow_table)
        self.assertEqual(sum("SWAP WITH" in sql for sql in engine.statements), 2)


class BizDateTest(unittest.TestCase):
    def test_normalizes_supported_formats(self) -> None:
        self.assertEqual(normalize_biz_date("20260531"), "20260531")
        self.assertEqual(normalize_biz_date("2026-05-31"), "20260531")

    def test_rejects_invalid_date(self) -> None:
        with self.assertRaisesRegex(ValueError, "业务日期格式错误"):
            normalize_biz_date("20260231")


if __name__ == "__main__":
    unittest.main()
