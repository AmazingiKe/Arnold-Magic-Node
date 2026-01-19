from typing import Callable, Any, Optional, Dict, List
from .i_event_bus import IEventBus


class EventBus(IEventBus):
    """
    事件总线实现

    职责:
    - 提供事件发布订阅机制
    - 支持事件的异步处理
    - 解耦模块间的通信
    """

    def __init__(self):
        """
        初始化事件总线
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._callback_id_counter = 0
        self._callback_ids: Dict[str, Callable] = {}

    def subscribe(self, event_name: str, callback: Callable) -> str:
        """
        订阅事件

        参数:
            event_name: 事件名称
            callback: 回调函数

        返回:
            订阅ID，用于取消订阅
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []

        callback_id = f"{event_name}_{self._callback_id_counter}"
        self._callback_id_counter += 1

        self._subscribers[event_name].append(callback)
        self._callback_ids[callback_id] = callback

        return callback_id

    def unsubscribe(self, event_name: str, callback_id: str) -> bool:
        """
        取消订阅

        参数:
            event_name: 事件名称
            callback_id: 订阅ID

        返回:
            是否成功取消订阅
        """
        if event_name not in self._subscribers:
            return False

        callback = self._callback_ids.get(callback_id)
        if callback and callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)
            del self._callback_ids[callback_id]
            return True

        return False

    def publish(self, event_name: str, data: Any = None) -> None:
        """
        发布事件

        参数:
            event_name: 事件名称
            data: 事件数据
        """
        if event_name not in self._subscribers:
            return

        for callback in self._subscribers[event_name]:
            try:
                callback(data)
            except Exception as e:
                print(f"事件处理失败: {event_name}, 错误: {e}")

    def clear(self, event_name: Optional[str] = None) -> None:
        """
        清除事件订阅

        参数:
            event_name: 事件名称，如果为None则清除所有订阅
        """
        if event_name:
            if event_name in self._subscribers:
                del self._subscribers[event_name]
        else:
            self._subscribers.clear()
            self._callback_ids.clear()
