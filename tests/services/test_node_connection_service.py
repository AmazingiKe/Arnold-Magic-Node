import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.node_connection.node_connection_service import NodeConnectionService
from services.node_connection.i_node_connection_service import INodeConnectionService
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from data.i_node_data_repository import INodeDataRepository


class TestNodeConnectionService:
    """节点连接服务测试"""

    @pytest.fixture
    def container(self):
        """创建依赖注入容器"""
        from core.di_container import DIContainer
        container = DIContainer()

        container.register_singleton(IConfigManager, Mock())
        container.register_singleton(ILogger, Mock())
        container.register_singleton(IEventBus, Mock())
        container.register_singleton(INodeDataRepository, Mock())

        return container

    @pytest.fixture
    def service(self, container):
        """创建服务实例"""
        return NodeConnectionService(
            container.resolve(IConfigManager),
            container.resolve(ILogger),
            container.resolve(INodeDataRepository),
            container.resolve(IEventBus)
        )

    def test_auto_connect_nodes(self, service, container):
        """测试自动连接节点"""
        result = service.auto_connect_nodes("material1", ["texture1"], {})

        assert "connected_count" in result
        assert "failed_count" in result
        assert "connections" in result

    def test_direct_connect_nodes(self, service, container):
        """测试直接连接节点"""
        channel_map = {"texture1": "color"}

        with patch.object(service, '_connect_texture_to_material'):
            result = service.direct_connect_nodes("material1", ["texture1"], channel_map)

            assert result == True

    def test_unify_uv_nodes_no_uv(self, service, container):
        """测试统一UV节点（无UV）"""
        node_repo = container.resolve(INodeDataRepository)
        node_repo.listConnections = Mock(return_value=[])

        result = service.unify_uv_nodes(["texture1"])

        assert result == False

    def test_set_color_space(self, service, container):
        """测试设置色彩空间"""
        with patch.object(service, '_connect_texture_to_material'):
            result = service.set_color_space(["texture1"], "sRGB")

            assert result == True

    def test_set_udim_mode_with_udim(self, service, container):
        """测试设置UDIM模式（有UDIM）"""
        node_repo = container.resolve(INodeDataRepository)
        node_repo.get_node_attribute.return_value = "/path/texture_<UDIM>.jpg"

        with patch.object(service, '_connect_texture_to_material'):
            result = service.set_udim_mode(["texture1"])

            assert result == True

    def test_set_udim_mode_without_udim(self, service, container):
        """测试设置UDIM模式（无UDIM）"""
        node_repo = container.resolve(INodeDataRepository)
        node_repo.get_node_attribute.return_value = "/path/texture.jpg"

        with patch.object(service, '_connect_texture_to_material'):
            result = service.set_udim_mode(["texture1"])

            assert result == True
