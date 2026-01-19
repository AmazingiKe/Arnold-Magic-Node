"""
Arnold Magic Node 解耦架构使用示例

本示例展示了如何使用解耦后的架构进行开发
"""

from service_config import get_container
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from services.texture_manager.i_texture_manager_service import ITextureManagerService
from services.node_connection.i_node_connection_service import INodeConnectionService
from core.config_manager import ConfigManager


def example_basic_usage():
    """示例1：基本使用"""
    print("=== 示例1：基本使用 ===")

    container = get_container()

    config = container.resolve(IConfigManager)
    logger = container.resolve(ILogger)

    logger.info("应用启动")

    config.set('user_name', 'Arnold')
    user_name = config.get('user_name')

    logger.info(f"用户名: {user_name}")


def example_texture_management():
    """示例2：贴图管理"""
    print("\n=== 示例2：贴图管理 ===")

    container = get_container()
    texture_service = container.resolve(ITextureManagerService)
    logger = container.resolve(ILogger)

    logger.info("获取所有贴图")

    try:
        all_textures = texture_service.get_all_textures()
        logger.info(f"找到 {len(all_textures)} 个材质")

        for material_name, texture_dict in all_textures.items():
            logger.info(f"材质: {material_name}, 贴图数: {len(texture_dict)}")
    except Exception as e:
        logger.warning(f"Maya环境不可用，跳过贴图管理示例: {e}")
        print("⚠ Maya环境不可用，此示例需要Maya环境")


def example_event_subscription():
    """示例3：事件订阅"""
    print("\n=== 示例3：事件订阅 ===")

    container = get_container()
    event_bus = container.resolve(IEventBus)
    logger = container.resolve(ILogger)

    def on_textures_fixed(data):
        logger.info("贴图修复完成", data=data)
        print(f"✓ 修复了 {data['fixed_count']} 个贴图")

    def on_nodes_connected(data):
        logger.info("节点连接完成", data=data)
        print(f"✓ 连接了 {data['connected_count']} 个节点")

    event_bus.subscribe('textures.fixed', on_textures_fixed)
    event_bus.subscribe('nodes.connected', on_nodes_connected)

    logger.info("已订阅事件")

    event_bus.publish('textures.fixed', {'fixed_count': 5, 'failed_count': 0})
    event_bus.publish('nodes.connected', {'connected_count': 3, 'failed_count': 0})


def example_service_collaboration():
    """示例4：服务协作"""
    print("\n=== 示例4：服务协作 ===")

    container = get_container()
    texture_service = container.resolve(ITextureManagerService)
    node_service = container.resolve(INodeConnectionService)
    logger = container.resolve(ILogger)

    logger.info("服务协作示例")

    try:
        textures = texture_service.get_all_textures()

        for material_name, texture_data in textures.items():
            texture_nodes = list(texture_data.keys())

            if texture_nodes:
                logger.info(f"处理材质: {material_name}")

                result = node_service.auto_connect_nodes(
                    material_name,
                    texture_nodes,
                    {}
                )

                logger.info(f"连接结果: {result['connected_count']} 成功, {result['failed_count']} 失败")
    except Exception as e:
        logger.warning(f"Maya环境不可用，跳过服务协作示例: {e}")
        print("⚠ Maya环境不可用，此示例需要Maya环境")


def example_dependency_injection():
    """示例5：依赖注入"""
    print("\n=== 示例5：依赖注入 ===")

    from core.di_container import DIContainer
    from core.i_config_manager import IConfigManager
    from core.logger import ConsoleLogger

    container = DIContainer()

    container.register_singleton(IConfigManager, ConfigManager)
    container.register_singleton(ILogger, ConsoleLogger)

    config = container.resolve(IConfigManager)
    logger = container.resolve(ILogger)

    logger.info("依赖注入示例")


def example_singleton_vs_transient():
    """示例6：单例 vs 瞬态"""
    print("\n=== 示例6：单例 vs 瞬态 ===")

    container = get_container()

    config1 = container.resolve(IConfigManager)
    config2 = container.resolve(IConfigManager)

    print(f"单例服务: {config1 is config2}")

    service1 = container.resolve(ITextureManagerService)
    service2 = container.resolve(ITextureManagerService)

    print(f"瞬态服务: {service1 is not service2}")


def main():
    """主函数"""
    print("Arnold Magic Node 解耦架构使用示例\n")

    example_basic_usage()
    example_texture_management()
    example_event_subscription()
    example_service_collaboration()
    example_dependency_injection()
    example_singleton_vs_transient()

    print("\n=== 所有示例运行完成 ===")


if __name__ == "__main__":
    main()
