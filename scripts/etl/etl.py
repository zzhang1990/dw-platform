"""ETL entry point for registered demo jobs."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.etl.ads import proc_ads_demo_project_monthly_finance  # noqa: E402
from scripts.etl.dim import proc_dim_demo_project  # noqa: E402
from scripts.etl.dwd import proc_dwd_demo_order_receivable  # noqa: E402
from scripts.etl.dws import proc_dws_demo_project_monthly_receivable  # noqa: E402
from scripts.utils.etl_refresh import normalize_biz_date  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EtlTask:
    """One independently schedulable ETL task."""

    name: str
    layer: str
    run: Callable[[str], None]
    build_refresh_sql: Callable[..., str]


DEMO_FINANCE_CHAIN_TASKS = (
    EtlTask(
        name="dim_demo_project",
        layer="dim",
        run=proc_dim_demo_project.run,
        build_refresh_sql=proc_dim_demo_project.build_refresh_sql,
    ),
    EtlTask(
        name="dwd_demo_order_receivable",
        layer="dwd",
        run=proc_dwd_demo_order_receivable.run,
        build_refresh_sql=proc_dwd_demo_order_receivable.build_refresh_sql,
    ),
    EtlTask(
        name="dws_demo_project_monthly_receivable",
        layer="dws",
        run=proc_dws_demo_project_monthly_receivable.run,
        build_refresh_sql=proc_dws_demo_project_monthly_receivable.build_refresh_sql,
    ),
    EtlTask(
        name="ads_demo_project_monthly_finance",
        layer="ads",
        run=proc_ads_demo_project_monthly_finance.run,
        build_refresh_sql=proc_ads_demo_project_monthly_finance.build_refresh_sql,
    ),
)


def select_tasks(layer: str) -> tuple[EtlTask, ...]:
    """Select registered demo tasks in dependency order."""
    if layer == "all":
        return DEMO_FINANCE_CHAIN_TASKS
    if layer not in {"dim", "dwd", "dws", "ads"}:
        raise ValueError(f"不支持的 layer: {layer}")
    return tuple(task for task in DEMO_FINANCE_CHAIN_TASKS if task.layer == layer)


def run_etl(dt: str, layer: str = "all", *, dry_run: bool = False) -> None:
    """Run or render the registered demo finance chain."""
    biz_date = normalize_biz_date(dt)
    tasks = select_tasks(layer)
    logger.info("开始 ETL, 日期: %s, 层级: %s, dry_run=%s", biz_date, layer, dry_run)

    for task in tasks:
        logger.info("开始任务: %s", task.name)
        if dry_run:
            print(f"-- ===== {task.layer.upper()}: {task.name} =====")
            print(task.build_refresh_sql(biz_date, run_token="dryrun"))
        else:
            task.run(biz_date)
        logger.info("完成任务: %s", task.name)

    logger.info("ETL 完成")


def main() -> None:
    parser = argparse.ArgumentParser(description="DW Platform demo finance ETL")
    parser.add_argument(
        "--dt",
        default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        help="Business date: YYYY-MM-DD or YYYYMMDD. Defaults to yesterday.",
    )
    parser.add_argument(
        "--layer",
        default="all",
        choices=("all", "dim", "dwd", "dws", "ads"),
        help="Layer to execute.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Render SQL without connecting.")
    args = parser.parse_args()
    run_etl(args.dt, args.layer, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
