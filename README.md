# DW Platform

StarRocks 数仓平台 - 财务营销主题

## 技术栈

- **数据库**: StarRocks
- **调度**: DolphinScheduler
- **同步**: CloudCanal (实时), DataX (批量)
- **采集**: Python API 脚本
- **语言**: Python 3.12+, SQL, Shell

## 数据采集架构

| 方式 | 场景 | 工具 |
|------|------|------|
| 实时同步 | PostgreSQL 等支持 CDC 的源库 | CloudCanal |
| 批量同步 | 不支持 CDC 的源库 | DataX |
| API 采集 | 不能直连数据库的第三方系统 | Python 脚本 |

## 项目结构

```
dw-platform/
├── config/          # 配置文件
├── sql/             # SQL 脚本（按主题分层）
│   ├── finance/     # 财务主题
│   └── marketing/   # 营销主题
├── datax/           # DataX 同步配置
├── scripts/         # Python 脚本
│   ├── api/         # API 数据采集
│   ├── etl/         # ETL 脚本
│   └── utils/       # 工具函数
├── shell/           # DolphinScheduler 执行脚本
├── tests/           # 测试
└── docs/            # 文档
```

## 数仓分层

| 层级 | 说明 | 命名规范 |
|------|------|----------|
| ODS | 贴源层，原始数据 | `ods_{source}_{table}` |
| DWD | 明细层，清洗标准化 | `dwd_{domain}_{entity}` |
| ADS | 应用层，业务指标 | `ads_{business}_{metric}` |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 执行 SQL
bash shell/run_etl.sh sql/finance/dwd_finance_detail.sql 2024-01-01
```