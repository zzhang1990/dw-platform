# SQL 编码规范

## 基本规范

### 关键字

- 使用大写
- 每个关键字独占一行

```sql
-- 正确
SELECT
    user_id,
    user_name
FROM user_table
WHERE dt = '2024-01-01'

-- 错误
select user_id, user_name from user_table where dt = '2024-01-01'
```

### 缩进

- 使用 4 空格缩进
- 子查询缩进一层

```sql
SELECT
    user_id,
    (
        SELECT COUNT(*)
        FROM order_table
        WHERE user_id = u.user_id
    ) AS order_cnt
FROM user_table u
```

---

## SELECT 语句

### 字段列表

```sql
SELECT
    user_id,
    user_name,
    email,
    created_at,
    updated_at
FROM user_table
```

### 别名

```sql
-- 使用 AS 关键字
SELECT
    user_id,
    COUNT(*) AS order_cnt,
    SUM(amount) AS total_amt
FROM order_table
GROUP BY user_id
```

### 表别名

```sql
-- 使用有意义的别名
SELECT
    u.user_id,
    u.user_name,
    o.order_id
FROM user_table u
LEFT JOIN order_table o ON u.user_id = o.user_id
```

---

## JOIN 规范

### JOIN 类型

```sql
-- INNER JOIN
FROM table_a a
INNER JOIN table_b b ON a.id = b.a_id

-- LEFT JOIN（推荐）
FROM table_a a
LEFT JOIN table_b b ON a.id = b.a_id

-- 避免 RIGHT JOIN，改用 LEFT JOIN
```

### 多表 JOIN

```sql
SELECT
    u.user_id,
    u.user_name,
    o.order_id,
    p.product_name
FROM user_table u
LEFT JOIN order_table o ON u.user_id = o.user_id
LEFT JOIN product_table p ON o.product_id = p.product_id
WHERE u.dt = '{dt}'
```

---

## WHERE 条件

### 条件格式

```sql
WHERE
    dt = '{dt}'
    AND status = 'active'
    AND created_at >= '2024-01-01'
```

### 分区条件

```sql
-- 分区条件放在最前面
WHERE
    dt = '{dt}'
    AND other_conditions
```

### IN 条件

```sql
-- 少量值
WHERE status IN ('active', 'pending')

-- 大量值使用临时表或子查询
WHERE user_id IN (
    SELECT user_id FROM active_users
)
```

---

## GROUP BY 和聚合

### 分组

```sql
SELECT
    user_id,
    dt,
    COUNT(*) AS cnt,
    SUM(amount) AS total_amt,
    AVG(amount) AS avg_amt
FROM order_table
WHERE dt = '{dt}'
GROUP BY user_id, dt
```

### HAVING

```sql
SELECT
    user_id,
    COUNT(*) AS order_cnt
FROM order_table
WHERE dt = '{dt}'
GROUP BY user_id
HAVING COUNT(*) > 10
```

---

## 子查询

### WITH 语句

```sql
WITH user_orders AS (
    SELECT
        user_id,
        COUNT(*) AS order_cnt
    FROM order_table
    WHERE dt = '{dt}'
    GROUP BY user_id
),
active_users AS (
    SELECT user_id
    FROM user_table
    WHERE status = 'active'
)
SELECT
    u.user_id,
    u.user_name,
    COALESCE(o.order_cnt, 0) AS order_cnt
FROM active_users a
LEFT JOIN user_orders o ON a.user_id = o.user_id
```

### 嵌套子查询

```sql
SELECT
    user_id,
    order_cnt
FROM (
    SELECT
        user_id,
        COUNT(*) AS order_cnt
    FROM order_table
    WHERE dt = '{dt}'
    GROUP BY user_id
) t
WHERE order_cnt > 10
```

---

## INSERT 语句

### INSERT INTO

```sql
INSERT INTO target_table
(
    user_id,
    user_name,
    dt
)
SELECT
    user_id,
    user_name,
    dt
FROM source_table
WHERE dt = '{dt}'
```

### INSERT OVERWRITE

```sql
INSERT OVERWRITE TABLE target_table
SELECT
    user_id,
    user_name,
    dt
FROM source_table
WHERE dt = '{dt}'
```

---

## 性能优化

### 分区裁剪

```sql
-- 使用分区条件
WHERE dt = '{dt}'
  AND dt_hour = '{hour}'
```

### 索引利用

```sql
-- 使用索引字段
WHERE user_id = '{user_id}'  -- user_id 是索引
```

### 避免全表扫描

```sql
-- 错误：使用函数导致索引失效
WHERE DATE_FORMAT(created_at, '%Y-%m-%d') = '2024-01-01'

-- 正确：范围查询
WHERE created_at >= '2024-01-01 00:00:00'
  AND created_at < '2024-01-02 00:00:00'
```

### LIMIT 使用

```sql
-- 查询前 N 条
SELECT *
FROM large_table
WHERE dt = '{dt}'
LIMIT 1000
```

---

## 注释规范

### 单行注释

```sql
-- 用户状态统计
SELECT status, COUNT(*) AS cnt
FROM user_table
GROUP BY status
```

### 多行注释

```sql
/*
 * 财务报表查询
 * 统计各部门收入情况
 * 按日期和部门分组
 */
SELECT
    dt,
    dept_id,
    SUM(amount) AS total_amt
FROM finance_table
GROUP BY dt, dept_id
```

### 字段注释

```sql
SELECT
    user_id,           -- 用户ID
    user_name,         -- 用户名
    COUNT(*) AS cnt    -- 订单数量
FROM order_table
```