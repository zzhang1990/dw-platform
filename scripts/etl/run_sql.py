"""SQL 执行脚本"""
import argparse
import logging
from pathlib import Path

from config.settings import BASE_DIR
from scripts.utils.db import execute_sql

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_sql_file(sql_path: str, dt: str) -> int:
    """
    执行 SQL 文件

    Args:
        sql_path: SQL 文件路径（相对于 sql 目录）
        dt: 日期参数

    Returns:
        影响行数
    """
    # 读取 SQL 文件
    full_path = BASE_DIR / "sql" / sql_path
    if not full_path.exists():
        raise FileNotFoundError(f"SQL 文件不存在: {full_path}")

    sql = full_path.read_text(encoding="utf-8")

    # 替换日期参数
    sql = sql.replace("{dt}", dt)

    logger.info(f"执行 SQL: {sql_path}, 日期: {dt}")
    result = execute_sql(sql)
    logger.info(f"执行完成, 影响行数: {result}")

    return result


def main():
    parser = argparse.ArgumentParser(description="执行 SQL 脚本")
    parser.add_argument("--sql", required=True, help="SQL 文件路径")
    parser.add_argument("--dt", required=True, help="日期参数 (YYYY-MM-DD)")

    args = parser.parse_args()

    run_sql_file(args.sql, args.dt)


if __name__ == "__main__":
    main()