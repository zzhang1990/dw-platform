# 故障排查

## 常见问题

### 1. ETL 任务失败

**现象：** 任务执行报错，状态为失败

**排查步骤：**

```bash
# 1. 查看任务日志
tail -200 logs/etl_2024-01-01.log

# 2. 检查数据库连接
python -c "from scripts.utils.db import test_connection; test_connection()"

# 3. 检查源数据
SELECT COUNT(*) FROM ods_xxx WHERE dt = '2024-01-01';

# 4. 手动执行 SQL
python scripts/etl/etl.py --dt 2024-01-01 --layer dwd
```

**常见原因：**
- 数据库连接失败
- 源数据不存在
- SQL 语法错误
- 内存不足

---

### 2. 数据同步延迟

**现象：** CloudCanal/DataX 同步延迟高

**排查步骤：**

```bash
# CloudCanal
# 检查任务状态
# 检查同步延迟

# DataX
# 查看执行日志
grep "Total" logs/datax_xxx.log

# 检查网络
ping ${SOURCE_HOST}
ping ${TARGET_HOST}
```

**解决方案：**
- 增加并发数
- 优化查询 SQL
- 检查网络带宽
- 分批同步

---

### 3. StarRocks 查询慢

**现象：** 查询响应时间过长

**排查步骤：**

```sql
-- 1. 查看慢查询
SHOW RUNNING QUERIES;

-- 2. 分析查询计划
EXPLAIN SELECT ... FROM ... WHERE ...;

-- 3. 检查表统计信息
SHOW TABLE STATUS;

-- 4. 检查分区
SHOW PARTITIONS FROM table_name;
```

**优化方案：**
- 添加索引
- 分区裁剪
- 物化视图
- 调整内存配置

---

### 4. 内存溢出 (OOM)

**现象：** 任务执行中内存不足

**排查步骤：**

```bash
# 1. 查看内存使用
free -h
top -p $(pgrep -f "python.*etl")

# 2. 分析内存
python -m memory_profiler scripts/etl/etl.py

# 3. 检查数据量
SELECT COUNT(*) FROM large_table WHERE dt = '2024-01-01';
```

**解决方案：**
- 分批处理
- 减少内存占用
- 增加服务器内存
- 优化代码逻辑

---

### 5. 磁盘空间不足

**现象：** 磁盘使用率过高

**排查步骤：**

```bash
# 1. 查看磁盘使用
df -h

# 2. 查找大文件
du -sh /opt/dw-platform/* | sort -hr

# 3. 查找旧日志
find logs/ -mtime +30 -name "*.log"

# 4. 查看表大小
SHOW DATA FROM table_name;
```

**解决方案：**
- 清理旧日志
- 删除临时文件
- 清理旧分区数据
- 扩容磁盘

---

## 故障处理流程

### 1. 故障发现

```
监控告警 → 值班人员确认 → 创建故障工单
```

### 2. 故障定位

```
查看日志 → 分析原因 → 确定影响范围
```

### 3. 故障处理

```
制定方案 → 执行修复 → 验证结果
```

### 4. 故障复盘

```
分析根因 → 制定改进措施 → 更新文档
```

---

## 应急预案

### 数据恢复

```bash
# 从备份恢复
# 1. 恢复表结构
mysql -h host -P port -u user -p < backup/schema.sql

# 2. 恢复数据
mysql -h host -P port -u user -p < backup/data.sql

# 或从 ODS 层重新处理
python scripts/etl/etl.py --dt 2024-01-01 --layer all --rebuild
```

### 任务重跑

```bash
# DolphinScheduler 补数据
# 1. 选择任务
# 2. 选择日期范围
# 3. 执行补数据

# 或手动执行
bash shell/run_etl.sh 2024-01-01 all
```

### 降级方案

```
1. 暂停非关键任务
2. 减少并发数
3. 使用备份数据
4. 切换到备用节点
```

---

## 联系方式

| 角色 | 姓名 | 电话 | 邮箱 |
|------|------|------|------|
| 主要负责人 | xxx | xxx | xxx@xxx.com |
| DBA | xxx | xxx | xxx@xxx.com |
| 运维 | xxx | xxx | xxx@xxx.com |
| 开发 | xxx | xxx | xxx@xxx.com |