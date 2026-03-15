# CloudCanal 实时同步配置

## 概述

CloudCanal 用于 PostgreSQL 等支持 CDC 的数据源实时同步到 StarRocks。

## 任务配置

### 源端配置 (PostgreSQL)

```yaml
# 连接配置
host: ${PG_HOST}
port: 5432
database: source_db
user: replicator
password: ${PG_PASSWORD}

# 必须开启逻辑复制
# postgresql.conf
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10
```

### 目标端配置 (StarRocks)

```yaml
# 连接配置
host: ${STARROCKS_HOST}
port: 9030
database: dw
user: root
password: ${STARROCKS_PASSWORD}
```

### 同步配置

```yaml
# 任务类型
type: 实时同步

# 同步模式
mode: 全量 + 增量

# 表映射
table_mapping:
  source_table: ods_pg_{source_table}

# 字段映射
column_mapping:
  - source_column -> target_column

# 过滤条件
filter: null
```

---

## 任务命名规范

```
{source}_to_sr_{table}

示例：
- pg_to_sr_user
- pg_to_sr_order
- mysql_to_sr_product
```

---

## 目标表配置

### ODS 层表结构

```sql
CREATE TABLE IF NOT EXISTS ods_pg_{table} (
    -- 源表字段 (保持一致)
    id BIGINT,
    name VARCHAR(100),
    ...

    -- 系统字段
    _cdc_op VARCHAR(1),      -- 操作类型: I/U/D
    _cdc_ts DATETIME,        -- CDC 时间戳

    -- 分区字段
    dt DATE NOT NULL
)
DUPLICATE KEY(id)
PARTITION BY RANGE(dt) (
    PARTITION p202401 VALUES [('2024-01-01', '2024-02-01')),
    ...
)
DISTRIBUTED BY HASH(id) BUCKETS 3;
```

---

## 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| 同步延迟 | 源到目标的延迟 | < 5分钟 |
| 任务状态 | 运行/异常 | 正常运行 |
| 错误数量 | 同步错误数 | 0 |

---

## 常见问题

### 1. CDC 连接失败

```sql
-- 检查复制槽
SELECT * FROM pg_replication_slots;

-- 创建复制槽
SELECT pg_create_logical_replication_slot('cloudcanal_slot', 'pgoutput');
```

### 2. 目标表不存在

- CloudCanal 可自动建表
- 建议预先创建表结构

### 3. 数据类型不兼容

- 配置类型映射
- 使用转换函数