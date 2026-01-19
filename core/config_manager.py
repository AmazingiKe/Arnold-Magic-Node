import os
from typing import Any, Dict, List
from .i_config_manager import IConfigManager
from data.i_config_repository import IConfigRepository


class ConfigManager(IConfigManager):
    """
    配置管理器实现

    职责:
    - 管理应用配置
    - 支持配置的读写和重新加载
    - 提供嵌套配置访问
    """

    def __init__(self, config_repository: IConfigRepository = None, config_path: str = None):
        """
        初始化配置管理器

        参数:
            config_repository: 配置仓储
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_repository is None:
            from data.config_repository import ConfigRepository
            config_repository = ConfigRepository()

        self._repo = config_repository
        self._config: Dict[str, Any] = {}
        self._config_path = config_path or self._get_default_config_path()
        self._load_config()

    def _get_default_config_path(self) -> str:
        """
        获取默认配置文件路径

        返回:
            配置文件路径
        """
        script_path = os.path.dirname(os.path.abspath(__file__))
        datas_path = os.path.join(script_path, '..', 'Datas')
        settings_path = os.path.join(datas_path, 'settings')
        return os.path.join(settings_path, 'Arnold_Magic_Settings.bin')

    def _load_config(self) -> None:
        """
        加载配置
        """
        try:
            if os.path.exists(self._config_path):
                self._config = self._repo.load_config(self._config_path)
            else:
                self._config = self._get_default_config()
        except Exception as e:
            print(f"加载配置失败: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        返回:
            默认配置字典
        """
        return {
            'paths': {
                'script_path': os.path.dirname(os.path.abspath(__file__)),
                'datas_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Datas'),
                'settings_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Datas', 'settings'),
                'icon_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon'),
                'render_preset_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Datas', 'render_presets')
            },
            'language': 'zh_CN',
            'version': '1.0.0'
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        参数:
            key: 配置键
            default: 默认值

        返回:
            配置值
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        参数:
            key: 配置键
            value: 配置值
        """
        self._config[key] = value

    def get_nested(self, key_path: List[str], default: Any = None) -> Any:
        """
        获取嵌套配置值

        参数:
            key_path: 配置键路径，如 ['level1', 'level2', 'key']
            default: 默认值

        返回:
            配置值
        """
        current = self._config
        for key in key_path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def set_nested(self, key_path: List[str], value: Any) -> None:
        """
        设置嵌套配置值

        参数:
            key_path: 配置键路径，如 ['level1', 'level2', 'key']
            value: 配置值
        """
        current = self._config
        for key in key_path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[key_path[-1]] = value

    def reload(self) -> None:
        """
        重新加载配置
        """
        self._load_config()

    def save(self) -> None:
        """
        保存配置
        """
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            self._repo.save_config(self._config_path, self._config)
        except Exception as e:
            print(f"保存配置失败: {e}")
