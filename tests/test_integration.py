import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service_config import configure_services
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from data.i_config_repository import IConfigRepository
from data.i_node_data_repository import INodeDataRepository
from data.i_file_system_repository import IFileSystemRepository
from services.texture_manager.i_texture_manager_service import ITextureManagerService
from services.node_connection.i_node_connection_service import INodeConnectionService


class TestIntegration:
    """集成测试"""

    @pytest.fixture
    def container(self):
        """创建配置好的容器"""
        return configure_services()

    def test_container_configuration(self, container):
        """测试容器配置"""
        assert container.is_registered(IConfigManager)
        assert container.is_registered(ILogger)
        assert container.is_registered(IEventBus)
        assert container.is_registered(IConfigRepository)
        assert container.is_registered(INodeDataRepository)
        assert container.is_registered(IFileSystemRepository)
        assert container.is_registered(ITextureManagerService)
        assert container.is_registered(INodeConnectionService)

    def test_service_resolution(self, container):
        """测试服务解析"""
        config = container.resolve(IConfigManager)
        logger = container.resolve(ILogger)
        event_bus = container.resolve(IEventBus)
        config_repo = container.resolve(IConfigRepository)
        node_repo = container.resolve(INodeDataRepository)
        file_repo = container.resolve(IFileSystemRepository)
        texture_service = container.resolve(ITextureManagerService)
        node_service = container.resolve(INodeConnectionService)

        assert config is not None
        assert logger is not None
        assert event_bus is not None
        assert config_repo is not None
        assert node_repo is not None
        assert file_repo is not None
        assert texture_service is not None
        assert node_service is not None

    def test_singleton_services(self, container):
        """测试单例服务"""
        config1 = container.resolve(IConfigManager)
        config2 = container.resolve(IConfigManager)

        assert config1 is config2

        logger1 = container.resolve(ILogger)
        logger2 = container.resolve(ILogger)

        assert logger1 is logger2

    def test_transient_services(self, container):
        """测试瞬态服务"""
        service1 = container.resolve(ITextureManagerService)
        service2 = container.resolve(ITextureManagerService)

        assert service1 is not service2

    def test_event_bus_integration(self, container):
        """测试事件总线集成"""
        event_bus = container.resolve(IEventBus)
        texture_service = container.resolve(ITextureManagerService)

        received_events = []

        def on_textures_fixed(data):
            received_events.append(('textures.fixed', data))

        event_bus.subscribe('textures.fixed', on_textures_fixed)

        event_bus.publish('test_event', {'key': 'value'})
        assert len(received_events) == 0

        event_bus.publish('textures.fixed', {'fixed_count': 5})
        assert len(received_events) == 1
        assert received_events[0][0] == 'textures.fixed'
        assert received_events[0][1]['fixed_count'] == 5

    def test_service_dependencies(self, container):
        """测试服务依赖"""
        texture_service = container.resolve(ITextureManagerService)
        node_service = container.resolve(INodeConnectionService)

        assert texture_service._config is not None
        assert texture_service._logger is not None
        assert texture_service._node_repo is not None
        assert texture_service._file_repo is not None
        assert texture_service._event_bus is not None

        assert node_service._config is not None
        assert node_service._logger is not None
        assert node_service._node_repo is not None
        assert node_service._event_bus is not None

    def test_config_manager_integration(self, container):
        """测试配置管理器集成"""
        config = container.resolve(IConfigManager)

        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'

        config.set_nested(['level1', 'level2', 'key'], 'nested_value')
        assert config.get_nested(['level1', 'level2', 'key']) == 'nested_value'

    def test_file_system_repository_integration(self, container):
        """测试文件系统仓储集成"""
        file_repo = container.resolve(IFileSystemRepository)
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test.txt')
            with open(test_file, 'w') as f:
                f.write('test content')

            assert file_repo.file_exists(test_file) == True

            file_info = file_repo.get_file_info(test_file)
            assert 'size' in file_info
            assert 'extension' in file_info
            assert file_info['extension'] == '.txt'

    def test_config_repository_integration(self, container):
        """测试配置仓储集成"""
        config_repo = container.resolve(IConfigRepository)
        import tempfile

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
            temp_path = f.name

        test_config = {
            'paths': {
                'script_path': '/test/path'
            },
            'key1': 'value1',
            'key2': {'nested': 'value2'}
        }

        config_repo.save_config(temp_path, test_config)
        loaded_config = config_repo.load_config(temp_path)

        assert loaded_config == test_config

        assert config_repo.validate_config(test_config) == True
        assert config_repo.validate_config({'invalid': 'config'}) == False

    def test_texture_service_workflow(self, container):
        """测试贴图服务工作流"""
        from unittest.mock import patch

        texture_service = container.resolve(ITextureManagerService)

        with patch.object(texture_service._node_repo, 'get_all_textures', return_value={}):
            all_textures = texture_service.get_all_textures()
            assert isinstance(all_textures, dict)

        with patch.object(texture_service._node_repo, 'get_all_textures', return_value={}):
            filtered = texture_service.filter_textures({})
            assert isinstance(filtered, dict)

        with patch.object(texture_service._node_repo, 'get_all_textures', return_value={}), \
             patch.object(texture_service._file_repo, 'search_files', return_value={}):
            result = texture_service.fix_missing_textures('/nonexistent/path', {})
            assert 'fixed_count' in result
            assert 'failed_count' in result
            assert 'matched' in result

    def test_node_service_workflow(self, container):
        """测试节点连接服务工作流"""
        node_service = container.resolve(INodeConnectionService)

        result = node_service.auto_connect_nodes('test_material', [], {})
        assert 'connected_count' in result
        assert 'failed_count' in result
        assert 'connections' in result

        channel_map = {'texture1': 'color'}
        result = node_service.direct_connect_nodes('test_material', ['texture1'], channel_map)
        assert isinstance(result, bool)

        result = node_service.set_color_space(['texture1'], 'sRGB')
        assert isinstance(result, bool)

        result = node_service.set_udim_mode(['texture1'])
        assert isinstance(result, bool)
