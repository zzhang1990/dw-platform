"""配置模块"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库配置
STARROCKS_HOST = os.getenv("STARROCKS_HOST", "localhost")
STARROCKS_PORT = int(os.getenv("STARROCKS_PORT", "9030"))
STARROCKS_USER = os.getenv("STARROCKS_USER", "root")
STARROCKS_PASSWORD = os.getenv("STARROCKS_PASSWORD", "")
STARROCKS_DATABASE = os.getenv("STARROCKS_DATABASE", "dw")

# API 配置
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
API_RETRY = int(os.getenv("API_RETRY", "3"))