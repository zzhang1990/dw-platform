# CloudCanal 同步任务

## 同步配置

| 任务名称 | 源库 | 目标库 | 同步方式 | 备注 |
|----------|------|--------|----------|------|
| pg_to_sr_finance | PostgreSQL | StarRocks | 实时 CDC | 财务数据 |
| pg_to_sr_marketing | PostgreSQL | StarRocks | 实时 CDC | 营销数据 |

## ODS 表命名规范

CloudCanal 同步到 ODS 层的表命名：`ods_{source}_{table}`

示例：
- `ods_pg_finance_bill` - PostgreSQL 财务账单表
- `ods_pg_user_info` - PostgreSQL 用户信息表

## 注意事项

1. CloudCanal 任务配置需在 CloudCanal 控制台操作
2. 同步的表会自动建表到 StarRocks
3. 字段映射和类型转换需在 CloudCanal 中配置