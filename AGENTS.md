# DW Platform - Agent Instructions

## Cursor Cloud specific instructions

### 项目概述

基于 Python 3.12 的 StarRocks 数仓 ETL 平台，无 Web 服务，纯脚本项目。详细规范见 `CLAUDE.md`。

### 常用命令

| 操作 | 命令 |
|------|------|
| 测试 | `python3 -m pytest tests/ -v` |
| 代码格式检查 | `python3 -m black --check .` |
| Lint 检查 | `python3 -m ruff check .` |
| 运行 ETL | `python3 scripts/etl/etl.py --dt 2024-01-01 --layer all` |

### 注意事项

- 环境中 `python` 命令不存在，只有 `python3`。Shell 脚本 (`shell/*.sh`) 内使用了 `python`，直接执行会失败；开发时请使用 `python3` 直接调用 Python 脚本。
- Lint 工具 (`ruff`, `black`, `pytest`) 需通过 `python3 -m <tool>` 方式调用，因为 pip 安装的 console_scripts 可能不在 PATH 上。
- `.env` 文件从 `.env.example` 复制而来，包含 StarRocks 连接配置。Cloud 环境中没有 StarRocks 实例，涉及数据库连接的功能无法端到端测试，但模块导入和单元测试可以正常运行。
- 现有代码存在 ruff/black 格式问题（缺少尾部换行、import 排序），这是仓库原始状态，不要在无关 PR 中修复。
