from core.di_container import DIContainer
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from data.i_config_repository import IConfigRepository
from data.i_node_data_repository import INodeDataRepository
from data.i_file_system_repository import IFileSystemRepository
from services.texture_manager.i_texture_manager_service import ITextureManagerService
from services.node_connection.i_node_connection_service import INodeConnectionService

from core.config_manager import ConfigManager
from core.logger import ConsoleLogger
from core.event_bus import EventBus
from data.config_repository import ConfigRepository
from data.node_data_repository import NodeDataRepository
from data.file_system_repository import FileSystemRepository
from services.texture_manager.texture_manager_service import TextureManagerService
from services.node_connection.node_connection_service import NodeConnectionService


def configure_services() -> DIContainer:
    """
    配置所有服务

    返回:
        配置好的依赖注入容器
    """
    container = DIContainer()

    container.register_singleton(ILogger, ConsoleLogger)
    container.register_singleton(IEventBus, EventBus)
    container.register_singleton(IConfigRepository, ConfigRepository)
    container.register_singleton(IConfigManager, ConfigManager)
    container.register_singleton(INodeDataRepository, NodeDataRepository)
    container.register_singleton(IFileSystemRepository, FileSystemRepository)

    container.register_transient(ITextureManagerService, TextureManagerService)
    container.register_transient(INodeConnectionService, NodeConnectionService)

    return container


def get_container() -> DIContainer:
    """
    获取全局容器实例

    返回:
        依赖注入容器实例
    """
    if not hasattr(get_container, '_container'):
        get_container._container = configure_services()

    return get_container._container
