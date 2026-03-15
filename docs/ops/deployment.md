# 部署文档

## 环境要求

### 软件依赖

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.12+ | ETL 开发 |
| Conda | 最新 | 环境管理 |
| StarRocks | 3.x | OLAP 数据库 |
| DolphinScheduler | 3.x | 任务调度 |
| CloudCanal | 最新 | 实时同步 |
| DataX | 最新 | 批量同步 |

### 硬件要求

| 组件 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| StarRocks FE | 8核 | 16GB | 100GB SSD |
| StarRocks BE | 16核 | 64GB | 1TB SSD |
| DolphinScheduler | 4核 | 8GB | 50GB |
| ETL 服务器 | 4核 | 8GB | 100GB |

---

## 部署步骤

### 1. 项目部署

```bash
# 克隆项目
git clone https://github.com/org/dw-platform.git
cd dw-platform

# 创建 Conda 环境
conda env create -f environment.yml

# 激活环境
conda activate dw-platform

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

### 2. StarRocks 配置

```sql
-- 创建数据库
CREATE DATABASE dw;

-- 创建用户
CREATE USER 'dw_user'@'%' IDENTIFIED BY 'password';

-- 授权
GRANT ALL PRIVILEGES ON dw.* TO 'dw_user'@'%';
```

### 3. DolphinScheduler 配置

1. 创建项目：`dw-platform`
2. 配置环境变量
3. 创建工作流
4. 配置任务调度

### 4. CloudCanal 配置

1. 创建数据源连接
2. 配置同步任务
3. 启动同步

---

## 配置文件

### 环境变量 (.env)

```bash
# StarRocks
STARROCKS_HOST=localhost
STARROCKS_PORT=9030
STARROCKS_USER=root
STARROCKS_PASSWORD=
STARROCKS_DATABASE=dw

# PostgreSQL
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=
PG_DATABASE=source_db

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=source_db

# DolphinScheduler
DS_HOST=localhost
DS_PORT=12345
DS_TOKEN=
```

### Conda 环境 (environment.yml)

```yaml
name: dw-platform
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.12
  - pip
  - pip:
    - starrocks
    - pandas
    - requests
    - python-dotenv
```

---

## 目录结构

```
/opt/dw-platform/
├── scripts/          # 业务脚本
├── shell/            # Shell 脚本
├── datax/            # DataX 配置
├── cloudcanal/       # CloudCanal 配置
├── logs/             # 日志目录
├── data/             # 数据目录
└── config/           # 配置文件
```

---

## 启动服务

```bash
# 启动 ETL 任务
bash shell/run_etl.sh 2024-01-01

# 启动数据同步
bash shell/run_sync.sh

# 启动 API 采集
python scripts/api/fetch_data.py --dt 2024-01-01
```

---

## 监控检查

```bash
# 检查服务状态
systemctl status starrocks-fe
systemctl status starrocks-be
systemctl status dolphinscheduler

# 检查日志
tail -f logs/etl_2024-01-01.log

# 检查数据
python scripts/utils/check_data.py --dt 2024-01-01
```