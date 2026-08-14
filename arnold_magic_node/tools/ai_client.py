"""不依赖 OpenAI SDK 的轻量 OpenAI-compatible HTTP 客户端。"""

import ipaddress
import json
import math
import os
import re
import socket
import ssl
import uuid
from dataclasses import dataclass, fields
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from arnold_magic_node.core.ai_protocol import (
    API_STYLE_RESPONSES,
    SUPPORTED_API_STYLES,
    AiError,
    AiProtocolError,
    AiStreamAccumulator,
    build_request_payload,
    load_json_strict,
    parse_json_output,
    parse_response_text,
    validate_json_schema_subset,
)


DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-5.6-terra"
DEFAULT_API_KEY_ENV = "OPENAI_API_KEY"
MAX_BODY_LIMIT = 10 * 1024 * 1024
MAX_ERROR_BODY_BYTES = 64 * 1024
MAX_API_KEY_LENGTH = 8192


class AiClientError(AiError):
    """AI 客户端公共错误基类。"""


class AiConfigurationError(AiClientError):
    """AI 客户端配置无效或缺少凭据。"""


class AiTransportError(AiClientError):
    """网络传输失败。"""


class AiTimeoutError(AiTransportError):
    """网络请求超时。"""


class AiTlsError(AiTransportError):
    """HTTPS 证书或 TLS 握手失败。"""


class AiResponseTooLargeError(AiTransportError):
    """服务端响应超过本地安全上限。"""


class AiHttpError(AiClientError):
    """AI 服务返回非 2xx HTTP 状态。"""

    def __init__(
        self,
        status_code,
        message,
        request_id=None,
        error_code=None,
        retry_after=None,
    ):
        super(AiHttpError, self).__init__(
            "AI 服务请求失败（HTTP {}）：{}".format(status_code, message)
        )
        self.status_code = status_code
        self.request_id = request_id
        self.error_code = error_code
        self.retry_after = retry_after


class AiAuthenticationError(AiHttpError):
    """API Key 无效或当前凭据没有访问权限。"""


class AiRateLimitError(AiHttpError):
    """请求频率、余额或用量限制。"""


@dataclass(frozen=True)
class HttpResponse:
    """传输层返回的有限大小 HTTP 响应。"""

    status_code: int
    body: bytes
    headers: dict


class HttpEventStream(object):
    """有累计大小上限的 UTF-8 Server-Sent Events 数据流。"""

    def __init__(self, raw_stream, max_response_bytes):
        self.raw_stream = raw_stream
        self.max_response_bytes = max_response_bytes
        self.status_code = raw_stream.getcode()
        self.headers = _headers_dict(raw_stream.headers)
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()
        return False

    def close(self):
        if not self._closed:
            self._closed = True
            self.raw_stream.close()

    @staticmethod
    def _decode_data_lines(data_lines):
        try:
            return b"\n".join(data_lines).decode("utf-8")
        except UnicodeDecodeError as error:
            raise AiProtocolError("AI 流事件不是有效的 UTF-8") from error

    def __iter__(self):
        total_bytes = 0
        data_lines = []
        try:
            while True:
                remaining = self.max_response_bytes - total_bytes
                line = self.raw_stream.readline(remaining + 1)
                if len(line) > remaining:
                    raise AiResponseTooLargeError("AI 响应超过大小限制")
                total_bytes += len(line)
                if not line:
                    if data_lines:
                        yield self._decode_data_lines(data_lines)
                    break

                line = line.rstrip(b"\r\n")
                if not line:
                    if data_lines:
                        yield self._decode_data_lines(data_lines)
                        data_lines = []
                    continue
                if line.startswith(b":"):
                    continue
                field, separator, value = line.partition(b":")
                if not separator or field != b"data":
                    continue
                if value.startswith(b" "):
                    value = value[1:]
                data_lines.append(value)
        finally:
            self.close()


@dataclass(frozen=True)
class AiResult:
    """统一的 AI 响应结果。"""

    text: str
    data: object
    response_id: object
    request_id: object
    model: object
    usage: dict


