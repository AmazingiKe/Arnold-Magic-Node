from typing import Dict, List, Any
from .i_node_connection_service import INodeConnectionService
from core.i_config_manager import IConfigManager
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from data.i_node_data_repository import INodeDataRepository


class NodeConnectionService(INodeConnectionService):
    """
    节点连接服务实现

    职责:
    - 提供节点连接相关业务逻辑
    - 包括自动连接、直接连接、UV统一等功能
    """

    def __init__(
        self,
        config_manager: IConfigManager,
        logger: ILogger,
        node_data_repo: INodeDataRepository,
        event_bus: IEventBus
    ):
        """
        初始化服务

        参数:
            config_manager: 配置管理器
            logger: 日志器
            node_data_repo: 节点数据仓储
            event_bus: 事件总线
        """
        self._config = config_manager
        self._logger = logger
        self._node_repo = node_data_repo
        self._event_bus = event_bus

    def auto_connect_nodes(self, material_name: str, texture_nodes: List[str],
                          options: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动连接节点

        参数:
            material_name: 材质名称
            texture_nodes: 贴图节点列表
            options: 连接选项

        返回:
            连接结果
        """
        self._logger.info("开始自动连接节点", material=material_name,
                         texture_count=len(texture_nodes), options=options)

        result = {
            'connected_count': 0,
            'failed_count': 0,
            'connections': []
        }

        channel_map = self._generate_channel_map(texture_nodes, options)

        for texture_node, channel in channel_map.items():
            try:
                self._connect_texture_to_material(material_name, texture_node, channel)
                result['connected_count'] += 1
                result['connections'].append({
                    'texture': texture_node,
                    'channel': channel
                })
                self._logger.info(f"连接成功: {texture_node} -> {channel}")
            except Exception as e:
                self._logger.error(f"连接失败: {texture_node}", error=str(e))
                result['failed_count'] += 1

        self._event_bus.publish('nodes.connected', result)
        self._logger.info("自动连接节点完成", result=result)

        return result

    def _generate_channel_map(self, texture_nodes: List[str],
                            options: Dict[str, Any]) -> Dict[str, str]:
        """
        生成通道映射

        参数:
            texture_nodes: 贴图节点列表
            options: 连接选项

        返回:
            通道映射字典，格式为 {贴图节点名: 通道名}
        """
        channel_map = {}
        default_channels = ['color', 'specular', 'roughness', 'normal', 'bump']

        for i, texture_node in enumerate(texture_nodes):
            channel = options.get(f'channel_{i}', default_channels[i] if i < len(default_channels) else 'color')
            channel_map[texture_node] = channel

        return channel_map

    def _connect_texture_to_material(self, material_name: str, texture_node: str, channel: str) -> None:
        """
        将贴图连接到材质

        参数:
            material_name: 材质名称
            texture_node: 贴图节点名称
            channel: 通道名称
        """
        try:
            import maya.cmds as cmds

            cmds.connect(f"{texture_node}.outColor", f"{material_name}.{channel}")
        except Exception as e:
            raise RuntimeError(f"连接节点失败: {texture_node} -> {material_name}.{channel}, 错误: {e}")

    def direct_connect_nodes(self, material_name: str, texture_nodes: List[str],
                            channel_map: Dict[str, str]) -> bool:
        """
        直接连接节点

        参数:
            material_name: 材质名称
            texture_nodes: 贴图节点列表
            channel_map: 通道映射

        返回:
            是否成功
        """
        self._logger.info("开始直接连接节点", material=material_name,
                         texture_count=len(texture_nodes))

        try:
            for texture_node in texture_nodes:
                channel = channel_map.get(texture_node, 'color')
                self._connect_texture_to_material(material_name, texture_node, channel)

            self._event_bus.publish('nodes.connected', {
                'material': material_name,
                'texture_count': len(texture_nodes)
            })

            self._logger.info("直接连接节点完成", material=material_name)
            return True

        except Exception as e:
            self._logger.error("直接连接节点失败", error=str(e))
            return False

    def unify_uv_nodes(self, texture_nodes: List[str]) -> bool:
        """
        统一UV节点

        参数:
            texture_nodes: 贴图节点列表

        返回:
            是否成功
        """
        self._logger.info("开始统一UV节点", texture_count=len(texture_nodes))

        try:
            import maya.cmds as cmds

            uv_node = None
            for texture_node in texture_nodes:
                connections = cmds.listConnections(texture_node, source=True, destination=False, plugs=True)

                for conn in connections:
                    if '.uvCoord' in conn:
                        uv_node = conn.split('.')[0]
                        break

                if uv_node:
                    break

            if not uv_node:
                self._logger.warning("未找到UV节点")
                return False

            for texture_node in texture_nodes:
                try:
                    cmds.connect(f"{uv_node}.outUV", f"{texture_node}.uvCoord")
                    self._logger.info(f"统一UV: {texture_node}")
                except Exception as e:
                    self._logger.error(f"统一UV失败: {texture_node}", error=str(e))

            self._event_bus.publish('uv.unified', {
                'uv_node': uv_node,
                'texture_count': len(texture_nodes)
            })

            self._logger.info("统一UV节点完成", uv_node=uv_node)
            return True

        except Exception as e:
            self._logger.error("统一UV节点失败", error=str(e))
            return False

    def set_color_space(self, texture_nodes: List[str], color_space: str) -> bool:
        """
        设置色彩空间

        参数:
            texture_nodes: 贴图节点列表
            color_space: 色彩空间

        返回:
            是否成功
        """
        self._logger.info("开始设置色彩空间", texture_count=len(texture_nodes), color_space=color_space)

        try:
            import maya.cmds as cmds

            for texture_node in texture_nodes:
                try:
                    cmds.setAttr(f"{texture_node}.colorSpace", color_space)
                    self._logger.info(f"设置色彩空间: {texture_node}", color_space=color_space)
                except Exception as e:
                    self._logger.error(f"设置色彩空间失败: {texture_node}", error=str(e))

            self._event_bus.publish('color_space.set', {
                'texture_count': len(texture_nodes),
                'color_space': color_space
            })

            self._logger.info("设置色彩空间完成", color_space=color_space)
            return True

        except Exception as e:
            self._logger.error("设置色彩空间失败", error=str(e))
            return False

    def set_udim_mode(self, texture_nodes: List[str]) -> bool:
        """
        设置UDIM模式

        参数:
            texture_nodes: 贴图节点列表

        返回:
            是否成功
        """
        self._logger.info("开始设置UDIM模式", texture_count=len(texture_nodes))

        try:
            import maya.cmds as cmds

            for texture_node in texture_nodes:
                try:
                    texture_path = self._node_repo.get_node_attribute(texture_node, 'fileTextureName')

                    if '<UDIM>' in texture_path:
                        cmds.setAttr(f"{texture_node}.uvTilingMode", 3)
                        self._logger.info(f"设置UDIM模式: {texture_node}")
                    else:
                        cmds.setAttr(f"{texture_node}.uvTilingMode", 0)
                        self._logger.info(f"关闭UDIM模式: {texture_node}")

                except Exception as e:
                    self._logger.error(f"设置UDIM模式失败: {texture_node}", error=str(e))

            self._event_bus.publish('udim.set', {
                'texture_count': len(texture_nodes)
            })

            self._logger.info("设置UDIM模式完成")
            return True

        except Exception as e:
            self._logger.error("设置UDIM模式失败", error=str(e))
            return False
