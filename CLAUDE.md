# DW Platform - StarRocks 数仓平台

## 技术栈
- 数据库: StarRocks
- 调度: DolphinScheduler
- 同步: CloudCanal, DataX
- 语言: Python 3.12+, Shell

## 数据采集架构

| 方式 | 场景 | 工具 |
|------|------|------|
| 实时同步 | PostgreSQL 等支持 CDC 的源库 | CloudCanal |
| 批量同步 | 不支持 CDC 或不能开启 CDC 的源库 | DataX |
| API 采集 | 不能直连数据库的第三方系统 | Python 脚本 |

## 数仓分层规范

### 分层说明
- **ODS** (贴源层): 保持原始数据，表名 `ods_{source}_{table}`
- **DWD** (明细层): 清洗标准化数据，表名 `dwd_{domain}_{entity}`
- **ADS** (应用层): 面向业务指标，表名 `ads_{business}_{metric}`

### 主题划分
- **finance**: 财务主题 - 账单、收入、成本
- **marketing**: 营销主题 - 活动、用户行为、转化

## 编码规范

### Python
- 使用类型注解
- SQL 内嵌在 Python 脚本中
- 遵循 PEP 8，使用 Black 格式化

### SQL
- 关键字大写 (SELECT, FROM, WHERE 等)
- 使用 f-string 传入参数

### Shell
- 使用 `#!/bin/bash` 开头
- 使用 `set -e` 错误退出
- 包含日志记录

## 文件命名规范
- ETL 脚本: `{topic}_etl.py`，如 `finance_etl.py`
- API 采集: `fetch_{source}_data.py`
- DataX: `{source}_to_starrocks_{table}.json`

## DolphinScheduler 任务
- ETL 任务: `bash shell/run_etl.sh <finance|marketing> <dt>`
- DataX 任务: `bash shell/run_datax.sh <config.json>`
- API 采集: `bash shell/run_api.sh <script.py>`

## 常用命令
```bash
# 执行财务主题 ETL
bash shell/run_etl.sh finance 2024-01-01

# 执行营销主题 ETL
bash shell/run_etl.sh marketing 2024-01-01

# 运行 DataX 同步
bash shell/run_datax.sh mysql_to_starrocks_user.json

# 执行 API 数据采集
python scripts/api/fetch_marketing_data.py --dt 2024-01-01
```