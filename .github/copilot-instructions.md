# GitHub Copilot 指令

## 项目上下文
这是一个 StarRocks 数仓项目，包含财务和营销两个主题。

## 代码建议规则
1. SQL 使用大写关键字
2. Python 使用类型注解
3. 表命名遵循分层规范: ods_*, dwd_*, ads_*
4. 日期参数使用 `dt` 格式: YYYY-MM-DD

## 常用模式
- 数据库连接: `scripts/utils/db.py`
- SQL 执行: `scripts/etl/run_sql.py`
- 配置读取: `config/settings.py`