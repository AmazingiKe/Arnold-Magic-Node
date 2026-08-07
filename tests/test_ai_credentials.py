import json
import unittest

from arnold_magic_node.tools.ai_client import (
    AiConfigurationError,
    HttpResponse,
    create_openai_client,
)
from arnold_magic_node.tools.ai_credentials import (
    api_origin,
    clear_all_session_api_keys,
    clear_session_api_key,
    get_session_api_key,
    has_environment_api_key,
    set_session_api_key,
)


class FakeTransport(object):
    def __init__(self):
        self.calls = []

    def post(self, url, headers, body, timeout, max_response_bytes):
        self.calls.append(
            {
                "url": url,
                "headers": dict(headers),
                "body": body,
            }
        )
        return HttpResponse(
            status_code=200,
            body=json.dumps(
                {
                    "status": "completed",
                    "output_text": "ok",
                }
            ).encode("utf-8"),
            headers={},
        )


class AiCredentialStoreTests(unittest.TestCase):
    def setUp(self):
        clear_all_session_api_keys()

    def tearDown(self):
        clear_all_session_api_keys()

    def test_session_key_is_bound_to_effective_https_origin(self):
        set_session_api_key(
            "https://api.openai.com/v1",
            "session-secret",
        )

        self.assertEqual(
            api_origin("https://API.OPENAI.COM:443/another/path"),
            "https://api.openai.com:443",
        )
        self.assertEqual(
            get_session_api_key("https://api.openai.com:443/v2"),
            "session-secret",
        )
        self.assertIsNone(get_session_api_key("https://compatible.example/v1"))

    def test_session_key_rejects_local_http_and_can_be_cleared(self):
        with self.assertRaises(AiConfigurationError):
            set_session_api_key(
                "http://127.0.0.1:1234/v1",
                "local-secret",
            )

        set_session_api_key("https://ai.example.com/v1", "secret")
        self.assertTrue(clear_session_api_key("https://ai.example.com/v2"))
        self.assertIsNone(get_session_api_key("https://ai.example.com/v1"))
        self.assertFalse(clear_session_api_key("https://ai.example.com/v1"))

    def test_environment_status_never_returns_the_secret(self):
        environment = {
            "VALID_AI_KEY": "environment-secret",
            "INVALID_AI_KEY": "unsafe\nsecret",
        }

        self.assertTrue(has_environment_api_key("VALID_AI_KEY", environ=environment))
        self.assertFalse(has_environment_api_key("INVALID_AI_KEY", environ=environment))
        self.assertFalse(has_environment_api_key("MISSING_AI_KEY", environ=environment))

    def test_factory_does_not_use_legacy_session_key_for_model_profiles(self):
        set_session_api_key(
            "https://api.openai.com/v1",
            "origin-bound-secret",
        )
        matching_transport = FakeTransport()
        client = create_openai_client(
            settings={
                "schema_version": 1,
                "base_url": "https://api.openai.com/v1",
                "api_style": "responses",
                "model": "test-model",
            },
            transport=matching_transport,
            environ={},
        )

        with self.assertRaises(AiConfigurationError):
            client.generate_text("test", "graph")
        self.assertEqual(matching_transport.calls, [])

        other_transport = FakeTransport()
        other_client = create_openai_client(
            settings={
                "schema_version": 1,
                "base_url": "https://compatible.example/v1",
                "api_style": "responses",
                "model": "test-model",
                "api_key_env": "COMPATIBLE_AI_KEY",
            },
            transport=other_transport,
            environ={},
        )
        with self.assertRaises(AiConfigurationError):
            other_client.generate_text("test", "graph")
        self.assertEqual(other_transport.calls, [])


if __name__ == "__main__":
    unittest.main()
