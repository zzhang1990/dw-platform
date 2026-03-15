"""数据库连接工具"""
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.settings import (
    STARROCKS_HOST,
    STARROCKS_PORT,
    STARROCKS_USER,
    STARROCKS_PASSWORD,
    STARROCKS_DATABASE,
)

# 全局引擎缓存
_engine: Optional[Engine] = None


def get_engine(database: Optional[str] = None) -> Engine:
    """
    获取 StarRocks 数据库引擎

    Args:
        database: 数据库名，默认使用配置中的数据库

    Returns:
        SQLAlchemy Engine
    """
    global _engine

    db = database or STARROCKS_DATABASE

    # 连接字符串格式: starrocks://user:password@host:port/database
    url = f"starrocks://{STARROCKS_USER}:{STARROCKS_PASSWORD}@{STARROCKS_HOST}:{STARROCKS_PORT}/{db}"

    if _engine is None:
        _engine = create_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            echo=False,
        )

    return _engine


def execute_sql(sql: str) -> int:
    """
    执行 SQL 语句 (INSERT/UPDATE/DELETE)

    Args:
        sql: SQL 语句

    Returns:
        影响行数
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        return result.rowcount


def query_sql(sql: str) -> list[dict]:
    """
    查询 SQL

    Args:
        sql: SQL 语句

    Returns:
        查询结果列表
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]


def query_one(sql: str) -> Optional[dict]:
    """
    查询单条记录

    Args:
        sql: SQL 语句

    Returns:
        单条记录或 None
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        row = result.fetchone()
        if row is None:
            return None
        columns = result.keys()
        return dict(zip(columns, row))