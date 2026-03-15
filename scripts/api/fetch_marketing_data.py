"""API 数据采集示例"""
import argparse
import logging
from datetime import datetime, timedelta

import requests

from config.settings import API_TIMEOUT, API_RETRY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_marketing_data(dt: str) -> list[dict]:
    """
    获取营销数据

    Args:
        dt: 日期参数 YYYY-MM-DD

    Returns:
        数据列表
    """
    # TODO: 替换为实际的 API 地址和参数
    url = "https://api.example.com/marketing/data"
    params = {"date": dt}

    for attempt in range(API_RETRY):
        try:
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.RequestException as e:
            logger.warning(f"API 请求失败 (尝试 {attempt + 1}/{API_RETRY}): {e}")
            if attempt == API_RETRY - 1:
                raise

    return []


def main():
    parser = argparse.ArgumentParser(description="获取营销数据")
    parser.add_argument(
        "--dt",
        help="日期参数 (YYYY-MM-DD), 默认昨天",
    )

    args = parser.parse_args()

    if args.dt:
        dt = args.dt
    else:
        dt = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"开始获取营销数据, 日期: {dt}")

    data = fetch_marketing_data(dt)

    logger.info(f"获取完成, 数据条数: {len(data)}")

    # TODO: 写入数据库


if __name__ == "__main__":
    main()