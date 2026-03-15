# DW Platform - StarRocks 数仓平台

## 技术栈
- 数据库: StarRocks
- 调度: DolphinScheduler
- 同步: CloudCanal, DataX
- 语言: Python 3.12+, SQL, Shell

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
- 遵循 PEP 8
- 使用 Black 格式化

### SQL
- 关键字大写 (SELECT, FROM, WHERE 等)
- 使用 4 空格缩进
- 表名、字段名使用小写下划线

### Shell
- 使用 `#!/bin/bash` 开头
- 使用 `set -e` 错误退出
- 包含日志记录

## 文件命名规范
- SQL: 小写下划线，如 `ods_finance_bill.sql`
- Python: 小写下划线，如 `fetch_marketing_data.py`
- DataX: `{source}_to_starrocks_{table}.json`

## DolphinScheduler 任务
- 所有任务通过 `shell/` 目录下的脚本执行
- 参数: `--dt` 日期、`--sql` SQL 文件路径

## 常用命令
```bash
# 执行 SQL 脚本
bash shell/run_etl.sh sql/finance/dwd_finance_detail.sql --dt 2024-01-01

# 运行 DataX 同步
bash shell/run_datax.sh datax/finance/sync_finance_bill.json

# 执行 API 数据采集
python scripts/api/fetch_marketing_data.py --dt 2024-01-01
```