# DW Platform - StarRocks 数仓平台

## 项目概述

基于 StarRocks 的数据仓库平台，支持实时/批量数据同步、ETL 处理和报表生成。

## 目录结构

```
dw-platform/
├── config/           # 配置模块
│   └── settings.py  # 环境变量配置
├── scripts/         # 业务脚本
│   ├── etl/         # ETL 任务
│   ├── api/         # API 数据采集
│   └── utils/       # 公共工具
├── shell/           # Shell 脚本 (DolphinScheduler 调用)
├── datax/           # DataX 配置文件
├── cloudcanal/      # CloudCanal 任务配置
├── tests/           # 单元测试
└── docs/            # 文档
```

## 技术栈

| 组件 | 用途 | 版本 |
|------|------|------|
| StarRocks | OLAP 数据库 | 3.x |
| DolphinScheduler | 任务调度 | 3.x |
| CloudCanal | 实时同步 | - |
| DataX | 批量同步 | - |
| Python | ETL 开发 | 3.12 |
| Conda | 环境管理 | - |

## 数据采集架构

| 方式 | 场景 | 工具 |
|------|------|------|
| 实时同步 | PostgreSQL 等支持 CDC 的源库 | CloudCanal |
| 批量同步 | 不支持 CDC 或不能开启 CDC 的源库 | DataX |
| API 采集 | 不能直连数据库的第三方系统 | Python 脚本 |

## 数仓分层规范

| 层级 | 说明 | 命名规范 | 示例 |
|------|------|----------|------|
| ODS | 贴源层，原始数据 | `ods_{source}_{table}` | `ods_pg_finance_bill` |
| DWD | 明细层，清洗标准化 | `dwd_{domain}_{entity}` | `dwd_finance_detail` |
| ADS | 应用层，业务指标 | `ads_{business}_{metric}` | `ads_finance_report` |

---

## 编码规范

### Python

```python
# 1. 必须使用类型注解
def run_dwd_finance_detail(dt: str) -> int:
    ...

# 2. SQL 内嵌在 Python 中，使用 f-string 传参
sql = f"""
    SELECT *
    FROM ods_pg_finance_bill
    WHERE dt = '{dt}'
"""

# 3. 函数文档字符串
def run_dwd_user_behavior(dt: str) -> int:
    """
    DWD 层：用户行为明细清洗

    Args:
        dt: 日期参数 YYYY-MM-DD

    Returns:
        影响行数
    """
```

**格式化**: 使用 `black` 格式化，遵循 PEP 8

### SQL

```sql
-- 关键字大写，缩进清晰
SELECT
    user_id,
    COUNT(*) AS action_count
FROM dwd_user_behavior
WHERE dt = '{dt}'
GROUP BY user_id
```

### Shell

```bash
#!/bin/bash
# 脚本说明
# 用法: bash script.sh <args>

set -e  # 错误退出

# 日志格式
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行..."
```

---

## 数据库操作

### 连接配置

环境变量 (`.env`):
```bash
STARROCKS_HOST=localhost
STARROCKS_PORT=9030
STARROCKS_USER=root
STARROCKS_PASSWORD=
STARROCKS_DATABASE=dw
```

### 使用方式

```python
from scripts.utils.db import execute_sql, query_sql, query_one

# 执行 DML (INSERT/UPDATE/DELETE)
rows = execute_sql("INSERT INTO table VALUES (...)")

# 查询多行
results = query_sql("SELECT * FROM table WHERE dt = '2024-01-01'")

# 查询单行
row = query_one("SELECT COUNT(*) AS cnt FROM table")
```

---

## ETL 开发规范

### 函数命名

```python
# 按层级组织
def run_dwd_{domain}_{entity}(dt: str) -> int: ...
def run_ads_{business}_{metric}(dt: str) -> int: ...

# 层级入口函数
def run_dwd(dt: str): ...  # 执行所有 DWD 任务
def run_ads(dt: str): ...  # 执行所有 ADS 任务
```

### ETL 模板

```python
"""ETL 脚本 - {主题名称}"""
import logging
from scripts.utils.db import execute_sql

logger = logging.getLogger(__name__)


def run_dwd_xxx(dt: str) -> int:
    """DWD 层：xxx 明细清洗"""
    sql = f"""
        INSERT INTO dwd_xxx
        SELECT ... FROM ods_xxx WHERE dt = '{dt}'
    """
    logger.info(f"执行 DWD xxx, 日期: {dt}")
    return execute_sql(sql)


def run_dwd(dt: str):
    """执行 DWD 层所有任务"""
    run_dwd_xxx(dt)


def run_etl(dt: str, layer: str = "all"):
    """ETL 主入口"""
    if layer in ("all", "dwd"):
        run_dwd(dt)
```

---

## 文件命名规范

| 类型 | 路径 | 命名 |
|------|------|------|
| ETL 脚本 | `scripts/etl/` | `{theme}.py` |
| API 采集 | `scripts/api/` | `fetch_{source}_data.py` |
| DataX 配置 | `datax/` | `{source}_to_starrocks_{table}.json` |
| Shell 脚本 | `shell/` | `run_{task}.sh` |

---

## 环境配置

```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate dw-platform

# 更新环境
conda env update -f environment.yml

# 安装依赖
pip install -r requirements.txt
```

---

## 常用命令

### ETL 执行

```bash
# Python 直接执行
python scripts/etl/etl.py --dt 2024-01-01 --layer all
python scripts/etl/etl.py --dt 2024-01-01 --layer dwd
python scripts/etl/etl.py  # 默认昨天，all 层

# Shell 脚本执行 (DolphinScheduler 调用)
bash shell/run_etl.sh 2024-01-01
bash shell/run_etl.sh 2024-01-01 dwd
```

### API 数据采集

```bash
python scripts/api/fetch_marketing_data.py --dt 2024-01-01
bash shell/run_api.sh 2024-01-01
```

### DataX 同步

```bash
bash shell/run_datax.sh mysql_to_starrocks_user.json
```

### 测试

```bash
pytest tests/
pytest tests/ -v --cov=scripts
```

---

## Git 工作流

```bash
# 功能开发
git checkout -b feature/xxx
git commit -m "feat: 添加 xxx ETL 任务"

# 修复问题
git checkout -b fix/xxx
git commit -m "fix: 修复 xxx 问题"

# Commit 规范
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 重构
test: 测试
chore: 构建/工具
```

---

## Claude Code 指令

### 创建新 ETL 任务时

1. 在 `scripts/etl/` 创建或修改脚本
2. 遵循分层规范：ODS → DWD → ADS
3. 使用 `scripts/utils/db.py` 中的数据库工具
4. 在 `shell/run_etl.sh` 中添加调用入口

### 创建新 API 采集时

1. 在 `scripts/api/` 创建 `fetch_{source}_data.py`
2. 配置参数使用 `config/settings.py`
3. 在 `shell/run_api.sh` 中添加调用入口

### 创建 DataX 任务时

1. 在 `datax/` 创建 JSON 配置文件
2. 命名：`{source}_to_starrocks_{table}.json`
3. 在 `shell/run_datax.sh` 中添加调用入口