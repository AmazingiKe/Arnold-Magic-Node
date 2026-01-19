from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ILogger(ABC):
    """
    日志接口

    职责:
    - 提供统一的日志记录接口
    - 支持不同级别的日志记录
    - 支持结构化日志
    """

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """
        记录调试信息

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """
        记录信息

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """
        记录警告

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """
        记录错误

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass

    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """
        记录严重错误

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass
