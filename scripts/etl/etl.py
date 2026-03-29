"""ETL 脚本入口"""
import argparse
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_etl(dt: str, layer: str = "all") -> None:
    """
    ETL 主入口

    Args:
        dt: 日期参数 YYYY-MM-DD
        layer: 执行层级 dim/dwd/dws/ads/all
    """
    logger.info(f"开始 ETL, 日期: {dt}, 层级: {layer}")
    if layer in ("all", "dwd", "dim", "dws", "ads"):
        # 各层任务在此接入 run_dwd(dt) 等
        logger.info(f"层级 {layer} 暂无已注册任务，跳过")
    else:
        raise ValueError(f"不支持的 layer: {layer}")
    logger.info("ETL 完成")


def main() -> None:
    parser = argparse.ArgumentParser(description="DW Platform ETL")
    parser.add_argument(
        "--dt",
        type=str,
        default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        help="业务日期 YYYY-MM-DD，默认昨天",
    )
    parser.add_argument(
        "--layer",
        type=str,
        default="all",
        choices=("all", "dim", "dwd", "dws", "ads"),
        help="执行层级",
    )
    args = parser.parse_args()
    run_etl(args.dt, args.layer)


if __name__ == "__main__":
    main()
