"""营销主题 ETL 脚本"""
import argparse
import logging
from datetime import datetime, timedelta

from scripts.utils.db import execute_sql

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_dwd_user_behavior(dt: str) -> int:
    """
    DWD 层：用户行为明细清洗

    Args:
        dt: 日期参数 YYYY-MM-DD

    Returns:
        影响行数
    """
    sql = f"""
        INSERT INTO dwd_user_behavior
        SELECT
            user_id,
            session_id,
            action_type,
            action_time,
            page_url,
            referrer_url,
            device_type,
            platform,
            created_at
        FROM ods_pg_user_log
        WHERE dt = '{dt}'
          AND user_id IS NOT NULL
          AND action_time IS NOT NULL
    """
    logger.info(f"执行 DWD 用户行为清洗, 日期: {dt}")
    return execute_sql(sql)


def run_ads_marketing_dashboard(dt: str) -> int:
    """
    ADS 层：营销仪表盘

    Args:
        dt: 日期参数 YYYY-MM-DD

    Returns:
        影响行数
    """
    sql = f"""
        INSERT INTO ads_marketing_dashboard
        SELECT
            '{dt}' AS report_date,
            action_type,
            device_type,
            platform,
            COUNT(DISTINCT user_id) AS unique_users,
            COUNT(*) AS action_count,
            COUNT(DISTINCT session_id) AS session_count
        FROM dwd_user_behavior
        WHERE dt = '{dt}'
        GROUP BY action_type, device_type, platform
    """
    logger.info(f"执行 ADS 营销仪表盘, 日期: {dt}")
    return execute_sql(sql)


def run_marketing_etl(dt: str):
    """执行营销主题完整 ETL"""
    logger.info(f"开始营销主题 ETL, 日期: {dt}")

    # DWD 层
    dwd_rows = run_dwd_user_behavior(dt)
    logger.info(f"DWD 层完成, 影响行数: {dwd_rows}")

    # ADS 层
    ads_rows = run_ads_marketing_dashboard(dt)
    logger.info(f"ADS 层完成, 影响行数: {ads_rows}")

    logger.info("营销主题 ETL 完成")


def main():
    parser = argparse.ArgumentParser(description="营销主题 ETL")
    parser.add_argument(
        "--dt",
        help="日期参数 (YYYY-MM-DD), 默认昨天",
    )

    args = parser.parse_args()

    if args.dt:
        dt = args.dt
    else:
        dt = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    run_marketing_etl(dt)


if __name__ == "__main__":
    main()