#!/bin/bash
# API 数据采集脚本
# 用法: bash run_api.sh <script_name> [args...]

set -e

SCRIPT_NAME=$1
shift

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

if [ -z "$SCRIPT_NAME" ]; then
    echo "错误: 请指定脚本名称"
    echo "用法: bash run_api.sh <script_name> [args...]"
    exit 1
fi

echo "========================================"
echo "开始执行 API 数据采集"
echo "脚本: $SCRIPT_NAME"
echo "参数: $@"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

cd "$PROJECT_DIR"

python "scripts/api/$SCRIPT_NAME" "$@"

echo "========================================"
echo "API 数据采集完成"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"