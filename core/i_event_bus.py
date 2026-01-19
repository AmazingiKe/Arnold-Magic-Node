from abc import ABC, abstractmethod
from typing import Callable, Any, Optional


class IEventBus(ABC):
    """
    事件总线接口

    职责:
    - 提供事件发布订阅机制
    - 支持事件的异步处理
    - 解耦模块间的通信
    """

    @abstractmethod
    def subscribe(self, event_name: str, callback: Callable) -> str:
        """
        订阅事件

        参数:
            event_name: 事件名称
            callback: 回调函数

        返回:
            订阅ID，用于取消订阅
        """
        pass

    @abstractmethod
    def unsubscribe(self, event_name: str, callback_id: str) -> bool:
        """
        取消订阅

        参数:
            event_name: 事件名称
            callback_id: 订阅ID

        返回:
            是否成功取消订阅
        """
        pass

    @abstractmethod
    def publish(self, event_name: str, data: Any = None) -> None:
        """
        发布事件

        参数:
            event_name: 事件名称
            data: 事件数据
        """
        pass

    @abstractmethod
    def clear(self, event_name: Optional[str] = None) -> None:
        """
        清除事件订阅

        参数:
            event_name: 事件名称，如果为None则清除所有订阅
        """
        pass
