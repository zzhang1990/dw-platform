from __future__ import annotations

import unittest
from pathlib import Path

from scripts.etl.ads import proc_ads_demo_project_monthly_finance
from scripts.etl.dim import proc_dim_demo_project
from scripts.etl.dwd import proc_dwd_demo_order_receivable
from scripts.etl.dws import proc_dws_demo_project_monthly_receivable
from scripts.utils.etl_refresh import REFRESH_STRATEGY_FULL_SNAPSHOT_SWAP

SAMPLE_JOBS = (
    proc_dim_demo_project,
    proc_dwd_demo_order_receivable,
    proc_dws_demo_project_monthly_receivable,
    proc_ads_demo_project_monthly_finance,
)


class DemoFinanceChainSqlTest(unittest.TestCase):
    def test_each_job_renders_shadow_table_swap_refresh(self) -> None:
        for job in SAMPLE_JOBS:
            with self.subTest(job=job.__name__):
                sql = job.build_refresh_sql("2026-05-31", run_token="sample")

                self.assertEqual(job.REFRESH_STRATEGY, REFRESH_STRATEGY_FULL_SNAPSHOT_SWAP)
                self.assertTrue(job.DATABASE.startswith("demo_"))
                self.assertIn("_demo_", job.TARGET_TABLE)
                self.assertIn("CREATE TABLE", sql)
                self.assertIn(" LIKE ", sql)
                self.assertIn("STR_TO_DATE('20260531'", sql)
                self.assertIn("SELECT COUNT(*)", sql)
                self.assertIn("SWAP WITH", sql)
                self.assertIn("DROP TABLE IF EXISTS", sql)
                self.assertNotIn("DELETE FROM", sql)

    def test_historical_backfill_date_changes_each_job_sql(self) -> None:
        for job in SAMPLE_JOBS:
            with self.subTest(job=job.__name__):
                current_sql = job.build_refresh_sql("2026-05-31", run_token="sample")
                backfill_sql = job.build_refresh_sql("2026-05-01", run_token="sample")

                self.assertIn("STR_TO_DATE('20260531'", current_sql)
                self.assertIn("STR_TO_DATE('20260501'", backfill_sql)
                self.assertNotEqual(current_sql, backfill_sql)

    def test_chain_uses_only_sanitized_demo_tables(self) -> None:
        dim_sql = proc_dim_demo_project.build_insert_sql("shadow", "20260531")
        dwd_sql = proc_dwd_demo_order_receivable.build_insert_sql("shadow", "20260531")
        dws_sql = proc_dws_demo_project_monthly_receivable.build_insert_sql("shadow", "20260531")
        ads_sql = proc_ads_demo_project_monthly_finance.build_insert_sql("shadow", "20260531")

        self.assertIn("demo_ods.ods_demo_project", dim_sql)
        self.assertIn("demo_ods.ods_demo_order_receivable", dwd_sql)
        self.assertIn("demo_dim.dim_demo_project", dwd_sql)
        self.assertIn("demo_dwd.dwd_demo_order_receivable", dws_sql)
        self.assertIn("demo_dws.dws_demo_project_monthly_receivable", ads_sql)

        combined_sql = "\n".join((dim_sql, dwd_sql, dws_sql, ads_sql))
        self.assertNotIn("password", combined_sql.lower())
        self.assertNotIn("apikey", combined_sql.lower())
        self.assertNotIn("api_key", combined_sql.lower())

    def test_public_ddl_contains_the_complete_demo_chain(self) -> None:
        ddl_path = Path("examples/starrocks/demo_finance_chain.sql")
        ddl = ddl_path.read_text(encoding="utf-8")

        for table in (
            "demo_ods.ods_demo_project",
            "demo_ods.ods_demo_order_receivable",
            "demo_dim.dim_demo_project",
            "demo_dwd.dwd_demo_order_receivable",
            "demo_dws.dws_demo_project_monthly_receivable",
            "demo_ads.ads_demo_project_monthly_finance",
        ):
            with self.subTest(table=table):
                self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", ddl)

    def test_public_sql_assets_cover_seed_and_validation_queries(self) -> None:
        seed_sql = Path("examples/starrocks/demo_finance_seed.sql").read_text(encoding="utf-8")
        validation_sql = Path("examples/starrocks/demo_finance_validation.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("INSERT INTO demo_ods.ods_demo_project", seed_sql)
        self.assertIn("INSERT INTO demo_ods.ods_demo_order_receivable", seed_sql)
        self.assertIn("FROM demo_ads.ads_demo_project_monthly_finance", validation_sql)


if __name__ == "__main__":
    unittest.main()
