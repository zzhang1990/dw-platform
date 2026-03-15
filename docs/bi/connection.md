# 永洪BI 连接配置

## 连接 StarRocks

### 数据源配置

1. 进入永洪BI管理后台
2. 数据源 → 新建数据源
3. 选择 MySQL 协议（StarRocks 兼容）

### 连接参数

```yaml
名称: StarRocks-DW
类型: MySQL
主机: ${STARROCKS_HOST}
端口: 9030
数据库: dw
用户名: ${BI_USER}
密码: ${BI_PASSWORD}

高级设置:
  编码: UTF-8
  连接池大小: 10
  超时时间: 300s
```

### 连接测试

1. 点击"测试连接"
2. 确认连接成功
3. 保存数据源配置

---

## 数据集配置

### 创建数据集

1. 数据集 → 新建数据集
2. 选择数据源: StarRocks-DW
3. 选择表: ADS 层表

### 数据集类型

| 类型 | 用途 | 说明 |
|------|------|------|
| SQL 数据集 | 复杂查询 | 自定义 SQL |
| 表数据集 | 简单查询 | 直接选表 |
| 组合数据集 | 多表关联 | 可视化配置 |

### SQL 数据集示例

```sql
-- 财务报表数据集
SELECT
    dt,
    dept_name,
    SUM(order_amt) AS total_amt,
    COUNT(DISTINCT user_id) AS user_cnt
FROM ads_finance_report
WHERE dt >= '${start_date}'
  AND dt <= '${end_date}'
GROUP BY dt, dept_name
```

### 参数配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| start_date | 日期 | 今天-30 | 开始日期 |
| end_date | 日期 | 昨天 | 结束日期 |
| dept_name | 字符串 | 全部 | 部门筛选 |

---

## 性能优化

### 查询优化

1. **使用 ADS 层**
   - 报表直连 ADS 层
   - 避免 JOIN 操作
   - 预聚合数据

2. **分区裁剪**
   ```sql
   WHERE dt = '${date}'  -- 自动分区裁剪
   ```

3. **物化视图**
   ```sql
   -- StarRocks 创建物化视图
   CREATE MATERIALIZED VIEW mv_finance_report
   AS SELECT ... FROM ads_finance_report;
   ```

### 缓存配置

```yaml
缓存策略:
  启用缓存: 是
  缓存时长: 3600s  # 1小时
  刷新策略: 定时刷新
  刷新时间: 每天 06:00
```

---

## 权限管理

### 数据权限

1. 创建角色: 财务部、销售部
2. 配置行级权限
3. 关联用户和角色

### 行级权限示例

```sql
-- 按部门过滤
WHERE dept_id IN (SELECT dept_id FROM user_dept WHERE user_id = '${user_id}')
```

---

## 报表发布

### 发布流程

1. 开发报表
2. 测试验证
3. 申请发布
4. 管理员审核
5. 发布上线

### 访问控制

```yaml
报表权限:
  查看权限: 角色A, 角色B
  编辑权限: 开发者
  导出权限: 管理员
```