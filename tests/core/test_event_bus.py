import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.event_bus import EventBus
from core.i_event_bus import IEventBus


class TestEventBus:
    """事件总线测试"""

    @pytest.fixture
    def event_bus(self):
        """创建事件总线"""
        return EventBus()

    def test_subscribe_and_publish(self, event_bus):
        """测试订阅和发布事件"""
        received = []

        def callback(data):
            received.append(data)

        event_bus.subscribe("test_event", callback)
        event_bus.publish("test_event", {"key": "value"})

        assert len(received) == 1
        assert received[0] == {"key": "value"}

    def test_subscribe_returns_id(self, event_bus):
        """测试订阅返回ID"""
        def callback(data):
            pass

        callback_id = event_bus.subscribe("test_event", callback)
        assert callback_id is not None
        assert "test_event" in callback_id

    def test_unsubscribe(self, event_bus):
        """测试取消订阅"""
        received = []

        def callback(data):
            received.append(data)

        callback_id = event_bus.subscribe("test_event", callback)
        event_bus.unsubscribe("test_event", callback_id)
        event_bus.publish("test_event", {"key": "value"})

        assert len(received) == 0

    def test_multiple_subscribers(self, event_bus):
        """测试多个订阅者"""
        received1 = []
        received2 = []

        def callback1(data):
            received1.append(data)

        def callback2(data):
            received2.append(data)

        event_bus.subscribe("test_event", callback1)
        event_bus.subscribe("test_event", callback2)
        event_bus.publish("test_event", {"key": "value"})

        assert len(received1) == 1
        assert len(received2) == 1

    def test_publish_nonexistent_event(self, event_bus):
        """测试发布不存在的事件"""
        event_bus.publish("nonexistent_event", {"key": "value"})
        assert True  # Should not raise exception

    def test_clear_event(self, event_bus):
        """测试清除事件"""
        received = []

        def callback(data):
            received.append(data)

        event_bus.subscribe("test_event", callback)
        event_bus.clear("test_event")
        event_bus.publish("test_event", {"key": "value"})

        assert len(received) == 0

    def test_clear_all_events(self, event_bus):
        """测试清除所有事件"""
        received1 = []
        received2 = []

        def callback1(data):
            received1.append(data)

        def callback2(data):
            received2.append(data)

        event_bus.subscribe("event1", callback1)
        event_bus.subscribe("event2", callback2)
        event_bus.clear()
        event_bus.publish("event1", {"key": "value"})
        event_bus.publish("event2", {"key": "value"})

        assert len(received1) == 0
        assert len(received2) == 0

    def test_callback_exception_handling(self, event_bus):
        """测试回调异常处理"""
        received = []

        def callback_with_error(data):
            raise Exception("Test error")

        def callback_normal(data):
            received.append(data)

        event_bus.subscribe("test_event", callback_with_error)
        event_bus.subscribe("test_event", callback_normal)
        event_bus.publish("test_event", {"key": "value"})

        assert len(received) == 1  # Normal callback should still be called
