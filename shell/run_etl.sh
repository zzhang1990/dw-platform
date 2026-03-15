#!/bin/bash
# ETL 任务执行脚本
# 用法: bash run_etl.sh <topic> <dt>
# topic: finance 或 marketing

set -e

TOPIC=$1
DT=${2:-$(date +%Y-%m-%d)}

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

if [ -z "$TOPIC" ]; then
    echo "错误: 请指定主题名称"
    echo "用法: bash run_etl.sh <finance|marketing> <dt>"
    exit 1
fi

echo "========================================"
echo "开始执行 ETL 任务"
echo "主题: $TOPIC"
echo "日期: $DT"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

cd "$PROJECT_DIR"

python "scripts/etl/${TOPIC}_etl.py" --dt "$DT"

echo "========================================"
echo "ETL 任务执行完成"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"