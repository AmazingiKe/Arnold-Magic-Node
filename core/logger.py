import logging
from typing import Any, Dict
from .i_logger import ILogger, LogLevel


class ConsoleLogger(ILogger):
    """
    控制台日志器实现

    职责:
    - 提供日志记录功能
    - 支持不同级别的日志输出
    - 支持结构化日志
    """

    def __init__(self, name: str = 'ArnoldMagicNode', level: LogLevel = LogLevel.INFO):
        """
        初始化日志器

        参数:
            name: 日志器名称
            level: 日志级别
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.value))

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def debug(self, message: str, **kwargs) -> None:
        """
        记录调试信息

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        if kwargs:
            message = f"{message} - {kwargs}"
        self._logger.debug(message)

    def info(self, message: str, **kwargs) -> None:
        """
        记录信息

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        if kwargs:
            message = f"{message} - {kwargs}"
        self._logger.info(message)

    def warning(self, message: str, **kwargs) -> None:
        """
        记录警告

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        if kwargs:
            message = f"{message} - {kwargs}"
        self._logger.warning(message)

    def error(self, message: str, **kwargs) -> None:
        """
        记录错误

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        if kwargs:
            message = f"{message} - {kwargs}"
        self._logger.error(message)

    def critical(self, message: str, **kwargs) -> None:
        """
        记录严重错误

        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        if kwargs:
            message = f"{message} - {kwargs}"
        self._logger.critical(message)
