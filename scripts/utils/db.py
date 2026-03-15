"""数据库连接工具"""
from typing import Optional

import pymysql
from pymysql.cursors import DictCursor

from config.settings import (
    STARROCKS_HOST,
    STARROCKS_PORT,
    STARROCKS_USER,
    STARROCKS_PASSWORD,
    STARROCKS_DATABASE,
)


def get_connection(database: Optional[str] = None) -> pymysql.Connection:
    """
    获取 StarRocks 数据库连接

    Args:
        database: 数据库名，默认使用配置中的数据库

    Returns:
        pymysql.Connection: 数据库连接对象
    """
    return pymysql.connect(
        host=STARROCKS_HOST,
        port=STARROCKS_PORT,
        user=STARROCKS_USER,
        password=STARROCKS_PASSWORD,
        database=database or STARROCKS_DATABASE,
        charset="utf8mb4",
        cursorclass=DictCursor,
    )


def execute_sql(sql: str, params: Optional[dict] = None) -> int:
    """
    执行 SQL 语句

    Args:
        sql: SQL 语句
        params: 参数

    Returns:
        影响行数
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount


def query_sql(sql: str, params: Optional[dict] = None) -> list[dict]:
    """
    查询 SQL

    Args:
        sql: SQL 语句
        params: 参数

    Returns:
        查询结果列表
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()