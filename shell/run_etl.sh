#!/bin/bash
# ETL 任务执行脚本
# 用法: bash run_etl.sh <sql_file> <dt>

set -e

SQL_FILE=$1
DT=${2:-$(date +%Y-%m-%d)}

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

echo "========================================"
echo "开始执行 ETL 任务"
echo "SQL 文件: $SQL_FILE"
echo "日期参数: $DT"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

cd "$PROJECT_DIR"

python scripts/etl/run_sql.py --sql "$SQL_FILE" --dt "$DT"

echo "========================================"
echo "ETL 任务执行完成"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"