# DW Platform - StarRocks 数仓平台

## 技术栈
- 数据库: StarRocks
- 调度: DolphinScheduler
- 同步: CloudCanal, DataX
- 语言: Python 3.12, Shell
- 环境管理: Conda

## 数据采集架构

| 方式 | 场景 | 工具 |
|------|------|------|
| 实时同步 | PostgreSQL 等支持 CDC 的源库 | CloudCanal |
| 批量同步 | 不支持 CDC 或不能开启 CDC 的源库 | DataX |
| API 采集 | 不能直连数据库的第三方系统 | Python 脚本 |

## 数仓分层规范

| 层级 | 说明 | 命名规范 |
|------|------|----------|
| ODS | 贴源层，原始数据 | `ods_{source}_{table}` |
| DWD | 明细层，清洗标准化 | `dwd_{domain}_{entity}` |
| ADS | 应用层，业务指标 | `ads_{business}_{metric}` |

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
- ETL 脚本: `scripts/etl/etl.py`
- API 采集: `scripts/api/fetch_{source}_data.py`
- DataX: `datax/{source}_to_starrocks_{table}.json`

## 环境配置

```bash
# 创建 conda 环境
conda env create -f environment.yml

# 激活环境
conda activate dw-platform

# 更新环境
conda env update -f environment.yml
```

## DolphinScheduler 任务

```bash
# 执行完整 ETL
bash shell/run_etl.sh 2024-01-01

# 只执行 DWD 层
bash shell/run_etl.sh 2024-01-01 dwd

# 只执行 ADS 层
bash shell/run_etl.sh 2024-01-01 ads
```

## 常用命令

```bash
# 执行 ETL
python scripts/etl/etl.py --dt 2024-01-01 --layer all

# 执行 API 数据采集
python scripts/api/fetch_data.py --dt 2024-01-01

# 运行 DataX 同步
bash shell/run_datax.sh mysql_to_starrocks_user.json
```