# 监控告警

## 监控指标

### 系统指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| CPU 使用率 | 服务器 CPU | > 80% |
| 内存使用率 | 服务器内存 | > 85% |
| 磁盘使用率 | 磁盘空间 | > 85% |
| 网络流量 | 网络带宽 | > 80% |

### StarRocks 指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| QPS | 每秒查询数 | > 1000 |
| 查询延迟 | 平均响应时间 | > 5s |
| 慢查询 | 慢查询数量 | > 10/min |
| 导入延迟 | 数据导入时间 | > 10min |
| BE 存活 | Backend 节点状态 | 任一节点下线 |

### ETL 指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 任务成功率 | 任务执行成功率 | < 100% |
| 任务延迟 | 任务执行时间 | > 预期 2x |
| 数据量 | 处理数据量 | 波动 > 50% |
| 数据质量 | 空值率/重复率 | > 阈值 |

---

## 监控方案

### Prometheus + Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'starrocks'
    static_configs:
      - targets: ['starrocks-fe:9030']
    metrics_path: '/metrics'

  - job_name: 'dolphinscheduler'
    static_configs:
      - targets: ['dolphinscheduler:12345']
```

### Grafana 看板

1. **系统监控看板**
   - CPU/内存/磁盘/网络
   - 进程状态

2. **StarRocks 监控看板**
   - QPS/延迟
   - 慢查询分析
   - 导入状态

3. **ETL 监控看板**
   - 任务执行状态
   - 数据量趋势
   - 错误统计

---

## 告警配置

### 告警渠道

| 渠道 | 场景 | 优先级 |
|------|------|--------|
| 钉钉 | 实时告警 | P1/P2 |
| 邮件 | 日报/周报 | P3 |
| 短信 | 紧急告警 | P1 |

### 告警规则

```yaml
# alertmanager/rules.yml
groups:
  - name: etl_alerts
    rules:
      - alert: ETFTaskFailed
        expr: etl_task_success_rate < 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ETL 任务失败"

      - alert: ETLDelayHigh
        expr: etl_task_duration_seconds > 600
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ETL 任务执行时间过长"
```

### 钉钉告警

```python
import requests
import json

def send_dingtalk_alert(message: str):
    """发送钉钉告警"""
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=xxx"

    data = {
        "msgtype": "text",
        "text": {"content": message}
    }

    requests.post(webhook, json=data)
```

---

## 数据质量监控

### 质量检查脚本

```python
# scripts/utils/data_quality.py

def check_table_quality(table: str, dt: str) -> dict:
    """检查表数据质量"""
    results = {}

    # 行数检查
    row_count = query_one(f"SELECT COUNT(*) as cnt FROM {table} WHERE dt = '{dt}'")
    results['row_count'] = row_count['cnt']

    # 空值检查
    null_rate = query_one(f"""
        SELECT AVG(CASE WHEN column IS NULL THEN 1 ELSE 0 END) as rate
        FROM {table} WHERE dt = '{dt}'
    """)
    results['null_rate'] = null_rate['rate']

    # 重复检查
    dup_count = query_one(f"""
        SELECT COUNT(*) - COUNT(DISTINCT id) as dup
        FROM {table} WHERE dt = '{dt}'
    """)
    results['dup_count'] = dup_count['dup']

    return results
```

### 质量告警规则

| 检查项 | 阈值 | 告警级别 |
|--------|------|----------|
| 行数为 0 | = 0 | Critical |
| 空值率 | > 10% | Warning |
| 重复率 | > 1% | Warning |
| 数据波动 | > 50% | Warning |

---

## 日志监控

### 日志采集

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /opt/dw-platform/logs/*.log
    fields:
      type: etl

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "dw-platform-%{+yyyy.MM.dd}"
```

### 日志分析

1. **错误日志统计**
   - 按错误类型分组
   - 错误趋势分析

2. **性能日志分析**
   - 任务执行时间
   - 慢任务识别

---

## 值班响应

### P1 紧急告警

1. 5 分钟内响应
2. 30 分钟内定位问题
3. 1 小时内修复或临时方案

### P2 重要告警

1. 30 分钟内响应
2. 2 小时内定位问题
3. 当天内修复

### P3 一般告警

1. 2 小时内响应
2. 根据情况安排修复