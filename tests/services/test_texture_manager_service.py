import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.texture_manager.texture_manager_service import TextureManagerService
from services.texture_manager.i_texture_manager_service import ITextureManagerService
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from data.i_node_data_repository import INodeDataRepository
from data.i_file_system_repository import IFileSystemRepository


class TestTextureManagerService:
    """贴图管理服务测试"""

    @pytest.fixture
    def container(self):
        """创建依赖注入容器"""
        from core.di_container import DIContainer
        container = DIContainer()

        container.register_singleton(IConfigManager, Mock())
        container.register_singleton(ILogger, Mock())
        container.register_singleton(IEventBus, Mock())
        container.register_singleton(INodeDataRepository, Mock())
        container.register_singleton(IFileSystemRepository, Mock())

        return container

    @pytest.fixture
    def service(self, container):
        """创建服务实例"""
        return TextureManagerService(
            container.resolve(IConfigManager),
            container.resolve(ILogger),
            container.resolve(INodeDataRepository),
            container.resolve(IFileSystemRepository),
            container.resolve(IEventBus)
        )

    def test_get_all_textures(self, service, container):
        """测试获取所有贴图"""
        node_repo = container.resolve(INodeDataRepository)
        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/path/to/texture1.jpg", "isLoaded": True}
            }
        }

        result = service.get_all_textures()

        assert "material1" in result
        assert "texture1" in result["material1"]
        node_repo.get_all_textures.assert_called_once()

    def test_filter_textures(self, service, container):
        """测试过滤贴图"""
        node_repo = container.resolve(INodeDataRepository)
        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/path/to/texture1.jpg", "isLoaded": False},
                "texture2": {"Path": "/path/to/texture2.jpg", "isLoaded": True}
            }
        }

        result = service.filter_textures({"isLoaded": False})

        assert "material1" in result
        assert "texture1" in result["material1"]
        assert "texture2" not in result["material1"]

    def test_fix_missing_textures_no_missing(self, service, container):
        """测试修复缺失贴图（无缺失）"""
        node_repo = container.resolve(INodeDataRepository)
        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/path/to/texture1.jpg", "isLoaded": True}
            }
        }

        result = service.fix_missing_textures("/search/path", {})

        assert result["fixed_count"] == 0
        assert result["failed_count"] == 0

    def test_fix_missing_textures_with_matches(self, service, container):
        """测试修复缺失贴图（有匹配）"""
        node_repo = container.resolve(INodeDataRepository)
        file_repo = container.resolve(IFileSystemRepository)

        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/old/path/texture1.jpg", "isLoaded": False}
            }
        }

        file_repo.search_files.return_value = {
            "texture1.jpg": "/new/path/texture1.jpg"
        }

        result = service.fix_missing_textures("/search/path", {})

        assert result["fixed_count"] == 1
        assert result["failed_count"] == 0
        node_repo.set_texture_path.assert_called_once()

    def test_process_images(self, service, container):
        """测试批量处理图像"""
        node_repo = container.resolve(INodeDataRepository)
        file_repo = container.resolve(IFileSystemRepository)

        node_repo.get_node_attribute.return_value = "/path/to/texture.jpg"
        file_repo.file_exists.return_value = True

        result = service.process_images(["texture1"], {"format": "jpg"})

        assert result["processed_count"] == 1
        assert result["failed_count"] == 0

    def test_pack_textures(self, service, container):
        """测试打包贴图"""
        node_repo = container.resolve(INodeDataRepository)
        file_repo = container.resolve(IFileSystemRepository)

        node_repo.get_node_attribute.return_value = "/path/to/texture.jpg"
        file_repo.file_exists.return_value = True

        with patch('zipfile.ZipFile') as mock_zipfile:
            result = service.pack_textures(["texture1"], "/output.zip", {})

            assert result == True
