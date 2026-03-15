"""ETL 脚本 - 财务营销主题"""
import argparse
import logging
from datetime import datetime, timedelta

from scripts.utils.db import execute_sql

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ==================== DWD 层 ====================


def run_dwd_finance_detail(dt: str) -> int:
    """
    DWD 层：财务账单明细清洗

    Args:
        dt: 日期参数 YYYY-MM-DD

    Returns:
        影响行数
    """
    sql = f"""
        INSERT INTO dwd_finance_detail
        SELECT
            bill_id,
            account_id,
            account_name,
            amount,
            currency,
            transaction_type,
            transaction_time,
            created_at,
            updated_at
        FROM ods_pg_finance_bill
        WHERE dt = '{dt}'
          AND amount IS NOT NULL
          AND transaction_time IS NOT NULL
    """
    logger.info(f"执行 DWD 财务明细清洗, 日期: {dt}")
    return execute_sql(sql)


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


# ==================== ADS 层 ====================


def run_ads_finance_report(dt: str) -> int:
    """
    ADS 层：财务报表

    Args:
        dt: 日期参数 YYYY-MM-DD

    Returns:
        影响行数
    """
    sql = f"""
        INSERT INTO ads_finance_report
        SELECT
            '{dt}' AS report_date,
            transaction_type,
            currency,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_amount,
            AVG(amount) AS avg_amount
        FROM dwd_finance_detail
        WHERE dt = '{dt}'
        GROUP BY transaction_type, currency
    """
    logger.info(f"执行 ADS 财务报表, 日期: {dt}")
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


# ==================== 主流程 ====================


def run_dwd(dt: str):
    """执行 DWD 层所有任务"""
    logger.info(f"开始 DWD 层处理, 日期: {dt}")

    rows = run_dwd_finance_detail(dt)
    logger.info(f"财务明细完成, 影响行数: {rows}")

    rows = run_dwd_user_behavior(dt)
    logger.info(f"用户行为完成, 影响行数: {rows}")


def run_ads(dt: str):
    """执行 ADS 层所有任务"""
    logger.info(f"开始 ADS 层处理, 日期: {dt}")

    rows = run_ads_finance_report(dt)
    logger.info(f"财务报表完成, 影响行数: {rows}")

    rows = run_ads_marketing_dashboard(dt)
    logger.info(f"营销仪表盘完成, 影响行数: {rows}")


def run_etl(dt: str, layer: str = "all"):
    """
    执行 ETL 任务

    Args:
        dt: 日期参数
        layer: 执行层级 (dwd/ads/all)
    """
    logger.info(f"开始 ETL 任务, 日期: {dt}, 层级: {layer}")

    if layer in ("all", "dwd"):
        run_dwd(dt)

    if layer in ("all", "ads"):
        run_ads(dt)

    logger.info("ETL 任务完成")


def main():
    parser = argparse.ArgumentParser(description="财务营销主题 ETL")
    parser.add_argument(
        "--dt",
        help="日期参数 (YYYY-MM-DD), 默认昨天",
    )
    parser.add_argument(
        "--layer",
        choices=["dwd", "ads", "all"],
        default="all",
        help="执行层级: dwd/ads/all",
    )

    args = parser.parse_args()

    if args.dt:
        dt = args.dt
    else:
        dt = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    run_etl(dt, args.layer)


if __name__ == "__main__":
    main()