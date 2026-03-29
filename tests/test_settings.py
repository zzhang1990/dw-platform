"""配置模块单元测试（不依赖数据库）"""
from pathlib import Path

from config import settings


def test_base_dir_points_to_project_root() -> None:
    assert settings.BASE_DIR == Path(__file__).resolve().parent.parent
    assert (settings.BASE_DIR / "config" / "settings.py").is_file()


def test_starrocks_config_types() -> None:
    assert isinstance(settings.STARROCKS_HOST, str) and settings.STARROCKS_HOST
    assert isinstance(settings.STARROCKS_PORT, int) and settings.STARROCKS_PORT > 0
    assert isinstance(settings.STARROCKS_USER, str)
    assert isinstance(settings.STARROCKS_PASSWORD, str)
    assert isinstance(settings.STARROCKS_DATABASE, str) and settings.STARROCKS_DATABASE


def test_api_numeric_settings() -> None:
    assert isinstance(settings.API_TIMEOUT, int) and settings.API_TIMEOUT > 0
    assert isinstance(settings.API_RETRY, int) and settings.API_RETRY >= 1
