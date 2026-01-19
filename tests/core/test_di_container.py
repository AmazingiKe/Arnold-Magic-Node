import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.di_container import DIContainer
from core.i_logger import ILogger
from core.i_event_bus import IEventBus
from core.logger import ConsoleLogger
from core.event_bus import EventBus


class MockService:
    """Mock服务"""
    def __init__(self, logger: ILogger):
        self.logger = logger


class MockServiceWithMultipleDeps:
    """Mock服务（多个依赖）"""
    def __init__(self, logger: ILogger, event_bus: IEventBus):
        self.logger = logger
        self.event_bus = event_bus


class TestDIContainer:
    """依赖注入容器测试"""

    @pytest.fixture
    def container(self):
        """创建容器"""
        return DIContainer()

    def test_register_singleton(self, container):
        """测试注册单例服务"""
        container.register_singleton(ILogger, ConsoleLogger)
        assert container.is_registered(ILogger)

    def test_register_transient(self, container):
        """测试注册瞬态服务"""
        container.register_transient(ILogger, ConsoleLogger)
        assert container.is_registered(ILogger)

    def test_register_instance(self, container):
        """测试注册实例"""
        instance = ConsoleLogger()
        container.register_instance(ILogger, instance)
        assert container.is_registered(ILogger)

    def test_resolve_singleton(self, container):
        """测试解析单例服务"""
        container.register_singleton(ILogger, ConsoleLogger)
        instance1 = container.resolve(ILogger)
        instance2 = container.resolve(ILogger)
        assert instance1 is instance2

    def test_resolve_transient(self, container):
        """测试解析瞬态服务"""
        container.register_transient(ILogger, ConsoleLogger)
        instance1 = container.resolve(ILogger)
        instance2 = container.resolve(ILogger)
        assert instance1 is not instance2

    def test_resolve_instance(self, container):
        """测试解析实例"""
        instance = ConsoleLogger()
        container.register_instance(ILogger, instance)
        resolved = container.resolve(ILogger)
        assert resolved is instance

    def test_resolve_with_dependencies(self, container):
        """测试解析带依赖的服务"""
        container.register_singleton(ILogger, ConsoleLogger)
        container.register_transient(MockService, MockService)
        service = container.resolve(MockService)
        assert service is not None
        assert service.logger is not None

    def test_resolve_with_multiple_dependencies(self, container):
        """测试解析带多个依赖的服务"""
        container.register_singleton(ILogger, ConsoleLogger)
        container.register_singleton(IEventBus, EventBus)
        container.register_transient(MockServiceWithMultipleDeps, MockServiceWithMultipleDeps)
        service = container.resolve(MockServiceWithMultipleDeps)
        assert service is not None
        assert service.logger is not None
        assert service.event_bus is not None

    def test_resolve_unregistered_service(self, container):
        """测试解析未注册的服务"""
        with pytest.raises(ValueError):
            container.resolve(ILogger)

    def test_is_registered(self, container):
        """测试检查服务是否已注册"""
        assert not container.is_registered(ILogger)
        container.register_singleton(ILogger, ConsoleLogger)
        assert container.is_registered(ILogger)

    def test_clear(self, container):
        """测试清除所有服务"""
        container.register_singleton(ILogger, ConsoleLogger)
        container.register_singleton(IEventBus, EventBus)
        container.clear()
        assert not container.is_registered(ILogger)
        assert not container.is_registered(IEventBus)

    def test_dependency_injection_chain(self, container):
        """测试依赖注入链"""
        container.register_singleton(ILogger, ConsoleLogger)
        container.register_singleton(IEventBus, EventBus)
        container.register_transient(MockServiceWithMultipleDeps, MockServiceWithMultipleDeps)

        service1 = container.resolve(MockServiceWithMultipleDeps)
        service2 = container.resolve(MockServiceWithMultipleDeps)

        assert service1.logger is service2.logger
        assert service1.event_bus is service2.event_bus
        assert service1 is not service2
