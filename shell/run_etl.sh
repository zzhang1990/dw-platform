#!/bin/bash
# ETL 任务执行脚本
# 用法: bash run_etl.sh <dt> <layer> [--dry-run]
# layer: dim/dwd/dws/ads/all

set -euo pipefail

DT=${1:-$(date +%Y-%m-%d)}
LAYER=${2:-all}
DRY_RUN=${3:-}

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

echo "========================================"
echo "开始执行 ETL 任务"
echo "日期: $DT"
echo "层级: $LAYER"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

cd "$PROJECT_DIR"

if [ "$DRY_RUN" = "--dry-run" ]; then
    python scripts/etl/etl.py --dt "$DT" --layer "$LAYER" --dry-run
else
    python scripts/etl/etl.py --dt "$DT" --layer "$LAYER"
fi

echo "========================================"
echo "ETL 任务执行完成"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
