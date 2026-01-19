import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.config_repository import ConfigRepository
from data.i_config_repository import IConfigRepository


class TestConfigRepository:
    """配置仓储测试"""

    @pytest.fixture
    def config_repo(self):
        """创建配置仓储"""
        return ConfigRepository()

    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
            temp_path = f.name
        yield temp_path
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_load_nonexistent_config(self, config_repo):
        """测试加载不存在的配置文件"""
        result = config_repo.load_config("nonexistent.bin")
        assert result == {}

    def test_save_and_load_config(self, config_repo, temp_config_file):
        """测试保存和加载配置"""
        test_config = {
            "key1": "value1",
            "key2": {"nested": "value2"},
            "paths": {
                "script_path": "/test/path"
            }
        }

        config_repo.save_config(temp_config_file, test_config)
        loaded_config = config_repo.load_config(temp_config_file)

        assert loaded_config == test_config

    def test_validate_valid_config(self, config_repo):
        """测试验证有效配置"""
        valid_config = {
            "paths": {
                "script_path": "/test/path"
            }
        }
        assert config_repo.validate_config(valid_config) == True

    def test_validate_invalid_config_no_dict(self, config_repo):
        """测试验证无效配置（非字典）"""
        invalid_config = "not a dict"
        assert config_repo.validate_config(invalid_config) == False

    def test_validate_invalid_config_missing_paths(self, config_repo):
        """测试验证无效配置（缺少paths）"""
        invalid_config = {
            "other_key": "value"
        }
        assert config_repo.validate_config(invalid_config) == False

    def test_validate_invalid_config_paths_not_dict(self, config_repo):
        """测试验证无效配置（paths不是字典）"""
        invalid_config = {
            "paths": "not a dict"
        }
        assert config_repo.validate_config(invalid_config) == False