@dataclass(frozen=True)
class AiClientConfig:
    """可由独立 JSON 设置构造的客户端配置。"""

    schema_version: int = 1
    api_style: str = API_STYLE_RESPONSES
    base_url: str = DEFAULT_OPENAI_BASE_URL
    model: str = DEFAULT_OPENAI_MODEL
    api_key_env: str = DEFAULT_API_KEY_ENV
    timeout_seconds: float = 60
    max_output_tokens: int = 4096
    max_request_bytes: int = 1024 * 1024
    max_response_bytes: int = 2 * 1024 * 1024
    chat_token_parameter: str = "max_tokens"

    @classmethod
    def from_mapping(cls, values):
        if not isinstance(values, dict):
            raise AiConfigurationError("AI 设置根节点必须是 JSON 对象")
        known_fields = {field.name for field in fields(cls)}
        unknown_fields = [key for key in values if key not in known_fields]
        if unknown_fields:
            raise AiConfigurationError(
                "未知 AI 设置字段：{}".format(
                    ", ".join(repr(key) for key in unknown_fields[:5])
                )
            )
        return cls(
            **{key: value for key, value in values.items() if key in known_fields}
        )

    def validate(self):
        _validate_ai_client_config(self)
        return self


class _RejectRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        raise HTTPError(
            request.full_url,
            code,
            "AI 接口重定向已被阻止",
            headers,
            file_pointer,
        )


def _headers_dict(headers):
    if headers is None:
        return {}
    if hasattr(headers, "items"):
        return {str(key): str(value) for key, value in headers.items()}
    return dict(headers)


def _header_value(headers, name):
    wanted = name.lower()
    for key, value in (headers or {}).items():
        if str(key).lower() == wanted:
            return value
    return None


def _sanitize_external_value(value, api_key=None, max_length=512):
    """压平服务端元数据并移除当前请求凭据。"""

    if value is None:
        return None
    text = str(value)
    if api_key:
        text = text.replace(api_key, "[REDACTED]")
    text = " ".join(text.split())[:max_length]
    return text or None


def _read_bounded(stream, headers, limit):
    content_length = _header_value(headers, "content-length")
    if content_length:
        try:
            if int(content_length) > limit:
                raise AiResponseTooLargeError("AI 响应超过大小限制")
        except ValueError:
            pass
    body = stream.read(limit + 1)
    if len(body) > limit:
        raise AiResponseTooLargeError("AI 响应超过大小限制")
    return body


class UrllibTransport(object):
    """使用 urllib 和系统默认 TLS 校验的同步 JSON 传输层。"""

    def __init__(self, opener=None, loopback_opener=None):
        if opener is None:
            context = ssl.create_default_context()
            opener = build_opener(
                _RejectRedirectHandler(), HTTPSHandler(context=context)
            )
            if loopback_opener is None:
                loopback_opener = build_opener(
                    ProxyHandler({}),
                    _RejectRedirectHandler(),
                    HTTPSHandler(context=context),
                )
        self.opener = opener
        self.loopback_opener = loopback_opener or opener

    def post(self, url, headers, body, timeout, max_response_bytes):
        request_headers = {
            key: value
            for key, value in headers.items()
            if key.lower() != "authorization"
        }
        request = Request(
            url,
            data=body,
            headers=request_headers,
            method="POST",
        )
        authorization = _header_value(headers, "authorization")
        if authorization:
            request.add_unredirected_header("Authorization", authorization)

        hostname = urlsplit(url).hostname
        opener = self.loopback_opener if _is_loopback_host(hostname) else self.opener
        try:
            with opener.open(request, timeout=timeout) as response:
                response_headers = _headers_dict(response.headers)
                response_body = _read_bounded(
                    response, response_headers, max_response_bytes
                )
                return HttpResponse(
                    status_code=response.getcode(),
                    body=response_body,
                    headers=response_headers,
                )
        except HTTPError as error:
            try:
                response_headers = _headers_dict(error.headers)
                response_body = _read_bounded(
                    error,
                    response_headers,
                    min(max_response_bytes, MAX_ERROR_BODY_BYTES),
                )
                return HttpResponse(
                    status_code=error.code,
                    body=response_body,
                    headers=response_headers,
                )
            finally:
                error.close()

    def open_stream(
        self,
        url,
        headers,
        body,
        timeout,
        max_response_bytes,
    ):
        """打开 SSE 响应；HTTP 错误仍转换为有限大小的普通响应。"""

        request_headers = {
            key: value
            for key, value in headers.items()
            if key.lower() != "authorization"
        }
        request = Request(
            url,
            data=body,
            headers=request_headers,
            method="POST",
        )
        authorization = _header_value(headers, "authorization")
        if authorization:
            request.add_unredirected_header("Authorization", authorization)

        hostname = urlsplit(url).hostname
        opener = self.loopback_opener if _is_loopback_host(hostname) else self.opener
        try:
            response = opener.open(request, timeout=timeout)
        except HTTPError as error:
            try:
                response_headers = _headers_dict(error.headers)
                response_body = _read_bounded(
                    error,
                    response_headers,
                    min(max_response_bytes, MAX_ERROR_BODY_BYTES),
                )
                return HttpResponse(
                    status_code=error.code,
                    body=response_body,
                    headers=response_headers,
                )
            finally:
                error.close()

        status_code = response.getcode()
        if status_code < 200 or status_code >= 300:
            try:
                response_headers = _headers_dict(response.headers)
                response_body = _read_bounded(
                    response,
                    response_headers,
                    min(max_response_bytes, MAX_ERROR_BODY_BYTES),
                )
                return HttpResponse(
                    status_code=status_code,
                    body=response_body,
                    headers=response_headers,
                )
            finally:
                response.close()
        return HttpEventStream(response, max_response_bytes)


