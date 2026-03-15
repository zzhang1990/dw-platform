# DataX 批量同步配置

## 概述

DataX 用于不支持 CDC 或不能开启 CDC 的数据源批量同步到 StarRocks。

## 配置模板

### MySQL → StarRocks

```json
{
  "job": {
    "setting": {
      "speed": {
        "channel": 3,
        "batchSize": 5000
      },
      "errorLimit": {
        "record": 0,
        "percentage": 0.02
      }
    },
    "content": [
      {
        "reader": {
          "name": "mysqlreader",
          "parameter": {
            "username": "${MYSQL_USER}",
            "password": "${MYSQL_PASSWORD}",
            "column": ["id", "name", "status", "created_at", "updated_at"],
            "connection": [
              {
                "table": ["source_table"],
                "jdbcUrl": ["jdbc:mysql://${MYSQL_HOST}:3306/source_db"]
              }
            ],
            "where": "updated_at >= '${START_TIME}' AND updated_at < '${END_TIME}'"
          }
        },
        "writer": {
          "name": "starrockswriter",
          "parameter": {
            "username": "${STARROCKS_USER}",
            "password": "${STARROCKS_PASSWORD}",
            "database": "dw",
            "table": "ods_mysql_source_table",
            "column": ["id", "name", "status", "created_at", "updated_at", "dt"],
            "preSql": ["DELETE FROM ods_mysql_source_table WHERE dt = '${DT}'"],
            "postSql": [],
            "jdbcUrl": "jdbc:mysql://${STARROCKS_HOST}:9030/",
            "loadProps": {
              "format": "json",
              "strip_outer_array": true
            }
          }
        }
      }
    ]
  }
}
```

### PostgreSQL → StarRocks

```json
{
  "job": {
    "content": [
      {
        "reader": {
          "name": "postgresqlreader",
          "parameter": {
            "username": "${PG_USER}",
            "password": "${PG_PASSWORD}",
            "column": ["*"],
            "connection": [
              {
                "table": ["source_table"],
                "jdbcUrl": ["jdbc:postgresql://${PG_HOST}:5432/source_db"]
              }
            ]
          }
        },
        "writer": {
          "name": "starrockswriter",
          "parameter": {
            "username": "${STARROCKS_USER}",
            "password": "${STARROCKS_PASSWORD}",
            "database": "dw",
            "table": "ods_pg_source_table",
            "column": ["*"],
            "jdbcUrl": "jdbc:mysql://${STARROCKS_HOST}:9030/"
          }
        }
      }
    ]
  }
}
```

---

## 文件命名规范

```
{source}_to_starrocks_{table}.json

示例：
- mysql_to_starrocks_user.json
- pg_to_starrocks_order.json
- oracle_to_starrocks_product.json
```

---

## 同步策略

### 全量同步

```json
{
  "reader": {
    "parameter": {
      "column": ["*"],
      "connection": [
        {
          "table": ["source_table"],
          "jdbcUrl": ["jdbc:mysql://..."]
        }
      ]
    }
  }
}
```

### 增量同步

```json
{
  "reader": {
    "parameter": {
      "column": ["*"],
      "where": "updated_at >= '${LAST_SYNC_TIME}'",
      "connection": [...]
    }
  }
}
```

---

## 执行脚本

```bash
#!/bin/bash
# shell/run_datax.sh

CONFIG_FILE=$1
DT=${2:-$(date -d "yesterday" +%Y-%m-%d)}

DATAX_HOME=/opt/datax

# 执行同步
python ${DATAX_HOME}/bin/datax.py \
  -p "-DDT=${DT}" \
  -p "-DSTART_TIME=${DT} 00:00:00" \
  -p "-DEND_TIME=${DT} 23:59:59" \
  datax/${CONFIG_FILE}
```

---

## 性能优化

### 并发配置

```json
{
  "setting": {
    "speed": {
      "channel": 3,
      "batchSize": 5000,
      "bytes": 1048576
    }
  }
}
```

### 内存配置

```json
{
  "setting": {
    "speed": {
      "channel": 3
    }
  },
  "jvm": "-Xms4G -Xmx4G"
}
```

---

## 错误处理

### 错误限制

```json
{
  "errorLimit": {
    "record": 100,
    "percentage": 0.01
  }
}
```

### 重试机制

- 失败任务自动重试 3 次
- 重试间隔 60 秒
- 记录错误日志

---

## 监控告警

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 执行时间 | 任务耗时 | 超过预期 2 倍 |
| 同步行数 | 数据量 | 波动超过 50% |
| 错误数 | 失败记录 | > 0 |