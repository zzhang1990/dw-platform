"""财务主题 ETL 脚本"""
import argparse
import logging
from datetime import datetime, timedelta

from scripts.utils.db import execute_sql

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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


def run_finance_etl(dt: str):
    """执行财务主题完整 ETL"""
    logger.info(f"开始财务主题 ETL, 日期: {dt}")

    # DWD 层
    dwd_rows = run_dwd_finance_detail(dt)
    logger.info(f"DWD 层完成, 影响行数: {dwd_rows}")

    # ADS 层
    ads_rows = run_ads_finance_report(dt)
    logger.info(f"ADS 层完成, 影响行数: {ads_rows}")

    logger.info("财务主题 ETL 完成")


def main():
    parser = argparse.ArgumentParser(description="财务主题 ETL")
    parser.add_argument(
        "--dt",
        help="日期参数 (YYYY-MM-DD), 默认昨天",
    )

    args = parser.parse_args()

    if args.dt:
        dt = args.dt
    else:
        dt = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    run_finance_etl(dt)


if __name__ == "__main__":
    main()