# Shell 编码规范

## 基本规范

### 脚本头部

```bash
#!/bin/bash
#================================================================
# 脚本名称: run_etl.sh
# 功能描述: 执行 ETL 任务
# 使用方法: bash run_etl.sh <dt> [layer]
# 作者: xxx
# 创建日期: 2024-01-01
#================================================================

set -e  # 遇错退出
set -u  # 未定义变量退出
set -o pipefail  # 管道错误退出
```

### 日志函数

```bash
# 日志函数
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
}
```

---

## 参数处理

### 位置参数

```bash
# 基本参数
dt=${1:-$(date -d "yesterday" +%Y-%m-%d)}
layer=${2:-"all"}

# 参数校验
if [[ ! "$dt" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    log_error "Invalid date format: $dt"
    exit 1
fi

log_info "参数: dt=$dt, layer=$layer"
```

### 命令行选项

```bash
# 使用 getopts
while getopts "d:l:h" opt; do
    case $opt in
        d) dt="$OPTARG" ;;
        l) layer="$OPTARG" ;;
        h) echo "Usage: $0 -d <date> -l <layer>"; exit 0 ;;
        ?) log_error "Invalid option: -$OPTARG"; exit 1 ;;
    esac
done

# 默认值
dt=${dt:-$(date -d "yesterday" +%Y-%m-%d)}
layer=${layer:-"all"}
```

---

## 环境配置

### 环境变量

```bash
# 加载环境变量
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

# 加载 .env
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Conda 环境
CONDA_ENV="dw-platform"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate $CONDA_ENV
```

### 路径配置

```bash
# 项目路径
PROJECT_ROOT="/opt/dw-platform"
SCRIPT_DIR="$PROJECT_ROOT/scripts"
LOG_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data"

# 创建目录
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"
```

---

## 函数定义

### 函数结构

```bash
# 函数定义
run_etl_task() {
    local dt=$1
    local layer=$2

    log_info "开始执行 ETL 任务: dt=$dt, layer=$layer"

    python "$SCRIPT_DIR/etl/etl.py" \
        --dt "$dt" \
        --layer "$layer"

    if [[ $? -eq 0 ]]; then
        log_success "ETL 任务执行成功"
    else
        log_error "ETL 任务执行失败"
        return 1
    fi
}
```

### 调用函数

```bash
# 主函数
main() {
    log_info "========== ETL 任务开始 =========="

    run_etl_task "$dt" "$layer"

    log_info "========== ETL 任务结束 =========="
}

# 执行主函数
main "$@"
```

---

## 错误处理

### 错误捕获

```bash
# 错误处理函数
handle_error() {
    local line_no=$1
    local error_code=$2
    log_error "Error at line $line_no: exit code $error_code"
    # 清理工作
    cleanup
    exit $error_code
}

trap 'handle_error $LINENO $?' ERR
```

### 清理函数

```bash
cleanup() {
    log_info "执行清理工作..."
    # 删除临时文件
    rm -f "$TEMP_FILE"
    # 释放资源
    # ...
}
```

---

## 日志输出

### 日志文件

```bash
# 日志文件
LOG_FILE="$LOG_DIR/etl_${dt}.log"

# 重定向输出
exec > >(tee -a "$LOG_FILE") 2>&1

# 或使用函数
run_with_log() {
    local cmd=$1
    log_info "执行: $cmd"
    eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
}
```

### 日志级别

```bash
# 日志级别控制
LOG_LEVEL=${LOG_LEVEL:-"INFO"}

log_debug() {
    [[ "$LOG_LEVEL" == "DEBUG" ]] && echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] $1"
}

log_info() {
    [[ "$LOG_LEVEL" =~ "INFO|DEBUG" ]] && echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}
```

---

## 脚本模板

### 完整模板

```bash
#!/bin/bash
#================================================================
# 脚本名称: run_etl.sh
# 功能描述: 执行 ETL 任务
# 使用方法: bash run_etl.sh <dt> [layer]
#================================================================

set -e
set -u
set -o pipefail

# 路径配置
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
LOG_DIR="$PROJECT_ROOT/logs"

# 日志函数
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
}

# 错误处理
trap 'log_error "Error at line $LINENO"; exit 1' ERR

# 主函数
main() {
    local dt=${1:-$(date -d "yesterday" +%Y-%m-%d)}
    local layer=${2:-"all"}

    log_info "========== ETL 任务开始 =========="
    log_info "参数: dt=$dt, layer=$layer"

    # 激活环境
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate dw-platform

    # 执行 ETL
    python "$PROJECT_ROOT/scripts/etl/etl.py" \
        --dt "$dt" \
        --layer "$layer"

    log_success "ETL 任务执行成功"
    log_info "========== ETL 任务结束 =========="
}

main "$@"
```

---

## 常用片段

### 检查依赖

```bash
# 检查命令是否存在
check_command() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        log_error "Command not found: $cmd"
        exit 1
    fi
}

check_command "python"
check_command "conda"
```

### 检查文件

```bash
# 检查文件存在
check_file() {
    local file=$1
    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        exit 1
    fi
}

# 检查目录存在
check_dir() {
    local dir=$1
    if [[ ! -d "$dir" ]]; then
        log_error "Directory not found: $dir"
        exit 1
    fi
}
```

### 重试机制

```bash
# 重试函数
retry() {
    local max_attempts=$1
    local delay=$2
    local cmd="${@:3}"

    local attempt=1
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Attempt $attempt: $cmd"
        if eval "$cmd"; then
            return 0
        fi
        sleep $delay
        ((attempt++))
    done

    log_error "Failed after $max_attempts attempts"
    return 1
}

# 使用
retry 3 5 "curl -f http://example.com/api"
```