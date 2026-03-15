#!/bin/bash
# DataX 同步任务执行脚本
# 用法: bash run_datax.sh <config_file>

set -e

CONFIG_FILE=$1

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

if [ -z "$CONFIG_FILE" ]; then
    echo "错误: 请指定 DataX 配置文件"
    echo "用法: bash run_datax.sh <config_file>"
    exit 1
fi

echo "========================================"
echo "开始执行 DataX 同步任务"
echo "配置文件: $CONFIG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# TODO: 修改为实际的 DataX 路径
DATAX_HOME=/opt/datax

python "$DATAX_HOME/bin/datax.py" "$PROJECT_DIR/datax/$CONFIG_FILE"

echo "========================================"
echo "DataX 同步任务执行完成"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"