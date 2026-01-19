import os
import msgpack
from typing import Dict, Any
from .i_config_repository import IConfigRepository


class ConfigRepository(IConfigRepository):
    """
    配置仓储实现

    职责:
    - 封装配置文件的读写操作
    - 提供配置验证功能
    """

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件

        参数:
            config_path: 配置文件路径

        返回:
            配置字典
        """
        if not os.path.exists(config_path):
            return {}

        try:
            with open(config_path, 'rb') as f:
                return msgpack.unpack(f, raw=False)
        except Exception as e:
            print(f"加载配置文件失败: {config_path}, 错误: {e}")
            return {}

    def save_config(self, config_path: str, config: Dict[str, Any]) -> None:
        """
        保存配置文件

        参数:
            config_path: 配置文件路径
            config: 配置字典
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'wb') as f:
                msgpack.pack(config, f, use_bin_type=True)
        except Exception as e:
            print(f"保存配置文件失败: {config_path}, 错误: {e}")
            raise

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置

        参数:
            config: 配置字典

        返回:
            是否有效
        """
        if not isinstance(config, dict):
            return False

        required_keys = ['paths']
        for key in required_keys:
            if key not in config:
                return False

        if 'paths' in config and not isinstance(config['paths'], dict):
            return False

        return True
