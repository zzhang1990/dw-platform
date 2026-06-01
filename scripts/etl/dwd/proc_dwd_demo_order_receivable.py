"""Sanitized demo order-receivable detail refresh."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utils.etl_refresh import (  # noqa: E402
    REFRESH_STRATEGY_FULL_SNAPSHOT_SWAP,
    biz_date_exclusive_upper_bound_sql,
    duplicate_key_check,
    render_swap_refresh_sql,
    run_swap_refresh,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATABASE = "demo_dwd"
TARGET_TABLE = "dwd_demo_order_receivable"
REFRESH_STRATEGY = REFRESH_STRATEGY_FULL_SNAPSHOT_SWAP
VALIDATION_CHECKS = (duplicate_key_check("receivable_id"),)


def build_insert_sql(target_table: str, biz_date: str) -> str:
    """Build the DWD full-snapshot load SQL."""
    upper_bound = biz_date_exclusive_upper_bound_sql(biz_date)
    return f"""
    INSERT INTO {target_table}
    SELECT
        rec.receivable_id,
        rec.tenant_id,
        rec.order_no,
        rec.customer_id,
        rec.project_id,
        COALESCE(project.project_code, 'UNKNOWN') AS project_code,
        COALESCE(project.project_name, 'Unknown project') AS project_name,
        COALESCE(rec.receivable_amount, 0) AS receivable_amount,
        COALESCE(rec.discount_amount, 0) AS discount_amount,
        COALESCE(rec.receivable_amount, 0) - COALESCE(rec.discount_amount, 0)
            AS net_receivable_amount,
        rec.receivable_status,
        rec.created_at,
        rec.updated_at
    FROM demo_ods.ods_demo_order_receivable rec
    LEFT JOIN demo_dim.dim_demo_project project
        ON project.project_id = rec.project_id
    WHERE rec.created_at IS NULL
       OR rec.created_at < {upper_bound};
    """.strip()


def build_refresh_sql(biz_date: str, *, run_token: str = "dryrun") -> str:
    """Render the DWD shadow-table refresh plan."""
    return render_swap_refresh_sql(
        database=DATABASE,
        target_table=TARGET_TABLE,
        biz_date=biz_date,
        build_insert_sql=build_insert_sql,
        validation_checks=VALIDATION_CHECKS,
        run_token=run_token,
    )


def run(biz_date: str) -> None:
    """Publish the DWD full snapshot."""
    from scripts.utils.db import get_engine

    run_swap_refresh(
        get_engine(),
        logger,
        database=DATABASE,
        target_table=TARGET_TABLE,
        biz_date=biz_date,
        build_insert_sql=build_insert_sql,
        validation_checks=VALIDATION_CHECKS,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh the sanitized demo receivable detail")
    parser.add_argument("--biz-date", required=True, help="Business date: YYYYMMDD or YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="Render SQL without connecting")
    args = parser.parse_args()
    if args.dry_run:
        print(build_refresh_sql(args.biz_date))
        return
    run(args.biz_date)


if __name__ == "__main__":
    main()
