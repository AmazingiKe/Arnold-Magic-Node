"""按接口 origin 隔离的进程内 AI 会话凭据。"""

import os
import threading

from .ai_client import (
    AiClientConfig,
    AiConfigurationError,
    normalize_api_key,
    normalize_base_url,
)


_SESSION_API_KEYS = {}
_SESSION_API_KEYS_LOCK = threading.RLock()


def api_origin(base_url):
    """返回包含有效端口的标准化接口 origin。"""

    _, parts = normalize_base_url(base_url)
    scheme = parts.scheme.lower()
    hostname = parts.hostname.lower()
    if ":" in hostname:
        hostname = "[{}]".format(hostname)
    port = parts.port or (443 if scheme == "https" else 80)
    return "{}://{}:{}".format(scheme, hostname, port)


def set_session_api_key(base_url, api_key):
    """为一个 HTTPS origin 保存当前进程有效的临时密钥。"""

    origin = api_origin(base_url)
    if not origin.startswith("https://"):
        raise AiConfigurationError("本地 HTTP 接口不会接收会话 API Key")
    normalized_key = normalize_api_key(api_key)
    if normalized_key is None:
        raise AiConfigurationError("会话 API Key 不能为空")
    with _SESSION_API_KEYS_LOCK:
        _SESSION_API_KEYS[origin] = normalized_key
    return origin


def get_session_api_key(base_url):
    """仅返回与目标 origin 完全匹配的会话密钥。"""

    origin = api_origin(base_url)
    with _SESSION_API_KEYS_LOCK:
        return _SESSION_API_KEYS.get(origin)


def clear_session_api_key(base_url):
    """清除目标 origin 的会话密钥并返回是否曾存在。"""

    origin = api_origin(base_url)
    with _SESSION_API_KEYS_LOCK:
        return _SESSION_API_KEYS.pop(origin, None) is not None


def clear_all_session_api_keys():
    """清除当前进程中的全部 AI 会话密钥。"""

    with _SESSION_API_KEYS_LOCK:
        _SESSION_API_KEYS.clear()


def has_environment_api_key(api_key_env, environ=None):
    """只报告环境变量中是否有格式有效的密钥，不返回密钥内容。"""

    AiClientConfig(api_key_env=api_key_env).validate()
    environment = os.environ if environ is None else environ
    try:
        return normalize_api_key(environment.get(api_key_env)) is not None
    except AiConfigurationError:
        return False


__all__ = [
    "api_origin",
    "clear_all_session_api_keys",
    "clear_session_api_key",
    "get_session_api_key",
    "has_environment_api_key",
    "set_session_api_key",
]
