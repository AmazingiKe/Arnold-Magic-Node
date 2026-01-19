import inspect
from typing import Any, Dict, Callable, Type


class DIContainer:
    """
    依赖注入容器

    职责:
    - 管理服务的注册和解析
    - 支持单例和瞬态服务
    - 自动解析依赖关系
    """

    def __init__(self):
        """
        初始化容器
        """
        self._services: Dict[str, Type] = {}
        self._factories: Dict[str, Type] = {}
        self._singletons: Dict[str, Any] = {}
        self._instances: Dict[str, Any] = {}

    def register_singleton(self, interface: Type, implementation: Type) -> None:
        """
        注册单例服务

        参数:
            interface: 接口类型
            implementation: 实现类型
        """
        interface_name = interface.__name__
        self._factories[interface_name] = implementation

    def register_transient(self, interface: Type, implementation: Type) -> None:
        """
        注册瞬态服务

        参数:
            interface: 接口类型
            implementation: 实现类型
        """
        interface_name = interface.__name__
        self._services[interface_name] = implementation

    def register_instance(self, interface: Type, instance: Any) -> None:
        """
        注册实例

        参数:
            interface: 接口类型
            instance: 实例
        """
        interface_name = interface.__name__
        self._instances[interface_name] = instance

    def resolve(self, interface: Type) -> Any:
        """
        解析服务

        参数:
            interface: 接口类型

        返回:
            服务实例
        """
        interface_name = interface.__name__

        if interface_name in self._instances:
            return self._instances[interface_name]

        if interface_name in self._factories:
            if interface_name not in self._singletons:
                self._singletons[interface_name] = self._create_instance(
                    self._factories[interface_name]
                )
            return self._singletons[interface_name]

        if interface_name in self._services:
            return self._create_instance(self._services[interface_name])

        raise ValueError(f"Service {interface_name} not registered")

    def _create_instance(self, implementation: Type) -> Any:
        """
        创建实例

        参数:
            implementation: 实现类型

        返回:
            实例
        """
        constructor = implementation.__init__
        params = inspect.signature(constructor).parameters

        kwargs = {}
        for param_name, param in params.items():
            if param_name == 'self':
                continue

            param_type = param.annotation
            if param_type and param_type != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.resolve(param_type)
                except ValueError:
                    pass

        return implementation(**kwargs)

    def is_registered(self, interface: Type) -> bool:
        """
        检查服务是否已注册

        参数:
            interface: 接口类型

        返回:
            是否已注册
        """
        interface_name = interface.__name__
        return interface_name in self._services or \
               interface_name in self._factories or \
               interface_name in self._instances

    def clear(self) -> None:
        """
        清除所有注册的服务
        """
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._instances.clear()