def _is_loopback_host(hostname):
    if not hostname:
        return False
    if hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def normalize_base_url(base_url):
    """校验并标准化 AI 服务根 URL。"""

    if not isinstance(base_url, str) or not base_url:
        raise AiConfigurationError("base_url 不能为空")
    if base_url != base_url.strip() or "\\" in base_url:
        raise AiConfigurationError("base_url 格式无效")
    if any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in base_url
    ):
        raise AiConfigurationError("base_url 包含空白或控制字符")

    try:
        parts = urlsplit(base_url)
        port = parts.port
    except ValueError as error:
        raise AiConfigurationError("base_url 格式无效") from error
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise AiConfigurationError("base_url 必须是有效的 HTTP(S) URL")
    if parts.username is not None or parts.password is not None:
        raise AiConfigurationError("base_url 不得包含用户名或密码")
    if parts.query or parts.fragment:
        raise AiConfigurationError("base_url 不得包含 query 或 fragment")
    if port is not None and port < 1:
        raise AiConfigurationError("base_url 端口无效")
    if parts.scheme == "http" and not _is_loopback_host(parts.hostname):
        raise AiConfigurationError("远程 AI 接口必须使用 HTTPS")
    return base_url.rstrip("/"), parts


def _validate_number(value, name, minimum, maximum):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or (isinstance(value, float) and not math.isfinite(value))
        or value < minimum
        or value > maximum
    ):
        raise AiConfigurationError(
            "{} 必须在 {} 到 {} 之间".format(name, minimum, maximum)
        )


def _validate_integer(value, name, minimum, maximum):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < minimum
        or value > maximum
    ):
        raise AiConfigurationError(
            "{} 必须是 {} 到 {} 之间的整数".format(name, minimum, maximum)
        )


def _validate_ai_client_config(config):
    if not isinstance(config, AiClientConfig):
        raise AiConfigurationError("config 必须是 AiClientConfig")
    if isinstance(config.schema_version, bool) or config.schema_version != 1:
        raise AiConfigurationError("不支持的 AI 设置 schema_version")
    if config.api_style not in SUPPORTED_API_STYLES:
        raise AiConfigurationError("不支持的 API 风格：{}".format(config.api_style))
    if not isinstance(config.model, str) or not config.model.strip():
        raise AiConfigurationError("AI 模型名称不能为空")
    if not isinstance(config.api_key_env, str) or not re.match(
        r"^[A-Za-z_][A-Za-z0-9_]*$", config.api_key_env
    ):
        raise AiConfigurationError("API Key 环境变量名无效")
    _validate_number(config.timeout_seconds, "timeout_seconds", 1, 300)
    _validate_integer(
        config.max_output_tokens,
        "max_output_tokens",
        1,
        1000000,
    )
    _validate_integer(
        config.max_request_bytes,
        "max_request_bytes",
        1,
        MAX_BODY_LIMIT,
    )
    _validate_integer(
        config.max_response_bytes,
        "max_response_bytes",
        1,
        MAX_BODY_LIMIT,
    )
    if config.chat_token_parameter not in (
        "max_tokens",
        "max_completion_tokens",
    ):
        raise AiConfigurationError("Chat token 参数不受支持")
    normalize_base_url(config.base_url)


