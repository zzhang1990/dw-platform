# 脱敏财务纵向 ETL 样例

## 目标

本样例提供一条可审查、可 dry-run、可在独立 StarRocks 测试环境执行的纵向链路：

```text
demo_ods.ods_demo_project
          |
          v
demo_dim.dim_demo_project
          |
          +-------------------------------+
                                          v
demo_ods.ods_demo_order_receivable -> demo_dwd.dwd_demo_order_receivable
                                          |
                                          v
                        demo_dws.dws_demo_project_monthly_receivable
                                          |
                                          v
                        demo_ads.ads_demo_project_monthly_finance
```

仓库中的表名、字段、演示数据和库名均为公开样例。它们不对应任何私有项目中的真实名称、
账号、连接地址或 API key。

## 搬运范围

样例保留了可复用的工程模式：

- DIM -> DWD -> DWS -> ADS 的依赖顺序。
- 每个任务可独立调度，也可通过统一入口串行执行。
- `biz_date` 真实参与截止日期或统计月份过滤，支持历史补数审查。
- 全量和滚动重算任务使用临时表装载、非空校验、重复键校验、原子 `SWAP` 和异常清理。
- `--dry-run` 只渲染 SQL，不连接数据库。
- 批量 SQL 拆分、失败重试和逐条耗时日志。

没有搬运私有配置、真实表名、内部路径、账号、密码、token、API key 或私有业务扩展字段。

## SQL 资产

| 文件 | 用途 |
| --- | --- |
| [`examples/starrocks/demo_finance_chain.sql`](../../examples/starrocks/demo_finance_chain.sql) | 创建 5 个 demo 数据库、2 个 ODS 输入表和 4 个分层目标表 |
| [`examples/starrocks/demo_finance_seed.sql`](../../examples/starrocks/demo_finance_seed.sql) | 插入脱敏演示数据 |
| [`examples/starrocks/demo_finance_validation.sql`](../../examples/starrocks/demo_finance_validation.sql) | 查询 ADS 结果并检查重复粒度 |

每层转换 SQL 内嵌在对应 Python 任务中：

| 顺序 | 层级 | 任务脚本 | 策略 |
| --- | --- | --- | --- |
| 1 | DIM | [`proc_dim_demo_project.py`](../../scripts/etl/dim/proc_dim_demo_project.py) | 全量快照 + `SWAP` |
| 2 | DWD | [`proc_dwd_demo_order_receivable.py`](../../scripts/etl/dwd/proc_dwd_demo_order_receivable.py) | 全量快照 + `SWAP` |
| 3 | DWS | [`proc_dws_demo_project_monthly_receivable.py`](../../scripts/etl/dws/proc_dws_demo_project_monthly_receivable.py) | 滚动重算快照 + `SWAP` |
| 4 | ADS | [`proc_ads_demo_project_monthly_finance.py`](../../scripts/etl/ads/proc_ads_demo_project_monthly_finance.py) | 滚动重算快照 + `SWAP` |

## 刷新流程

公共刷新框架位于
[`scripts/utils/etl_refresh.py`](../../scripts/utils/etl_refresh.py)：

```text
删除可能残留的同名临时表
  -> CREATE TABLE shadow LIKE serving_table
  -> INSERT INTO shadow SELECT ...
  -> 校验 shadow 非空
  -> 校验 shadow 业务粒度没有重复
  -> ALTER TABLE serving_table SWAP WITH shadow
  -> 删除交换后的旧表
```

装载或校验失败时不会执行 `SWAP`，只会尝试清理临时表。正式表继续保留最近一次成功快照。

`SWAP` 适合体量可控、需要整体替换的快照表。增量明细、分区覆盖和 CDC 同步任务应分别设计，
不应机械套用该模式。

StarRocks 官方参考：

- [`CREATE TABLE LIKE`](https://docs.starrocks.io/docs/sql-reference/sql-statements/table_bucket_part_index/CREATE_TABLE_LIKE/)
- [`ALTER TABLE ... SWAP WITH`](https://docs.starrocks.io/docs/sql-reference/sql-statements/table_bucket_part_index/ALTER_TABLE/#swap)

## 执行步骤

先在独立测试环境创建 demo 表并装载演示数据：

```bash
mysql -h <host> -P <port> -u <user> -p < examples/starrocks/demo_finance_chain.sql
mysql -h <host> -P <port> -u <user> -p < examples/starrocks/demo_finance_seed.sql
```

提交数据库执行前，先审查完整 SQL 计划：

```bash
python scripts/etl/etl.py --dt 2026-05-31 --layer all --dry-run
bash shell/run_etl.sh 2026-05-31 all --dry-run
```

确认 SQL 后，在已经配置 `.env` 的测试环境执行：

```bash
python scripts/etl/etl.py --dt 2026-05-31 --layer all
```

最后运行验收查询：

```bash
mysql -h <host> -P <port> -u <user> -p < examples/starrocks/demo_finance_validation.sql
```

## 补数与重复执行

- 补数时传入目标日期，例如 `--dt 2026-05-15`。
- 相同日期可重复执行。临时表名包含日期和运行 token，不会复用上一次临时表。
- 演示 ODS 是当前状态表，只能按 `created_at` 限制数据截止时间。若需要还原严格历史状态，应使用带版本的 ODS 历史表。

## 上线前检查

1. 使用独立测试数据库，不要直接对生产库执行公开样例。
2. 确认执行账号具备目标 demo 数据库的 `CREATE TABLE`、`SELECT`、`ALTER` 和 `DROP` 权限。
3. 先运行 `--dry-run` 审查 SQL。
4. 人工制造一次装载失败，确认没有执行 `SWAP`。
5. 连续执行两次相同日期，核对 ADS 结果一致。
