# 数仓分层规范详解

## 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                         ADS 应用层                           │
│              (业务指标、报表数据、宽表)                        │
├─────────────────────────────────────────────────────────────┤
│                         DWS 汇总层                           │
│              (轻度聚合、主题汇总、中间表)                      │
├─────────────────────────────────────────────────────────────┤
│                         DWD 明细层                           │
│              (清洗转换、标准化、明细数据)                       │
├─────────────────────────────────────────────────────────────┤
│                      DIM 维度层                              │
│              (维度表、字典表、配置数据)                        │
├─────────────────────────────────────────────────────────────┤
│                         ODS 贴源层                           │
│              (原始数据、增量/全量同步)                         │
└─────────────────────────────────────────────────────────────┘
```

## 各层详解

### ODS 层 (Operational Data Store)

**定位：** 贴源层，保持与源系统一致

**特点：**
- 数据结构与源系统一致
- 保留原始数据，不做清洗
- 增量或全量同步
- 增加分区字段 `dt`

**命名规范：** `ods_{source}_{table}`

| 字段 | 说明 | 示例 |
|------|------|------|
| source | 数据来源 | pg, mysql, api |
| table | 源表名（下划线） | user_info |

**示例：**
- `ods_pg_user_info` - PostgreSQL 用户信息表
- `ods_mysql_order` - MySQL 订单表
- `ods_api_marketing` - API 营销数据

---

### DIM 层 (Dimension)

**定位：** 维度层，存储维度数据

**特点：**
- 维度属性整合
- 缓慢变化维处理 (SCD2)
- 代理键生成
- 多源维度整合

**命名规范：** `dim_{dimension}`

| 类型 | 命名 | 说明 |
|------|------|------|
| 用户维度 | `dim_user` | 用户基本信息 |
| 产品维度 | `dim_product` | 产品信息 |
| 组织维度 | `dim_org` | 组织架构 |
| 时间维度 | `dim_date` | 日期维度 |
| 地理维度 | `dim_region` | 区域信息 |

**字段规范：**
- `{dimension}_key` - 代理键 (SK)
- `{dimension}_id` - 业务键 (NK)
- `effective_date` - 生效日期
- `expiry_date` - 失效日期
- `is_current` - 是否当前版本

---

### DWD 层 (Data Warehouse Detail)

**定位：** 明细层，清洗标准化后的明细数据

**特点：**
- 数据清洗、过滤
- 字段标准化
- 编码转换
- 维度关联 (可选)
- 保留明细粒度

**命名规范：** `dwd_{domain}_{entity}`

| 字段 | 说明 | 示例 |
|------|------|------|
| domain | 业务域 | finance, user, order |
| entity | 实体名 | detail, transaction |

**处理规则：**
1. 空值处理：填充默认值或标记
2. 重复数据：去重
3. 异常值：标记或过滤
4. 编码统一：转换为标准编码
5. 字段命名：统一为下划线命名

**示例：**
- `dwd_finance_detail` - 财务明细
- `dwd_order_detail` - 订单明细
- `dwd_user_behavior` - 用户行为明细

---

### DWS 层 (Data Warehouse Summary)

**定位：** 汇总层，轻度聚合的中间表

**特点：**
- 按主题汇总
- 轻度聚合
- 多维度预计算
- 支持上卷下钻

**命名规范：** `dws_{domain}_{granularity}_{metric}`

| 字段 | 说明 | 示例 |
|------|------|------|
| domain | 业务域 | user, order, finance |
| granularity | 粒度 | day, month, user |
| metric | 指标 | stat, summary |

**示例：**
- `dws_user_day_stat` - 用户日统计
- `dws_order_day_summary` - 订单日汇总
- `dws_finance_month_stat` - 财务月统计

---

### ADS 层 (Application Data Store)

**定位：** 应用层，面向业务的指标数据

**特点：**
- 面向业务需求
- 高度聚合
- 报表直连
- 性能优化

**命名规范：** `ads_{business}_{metric}`

| 字段 | 说明 | 示例 |
|------|------|------|
| business | 业务主题 | finance, marketing, sales |
| metric | 指标名称 | report, dashboard, kpi |

**示例：**
- `ads_finance_report` - 财务报表
- `ads_marketing_dashboard` - 营销看板
- `ads_sales_kpi` - 销售 KPI

---

## 数据流转原则

```
ODS → DIM/DWD → DWS → ADS

规则：
1. ODS 不能直接跳到 DWS/ADS
2. DIM 被 DWD/DWS/ADS 关联使用
3. ADS 只能由 DWS 或 DWD 生成
4. 每层职责清晰，不越级
```

## 增量 vs 全量

| 层级 | 策略 | 说明 |
|------|------|------|
| ODS | 增量/全量 | 根据源系统确定 |
| DIM | 全量 | 维度表一般较小 |
| DWD | 增量 | 明细数据量大 |
| DWS | 增量 | 汇总数据 |
| ADS | 全量/增量 | 根据业务需求 |