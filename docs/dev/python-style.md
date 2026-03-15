# Python 编码规范

## 基本规范

### 代码格式

- 使用 `black` 格式化代码
- 遵循 PEP 8 规范
- 行长度不超过 100 字符
- 使用 UTF-8 编码

### 导入规范

```python
# 标准库
import os
import sys
from datetime import datetime

# 第三方库
import pandas as pd
from starrocks import connect

# 本地模块
from scripts.utils.db import execute_sql, query_sql
```

---

## 类型注解

**必须使用类型注解：**

```python
from typing import List, Dict, Optional

def run_dwd_order_detail(dt: str) -> int:
    """处理订单明细"""
    ...

def get_user_info(user_id: int) -> Dict[str, any]:
    """获取用户信息"""
    ...

def query_orders(dt: str, limit: Optional[int] = None) -> List[Dict]:
    """查询订单"""
    ...
```

---

## 函数规范

### 函数定义

```python
def run_dwd_finance_detail(dt: str, source: str = "ods") -> int:
    """
    DWD 层：财务明细清洗

    Args:
        dt: 日期参数 YYYY-MM-DD
        source: 数据来源，默认 ods

    Returns:
        影响行数

    Raises:
        ValueError: 日期格式错误
    """
    # 参数校验
    if not validate_date(dt):
        raise ValueError(f"Invalid date format: {dt}")

    # 业务逻辑
    sql = f"SELECT * FROM {source}_finance WHERE dt = '{dt}'"
    rows = execute_sql(sql)

    return rows
```

### 函数命名

```python
# 按层级组织
def run_dim_user(dt: str) -> int: ...
def run_dwd_order_detail(dt: str) -> int: ...
def run_dws_user_day_stat(dt: str) -> int: ...
def run_ads_finance_report(dt: str) -> int: ...

# 层级入口函数
def run_dim(dt: str) -> None: ...
def run_dwd(dt: str) -> None: ...
def run_dws(dt: str) -> None: ...
def run_ads(dt: str) -> None: ...

# ETL 主入口
def run_etl(dt: str, layer: str = "all") -> None: ...
```

---

## SQL 规范

### SQL 格式

```python
# 使用 f-string 传参
sql = f"""
    SELECT
        user_id,
        user_name,
        COUNT(*) AS order_cnt,
        SUM(amount) AS total_amt
    FROM dwd_order_detail
    WHERE dt = '{dt}'
    GROUP BY user_id, user_name
"""
```

### SQL 注入防护

```python
# 不要直接拼接用户输入
# 错误示例
user_input = request.args.get('name')
sql = f"SELECT * FROM table WHERE name = '{user_input}'"  # 危险！

# 正确示例：使用参数化查询或白名单验证
ALLOWED_SOURCES = {'ods', 'dwd', 'dws'}
source = request.args.get('source')
if source not in ALLOWED_SOURCES:
    raise ValueError("Invalid source")
```

---

## 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 日志级别
logger.debug("调试信息")
logger.info("正常信息")
logger.warning("警告信息")
logger.error("错误信息")

# 任务日志
logger.info(f"[START] DWD 订单明细处理, 日期: {dt}")
logger.info(f"[SUCCESS] 处理完成, 影响行数: {rows}")
logger.error(f"[FAILED] 处理失败, 原因: {e}")
```

---

## 异常处理

```python
# 明确的异常捕获
try:
    result = execute_sql(sql)
except ConnectionError as e:
    logger.error(f"数据库连接失败: {e}")
    raise
except Exception as e:
    logger.error(f"执行失败: {e}")
    raise

# 上下文管理器
with get_connection() as conn:
    result = conn.execute(sql)
```

---

## 文件结构

### ETL 脚本模板

```python
"""ETL 脚本 - {主题名称}

处理 {业务描述}
"""
import logging
from typing import Optional

from scripts.utils.db import execute_sql, query_sql

logger = logging.getLogger(__name__)


def run_dwd_xxx(dt: str, source: str = "ods") -> int:
    """DWD 层：xxx 明细清洗"""
    logger.info(f"[START] DWD xxx, 日期: {dt}")

    sql = f"""
        INSERT INTO dwd_xxx
        SELECT ... FROM {source}_xxx WHERE dt = '{dt}'
    """

    rows = execute_sql(sql)
    logger.info(f"[SUCCESS] DWD xxx, 影响行数: {rows}")
    return rows


def run_dwd(dt: str) -> None:
    """执行 DWD 层所有任务"""
    run_dwd_xxx(dt)


def run_etl(dt: str, layer: str = "all") -> None:
    """ETL 主入口"""
    if layer in ("all", "dwd"):
        run_dwd(dt)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dt", required=True)
    parser.add_argument("--layer", default="all")
    args = parser.parse_args()

    run_etl(args.dt, args.layer)
```

---

## 代码质量

### 工具配置

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py312']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.12"
warn_return_any = true
strict = true
```

### 质量检查

```bash
# 格式化
black scripts/

# 导入排序
isort scripts/

# 类型检查
mypy scripts/

# 代码检查
ruff check scripts/
```