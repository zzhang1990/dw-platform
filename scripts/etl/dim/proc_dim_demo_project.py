"""Sanitized demo project dimension refresh."""

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

DATABASE = "demo_dim"
TARGET_TABLE = "dim_demo_project"
REFRESH_STRATEGY = REFRESH_STRATEGY_FULL_SNAPSHOT_SWAP
VALIDATION_CHECKS = (duplicate_key_check("project_id"),)


def build_insert_sql(target_table: str, biz_date: str) -> str:
    """Build the DIM full-snapshot load SQL."""
    upper_bound = biz_date_exclusive_upper_bound_sql(biz_date)
    return f"""
    INSERT INTO {target_table}
    SELECT
        project_id,
        project_code,
        project_name,
        customer_id,
        project_status,
        created_at,
        updated_at
    FROM demo_ods.ods_demo_project
    WHERE created_at IS NULL
       OR created_at < {upper_bound};
    """.strip()


def build_refresh_sql(biz_date: str, *, run_token: str = "dryrun") -> str:
    """Render the DIM shadow-table refresh plan."""
    return render_swap_refresh_sql(
        database=DATABASE,
        target_table=TARGET_TABLE,
        biz_date=biz_date,
        build_insert_sql=build_insert_sql,
        validation_checks=VALIDATION_CHECKS,
        run_token=run_token,
    )


def run(biz_date: str) -> None:
    """Publish the DIM full snapshot."""
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
    parser = argparse.ArgumentParser(description="Refresh the sanitized demo project dimension")
    parser.add_argument("--biz-date", required=True, help="Business date: YYYYMMDD or YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="Render SQL without connecting")
    args = parser.parse_args()
    if args.dry_run:
        print(build_refresh_sql(args.biz_date))
        return
    run(args.biz_date)


if __name__ == "__main__":
    main()
