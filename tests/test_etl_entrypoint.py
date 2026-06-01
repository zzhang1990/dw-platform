from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO

from scripts.etl.etl import run_etl, select_tasks


class EtlEntrypointTest(unittest.TestCase):
    def test_selects_demo_finance_chain_in_dependency_order(self) -> None:
        self.assertEqual(
            [task.name for task in select_tasks("all")],
            [
                "dim_demo_project",
                "dwd_demo_order_receivable",
                "dws_demo_project_monthly_receivable",
                "ads_demo_project_monthly_finance",
            ],
        )

    def test_dry_run_renders_the_whole_chain_without_database_connection(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            run_etl("2026-05-31", "all", dry_run=True)

        output = stdout.getvalue()
        self.assertEqual(output.count("SWAP WITH"), 4)
        self.assertIn("STR_TO_DATE('20260531'", output)
        self.assertLess(output.index("dim_demo_project"), output.index("dwd_demo_order_receivable"))
        self.assertLess(
            output.index("dwd_demo_order_receivable"),
            output.index("dws_demo_project_monthly_receivable"),
        )
        self.assertLess(
            output.index("dws_demo_project_monthly_receivable"),
            output.index("ads_demo_project_monthly_finance"),
        )


if __name__ == "__main__":
    unittest.main()
