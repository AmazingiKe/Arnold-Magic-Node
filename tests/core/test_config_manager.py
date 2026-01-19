import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.config_manager import ConfigManager
from core.i_config_manager import IConfigManager
from data.i_config_repository import IConfigRepository


class TestConfigManager:
    """配置管理器测试"""

    @pytest.fixture
    def config_repo(self):
        """创建配置仓储mock"""
        return Mock(spec=IConfigRepository)

    @pytest.fixture
    def config_manager(self, config_repo):
        """创建配置管理器"""
        return ConfigManager(config_repo)

    def test_get_config_value(self, config_manager, config_repo):
        """测试获取配置值"""
        config_manager._config = {"key": "value"}
        result = config_manager.get("key")
        assert result == "value"

    def test_get_config_value_with_default(self, config_manager):
        """测试获取配置值（使用默认值）"""
        result = config_manager.get("nonexistent_key", default="default")
        assert result == "default"

    def test_set_config_value(self, config_manager):
        """测试设置配置值"""
        config_manager.set("key", "value")
        assert config_manager.get("key") == "value"

    def test_get_nested_config(self, config_manager):
        """测试获取嵌套配置"""
        config_manager._config = {
            "level1": {
                "level2": {
                    "key": "value"
                }
            }
        }
        result = config_manager.get_nested(["level1", "level2", "key"])
        assert result == "value"

    def test_get_nested_config_default(self, config_manager):
        """测试获取嵌套配置（使用默认值）"""
        config_manager._config = {"level1": {}}
        result = config_manager.get_nested(["level1", "level2", "key"], default="default")
        assert result == "default"

    def test_set_nested_config(self, config_manager):
        """测试设置嵌套配置"""
        config_manager._config = {}
        config_manager.set_nested(["level1", "level2", "key"], "value")
        assert config_manager.get_nested(["level1", "level2", "key"]) == "value"

    def test_reload_config(self, config_manager, config_repo):
        """测试重新加载配置"""
        config_repo.load_config.return_value = {"reloaded": True}
        with patch('os.path.exists', return_value=True):
            config_manager.reload()
        assert config_manager.get("reloaded") == True

    def test_save_config(self, config_manager, config_repo):
        """测试保存配置"""
        config_manager._config = {"key": "value"}
        config_manager.save()
        config_repo.save_config.assert_called_once()

    def test_default_config_structure(self, config_manager):
        """测试默认配置结构"""
        assert "paths" in config_manager._config
        assert "script_path" in config_manager._config["paths"]
        assert "datas_path" in config_manager._config["paths"]
        assert "settings_path" in config_manager._config["paths"]
        assert "icon_path" in config_manager._config["paths"]
        assert "render_preset_path" in config_manager._config["paths"]