def normalize_api_key(value):
    """返回去除首尾空白后的安全 API Key，空值返回 ``None``。"""

    if value is None:
        return None
    if not isinstance(value, str):
        raise AiConfigurationError("API Key 必须是字符串")
    key = value.strip()
    if not key:
        return None
    if len(key) > MAX_API_KEY_LENGTH or any(
        ord(character) < 33 or ord(character) > 126 for character in key
    ):
        raise AiConfigurationError("API Key 格式无效")
    return key


class OpenAICompatibleClient(object):
    """Responses 与 Chat Completions 共用的同步客户端。"""

    def __init__(
        self,
        config=None,
        api_key=None,
        transport=None,
        environ=None,
    ):
        self.config = AiClientConfig() if config is None else config
        self._validate_config()
        self.base_url, self._url_parts = normalize_base_url(self.config.base_url)
        self._explicit_api_key = api_key
        self.environ = os.environ if environ is None else environ
        self.transport = transport or UrllibTransport()

    @classmethod
    def from_user_settings(
        cls,
        settings=None,
        user_root=None,
        paths=None,
        api_key=None,
        transport=None,
        environ=None,
    ):
        if settings is None:
            from .ai_settings import load_ai_settings

            settings = load_ai_settings(user_root=user_root, paths=paths)
        from .ai_routing import AiRoutingConfig

        routing_config = AiRoutingConfig.from_mapping(settings)
        profile = routing_config.model_for_mode("fast")
        config = profile.client_config()
        if api_key is None:
            # v3 的每个模型都携带自己的明文凭据。即使配置中为空，也要
            # 显式传入空字符串，避免意外回退到进程环境中的其他密钥。
            api_key = profile.api_key
        return cls(
            config=config,
            api_key=api_key,
            transport=transport,
            environ=environ,
        )

    def _validate_config(self):
        _validate_ai_client_config(self.config)

    def _is_loopback(self):
        return _is_loopback_host(self._url_parts.hostname)

    def _resolve_api_key(self):
        if self._url_parts.scheme == "http":
            return None

        if self._explicit_api_key is not None:
            return normalize_api_key(self._explicit_api_key)

        if (
            self.config.api_key_env == DEFAULT_API_KEY_ENV
            and self._url_parts.hostname.lower() != "api.openai.com"
        ):
            return None
        return normalize_api_key(self.environ.get(self.config.api_key_env))

    def _endpoint_url(self):
        endpoint = (
            "responses"
            if self.config.api_style == API_STYLE_RESPONSES
            else "chat/completions"
        )
        return self.base_url + "/" + endpoint

    def _request_headers(self, api_key, stream=False):
        headers = {
            "Accept": "text/event-stream" if stream else "application/json",
            "Accept-Encoding": "identity",
            "Content-Type": "application/json; charset=utf-8",
            "X-Client-Request-Id": str(uuid.uuid4()),
        }
        if api_key:
            headers["Authorization"] = "Bearer " + api_key
        return headers

    def _send(
        self,
        instructions,
        input_data,
        response_schema,
        schema_name,
    ):
        api_key = self._resolve_api_key()
        if not api_key and not self._is_loopback():
            raise AiConfigurationError("当前模型未配置 API Key")

        payload = build_request_payload(
            api_style=self.config.api_style,
            model=self.config.model,
            instructions=instructions,
            input_data=input_data,
            response_schema=response_schema,
            schema_name=schema_name,
            max_output_tokens=self.config.max_output_tokens,
            chat_token_parameter=self.config.chat_token_parameter,
        )
        try:
            body = json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError, RecursionError) as error:
            raise AiProtocolError("AI 请求无法编码为 JSON") from error
        if len(body) > self.config.max_request_bytes:
            raise AiConfigurationError("AI 请求超过大小限制")

        headers = self._request_headers(api_key)
        try:
            response = self.transport.post(
                self._endpoint_url(),
                headers,
                body,
                self.config.timeout_seconds,
                self.config.max_response_bytes,
            )
        except (socket.timeout, TimeoutError):
            raise AiTimeoutError("AI 请求超时") from None
        except ssl.SSLError:
            raise AiTlsError("AI 接口 TLS 校验失败") from None
        except URLError as error:
            reason = getattr(error, "reason", None)
            if isinstance(reason, (socket.timeout, TimeoutError)):
                raise AiTimeoutError("AI 请求超时") from None
            if isinstance(reason, ssl.SSLError):
                raise AiTlsError("AI 接口 TLS 校验失败") from None
            raise AiTransportError("无法连接 AI 接口") from None
        except (HTTPException, OSError):
            raise AiTransportError("无法连接 AI 接口") from None

        if not isinstance(response, HttpResponse):
            raise AiTransportError("AI 传输层返回了无效响应")
        if len(response.body) > self.config.max_response_bytes:
            raise AiResponseTooLargeError("AI 响应超过大小限制")

        content_encoding = _header_value(response.headers, "content-encoding")
        if content_encoding and content_encoding.lower() not in (
            "identity",
            "none",
        ):
            raise AiTransportError("AI 响应使用了不支持的压缩编码")

        if response.status_code < 200 or response.status_code >= 300:
            self._raise_http_error(response, api_key)
        return response, self._decode_success_body(response.body)

    @staticmethod
    def _decode_success_body(body):
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError as error:
            raise AiProtocolError("AI 响应不是 UTF-8 JSON") from error
        payload = load_json_strict(text)
        if not isinstance(payload, dict):
            raise AiProtocolError("AI 响应根节点必须是 JSON 对象")
        return payload

    def _raise_http_error(self, response, api_key):
        request_id = _sanitize_external_value(
            _header_value(response.headers, "x-request-id"), api_key
        )
        error_code = None
        message = "服务端未提供错误详情"
        try:
            body_text = response.body.decode("utf-8")
            payload = load_json_strict(body_text)
        except (UnicodeDecodeError, AiProtocolError):
            payload = None

        if isinstance(payload, dict):
            error_data = payload.get("error")
            if isinstance(error_data, dict):
                message = str(
                    error_data.get("message") or error_data.get("type") or message
                )
                error_code = error_data.get("code")
            elif isinstance(error_data, str):
                message = error_data

        message = _sanitize_external_value(message, api_key, 2048)
        if message is None:
            message = "服务端未提供错误详情"
        error_code = _sanitize_external_value(error_code, api_key)
        retry_after = _sanitize_external_value(
            _header_value(response.headers, "retry-after"), api_key
        )
        error_type = AiHttpError
        if response.status_code in (401, 403):
            error_type = AiAuthenticationError
        elif response.status_code == 429:
            error_type = AiRateLimitError
        raise error_type(
            status_code=response.status_code,
            message=message,
            request_id=request_id,
            error_code=error_code,
            retry_after=retry_after,
        )

    @staticmethod
    def _raise_stream_transport_error(error):
        if isinstance(error, (socket.timeout, TimeoutError)):
            raise AiTimeoutError("AI 流式请求超时") from None
        if isinstance(error, ssl.SSLError):
            raise AiTlsError("AI 接口 TLS 校验失败") from None
        if isinstance(error, URLError):
            reason = getattr(error, "reason", None)
            if isinstance(reason, (socket.timeout, TimeoutError)):
                raise AiTimeoutError("AI 流式请求超时") from None
            if isinstance(reason, ssl.SSLError):
                raise AiTlsError("AI 接口 TLS 校验失败") from None
        raise AiTransportError("AI 流式连接中断") from None

    def stream_text(
        self,
        instructions,
        input_data,
        response_schema=None,
        schema_name="structured_output",
    ):
        """以 SSE 增量形式返回模型可见文本。"""

        api_key = self._resolve_api_key()
        if not api_key and not self._is_loopback():
            raise AiConfigurationError("当前模型未配置 API Key")

        payload = build_request_payload(
            api_style=self.config.api_style,
            model=self.config.model,
            instructions=instructions,
            input_data=input_data,
            response_schema=response_schema,
            schema_name=schema_name,
            max_output_tokens=self.config.max_output_tokens,
            chat_token_parameter=self.config.chat_token_parameter,
            stream=True,
        )
        try:
            body = json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError, RecursionError) as error:
            raise AiProtocolError("AI 请求无法编码为 JSON") from error
        if len(body) > self.config.max_request_bytes:
            raise AiConfigurationError("AI 请求超过大小限制")

        headers = self._request_headers(api_key, stream=True)
        try:
            stream_response = self.transport.open_stream(
                self._endpoint_url(),
                headers,
                body,
                self.config.timeout_seconds,
                self.config.max_response_bytes,
            )
        except (
            socket.timeout,
            TimeoutError,
            ssl.SSLError,
            URLError,
            HTTPException,
            OSError,
        ) as error:
            self._raise_stream_transport_error(error)

        if isinstance(stream_response, HttpResponse):
            if stream_response.status_code < 200 or stream_response.status_code >= 300:
                self._raise_http_error(stream_response, api_key)
            raise AiProtocolError("AI 流式传输层返回了无效响应")
        if not isinstance(stream_response, HttpEventStream):
            raise AiProtocolError("AI 流式传输层返回了无效响应")

        accumulator = AiStreamAccumulator(self.config.api_style)
        try:
            with stream_response:
                content_encoding = _header_value(
                    stream_response.headers, "content-encoding"
                )
                if content_encoding and content_encoding.lower() not in (
                    "identity",
                    "none",
                ):
                    raise AiProtocolError("AI 响应使用了不支持的压缩编码")
                content_type = _header_value(stream_response.headers, "content-type")
                if content_type and not content_type.lower().startswith(
                    "text/event-stream"
                ):
                    raise AiProtocolError("AI 流式响应不是 text/event-stream")

                for raw_data in stream_response:
                    delta = accumulator.consume(raw_data)
                    if delta:
                        yield delta
                    if accumulator.is_terminal:
                        break
                text, final_payload = accumulator.finalize()
        except (
            socket.timeout,
            TimeoutError,
            ssl.SSLError,
            URLError,
            HTTPException,
            OSError,
        ) as error:
            self._raise_stream_transport_error(error)

        response = HttpResponse(
            status_code=stream_response.status_code,
            body=b"",
            headers=stream_response.headers,
        )
        return self._result(response, final_payload, text, None)

    def generate_text(
        self,
        instructions,
        input_data,
        response_schema=None,
        schema_name="structured_output",
    ):
        """调用 AI 并返回统一文本结果。"""

        response, payload = self._send(
            instructions,
            input_data,
            response_schema,
            schema_name,
        )
        text = parse_response_text(self.config.api_style, payload)
        return self._result(response, payload, text, None)

    def generate_json(
        self,
        instructions,
        input_data,
        response_schema,
        schema_name="structured_output",
    ):
        """调用结构化输出并把模型文本严格解析成 Python 数据。"""

        result = self.generate_text(
            instructions,
            input_data,
            response_schema=response_schema,
            schema_name=schema_name,
        )
        data = parse_json_output(result.text)
        validate_json_schema_subset(data, response_schema)
        return AiResult(
            text=result.text,
            data=data,
            response_id=result.response_id,
            request_id=result.request_id,
            model=result.model,
            usage=result.usage,
        )

    @staticmethod
    def _result(response, payload, text, data):
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            usage = {}
        return AiResult(
            text=text,
            data=data,
            response_id=payload.get("id"),
            request_id=_header_value(response.headers, "x-request-id"),
            model=payload.get("model"),
            usage=usage,
        )


def create_openai_client(
    settings=None,
    user_root=None,
    paths=None,
    api_key=None,
    transport=None,
    environ=None,
):
    """从独立用户设置创建客户端的便捷入口。"""

    return OpenAICompatibleClient.from_user_settings(
        settings=settings,
        user_root=user_root,
        paths=paths,
        api_key=api_key,
        transport=transport,
        environ=environ,
    )


__all__ = [
    "AiAuthenticationError",
    "AiError",
    "AiClientConfig",
    "AiClientError",
    "AiConfigurationError",
    "AiHttpError",
    "AiRateLimitError",
    "AiResponseTooLargeError",
    "AiResult",
    "AiTimeoutError",
    "AiTlsError",
    "AiTransportError",
    "HttpEventStream",
    "HttpResponse",
    "OpenAICompatibleClient",
    "UrllibTransport",
    "create_openai_client",
    "normalize_api_key",
    "normalize_base_url",
]
