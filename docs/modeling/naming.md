# 命名规范

## 表命名规范

### 通用规则

1. 使用小写字母和下划线
2. 长度不超过 64 字符
3. 见名知意，避免缩写
4. 单数形式（除汇总表外）

### 各层命名

```
{layer}_{domain}_{entity}

layer: ods, dim, dwd, dws, ads
domain: 业务域
entity: 实体/指标
```

### ODS 层

```
ods_{source}_{table}

示例：
- ods_pg_user_info      # PostgreSQL 用户表
- ods_mysql_order       # MySQL 订单表
- ods_api_product       # API 产品数据
```

### DIM 层

```
dim_{dimension}

示例：
- dim_user              # 用户维度
- dim_product           # 产品维度
- dim_organization      # 组织维度
- dim_date              # 日期维度
- dim_region            # 区域维度
```

### DWD 层

```
dwd_{domain}_{entity}

示例：
- dwd_finance_detail    # 财务明细
- dwd_order_detail      # 订单明细
- dwd_user_behavior     # 用户行为
```

### DWS 层

```
dws_{domain}_{granularity}_{metric}

示例：
- dws_user_day_stat     # 用户日统计
- dws_order_month_sum   # 订单月汇总
- dws_product_day_cnt   # 产品日计数
```

### ADS 层

```
ads_{business}_{metric}

示例：
- ads_finance_report    # 财务报表
- ads_sales_dashboard   # 销售看板
- ads_user_kpi          # 用户 KPI
```

---

## 字段命名规范

### 主键

```
{table}_id 或 id

示例：
- user_id
- order_id
- id
```

### 外键

```
{referenced_table}_id

示例：
- user_id       # 关联用户
- product_id    # 关联产品
```

### 时间字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |
| `dt` | DATE | 分区日期 |
| `dt_hour` | STRING | 分区小时 |

### 金额字段

```
{entity}_amt    # 金额（元）
{entity}_cnt    # 数量
{entity}_rate   # 比率

示例：
- order_amt      # 订单金额
- order_cnt      # 订单数量
- discount_rate  # 折扣率
```

### 布尔字段

```
is_{description}

示例：
- is_active      # 是否有效
- is_deleted     # 是否删除
- is_valid       # 是否合法
```

### 状态字段

```
{entity}_status

示例：
- order_status   # 订单状态
- pay_status     # 支付状态
```

---

## 字段类型规范

| 类型 | StarRocks | 说明 |
|------|-----------|------|
| 整数 | INT, BIGINT | 根据范围选择 |
| 小数 | DECIMAL(m,n) | 金额类必须使用 |
| 字符串 | VARCHAR(n) | 明确长度 |
| 日期 | DATE | 日期 |
| 时间 | DATETIME | 时间戳 |
| 布尔 | BOOLEAN | 或 TINYINT |

---

## 索引命名

```
idx_{table}_{column}

示例：
- idx_user_mobile
- idx_order_user_id
```

## 约束命名

```
pk_{table}              # 主键
uk_{table}_{column}     # 唯一键
fk_{table}_{ref_table}  # 外键
```

---

## 脚本命名规范

### ETL 脚本

```
{theme}.py

示例：
- finance.py      # 财务主题
- marketing.py    # 营销主题
- user.py         # 用户主题
```

### Shell 脚本

```
run_{task}.sh

示例：
- run_etl.sh      # ETL 任务
- run_sync.sh     # 同步任务
```

### DataX 配置

```
{source}_to_starrocks_{table}.json

示例：
- mysql_to_starrocks_user.json
- pg_to_starrocks_order.json
```