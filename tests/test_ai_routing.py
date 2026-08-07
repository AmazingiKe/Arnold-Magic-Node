import inspect
import io
import json
import unittest

from arnold_magic_node.tools.ai_client import (
    AiConfigurationError,
    AiTimeoutError,
    HttpEventStream,
)
from arnold_magic_node.tools.ai_routing import (
    AI_MODE_COMPLEX,
    AI_MODE_FAST,
    AiRoutingConfig,
    AiService,
    create_ai_service,
    migrate_ai_settings,
    test_ai_model,
)


def make_model(
    model_id,
    model,
    base_url="https://api.openai.com/v1",
    api_style="responses",
    api_key="stored-secret",
    timeout_seconds=30,
    max_output_tokens=2048,
    chat_token_parameter="max_tokens",
):
    return {
        "id": model_id,
        "model": model,
        "base_url": base_url,
        "api_style": api_style,
        "api_key": api_key,
        "timeout_seconds": timeout_seconds,
        "max_output_tokens": max_output_tokens,
        "max_request_bytes": 1024 * 1024,
        "max_response_bytes": 2 * 1024 * 1024,
        "chat_token_parameter": chat_token_parameter,
    }


def make_v3_settings():
    return {
        "schema_version": 3,
        "models": [
            make_model("fast-id", "fast-model", api_key="fast-secret"),
            make_model(
                "middle-id",
                "middle-model",
                base_url="https://middle.example/v1",
                api_key="middle-secret",
            ),
            make_model(
                "complex-id",
                "complex-model",
                base_url="https://complex.example/v1",
                api_style="chat_completions",
                api_key="complex-secret",
                timeout_seconds=90,
                chat_token_parameter="max_completion_tokens",
            ),
        ],
        "fast_model_id": "fast-id",
        "complex_model_id": "complex-id",
    }


def make_v1_settings():
    return {
        "schema_version": 1,
        "api_style": "chat_completions",
        "base_url": "https://legacy.example/v1",
        "model": "legacy-model",
        "api_key_env": "LEGACY_KEY",
        "timeout_seconds": 45,
        "max_output_tokens": 512,
        "max_request_bytes": 2048,
        "max_response_bytes": 4096,
        "chat_token_parameter": "max_completion_tokens",
    }


def make_v2_settings():
    return {
        "schema_version": 2,
        "default_mode": "complex",
        "api_style": "responses",
        "base_url": "https://shared.example/v1",
        "model_queues": {
            "fast": {
                "models": ["fast-a", "shared"],
                "rotate_on_error": True,
            },
            "complex": {
                "models": ["complex-a", "shared"],
                "rotate_on_error": False,
            },
        },
        "api_key_env": "SHARED_KEY",
        "timeout_seconds": 60,
        "max_output_tokens": 4096,
        "max_request_bytes": 1024 * 1024,
        "max_response_bytes": 2 * 1024 * 1024,
        "chat_token_parameter": "max_tokens",
    }


class FakeClient(object):
    def __init__(self, events, profile, calls):
        self.events = list(events)
        self.profile = profile
        self.calls = calls

    def stream_text(
        self,
        instructions,
        input_data,
        response_schema=None,
        schema_name="structured_output",
    ):
        self.calls.append(
            (
                self.profile.id,
                instructions,
                input_data,
                response_schema,
                schema_name,
            )
        )
        for event in self.events:
            if isinstance(event, BaseException):
                raise event
            yield event


class FakeClientFactory(object):
    def __init__(self, events_by_id):
        self.events_by_id = events_by_id
        self.created = []
        self.calls = []

    def __call__(self, profile):
        self.created.append(profile)
        return FakeClient(self.events_by_id[profile.id], profile, self.calls)


class FakeStreamingResponse(object):
    def __init__(self, body):
        self._body = io.BytesIO(body)
        self.headers = {"Content-Type": "text/event-stream"}
        self.closed = False

    def getcode(self):
        return 200

    def readline(self, size=-1):
        return self._body.readline(size)

    def close(self):
        self.closed = True
        self._body.close()


class RecordingProbeTransport(object):
    def __init__(self):
        self.calls = []

    def open_stream(self, url, headers, body, timeout, max_response_bytes):
        self.calls.append((url, headers, body, timeout, max_response_bytes))
        response = {
            "id": "resp_probe",
            "status": "completed",
            "model": "probe-model",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "1"}],
                }
            ],
        }
        events = [
            {"type": "response.output_text.delta", "delta": "1"},
            {"type": "response.output_text.done", "text": "1"},
            {"type": "response.completed", "response": response},
        ]
        raw = b"".join(
            (
                "data: {}\n\n".format(json.dumps(event, separators=(",", ":"))).encode(
                    "utf-8"
                )
                for event in events
            )
        )
        return HttpEventStream(FakeStreamingResponse(raw), max_response_bytes)


class AiRoutingConfigTests(unittest.TestCase):
    def test_parses_ordered_independent_model_profiles_and_redacts_repr(self):
        config = AiRoutingConfig.from_mapping(make_v3_settings())

        self.assertEqual(config.schema_version, 3)
        self.assertEqual(
            [profile.id for profile in config.models],
            ["fast-id", "middle-id", "complex-id"],
        )
        self.assertEqual(config.model_for_mode(AI_MODE_FAST).model, "fast-model")
        complex_profile = config.model_for_mode(AI_MODE_COMPLEX)
        self.assertEqual(complex_profile.base_url, "https://complex.example/v1")
        self.assertEqual(complex_profile.api_key, "complex-secret")
        self.assertNotIn("complex-secret", repr(complex_profile))
        self.assertEqual(config.to_mapping(), make_v3_settings())

    def test_v3_migration_is_a_deep_copy(self):
        settings = make_v3_settings()
        migrated = migrate_ai_settings(settings)

        migrated["models"][0]["model"] = "changed"

        self.assertEqual(settings["models"][0]["model"], "fast-model")

    def test_migrates_v1_to_one_profile_without_capturing_environment_key(self):
        migrated = migrate_ai_settings(make_v1_settings())

        self.assertEqual(migrated["schema_version"], 3)
        self.assertEqual(len(migrated["models"]), 1)
        profile = migrated["models"][0]
        self.assertEqual(profile["id"], "model_001")
        self.assertEqual(profile["model"], "legacy-model")
        self.assertEqual(profile["base_url"], "https://legacy.example/v1")
        self.assertEqual(profile["api_key"], "")
        self.assertEqual(profile["timeout_seconds"], 45)
        self.assertEqual(migrated["fast_model_id"], "model_001")
        self.assertEqual(migrated["complex_model_id"], "model_001")

    def test_migrates_v2_queues_to_ordered_profiles_and_drops_rotation(self):
        migrated = migrate_ai_settings(make_v2_settings())

        self.assertEqual(
            [profile["model"] for profile in migrated["models"]],
            ["fast-a", "shared", "complex-a"],
        )
        self.assertEqual(migrated["fast_model_id"], "model_001")
        self.assertEqual(migrated["complex_model_id"], "model_003")
        self.assertTrue(all(profile["api_key"] == "" for profile in migrated["models"]))
        serialized = json.dumps(migrated)
        self.assertNotIn("model_queues", serialized)
        self.assertNotIn("rotate_on_error", serialized)
        self.assertNotIn("default_mode", serialized)

    def test_rejects_invalid_profiles_and_dangling_mode_references(self):
        cases = []

        no_models = make_v3_settings()
        no_models["models"] = []
        cases.append(no_models)

        duplicate_ids = make_v3_settings()
        duplicate_ids["models"][1]["id"] = "fast-id"
        cases.append(duplicate_ids)

        dangling_fast = make_v3_settings()
        dangling_fast["fast_model_id"] = "missing"
        cases.append(dangling_fast)

        invalid_id = make_v3_settings()
        invalid_id["models"][0]["id"] = "bad id"
        cases.append(invalid_id)

        invalid_key = make_v3_settings()
        invalid_key["models"][0]["api_key"] = "secret with spaces"
        cases.append(invalid_key)

        unknown_root = make_v3_settings()
        unknown_root["rotate_on_error"] = True
        cases.append(unknown_root)

        unknown_profile = make_v3_settings()
        unknown_profile["models"][0]["unexpected"] = True
        cases.append(unknown_profile)

        for settings in cases:
            with self.subTest(settings=settings):
                with self.assertRaises(AiConfigurationError):
                    AiRoutingConfig.from_mapping(settings)

    def test_rejects_non_integer_versions_and_malformed_legacy_model_entries(self):
        for version in (3.0, "3", True):
            settings = make_v3_settings()
            settings["schema_version"] = version
            with self.subTest(version=version):
                with self.assertRaises(AiConfigurationError):
                    AiRoutingConfig.from_mapping(settings)

        malformed_v2 = make_v2_settings()
        malformed_v2["model_queues"]["fast"]["models"] = [["not-a-name"]]
        with self.assertRaises(AiConfigurationError):
            AiRoutingConfig.from_mapping(malformed_v2)

    def test_profile_creates_complete_client_config(self):
        profile = AiRoutingConfig.from_mapping(make_v3_settings()).model_by_id(
            "complex-id"
        )

        client_config = profile.client_config()

        self.assertEqual(client_config.model, "complex-model")
        self.assertEqual(client_config.base_url, "https://complex.example/v1")
        self.assertEqual(client_config.api_style, "chat_completions")
        self.assertEqual(client_config.timeout_seconds, 90)
        self.assertEqual(
            client_config.chat_token_parameter,
            "max_completion_tokens",
        )


class AiServiceTests(unittest.TestCase):
    def test_fast_and_complex_each_call_only_their_selected_profile(self):
        factory = FakeClientFactory(
            {
                "fast-id": ["fast"],
                "middle-id": ["must not run"],
                "complex-id": ["complex"],
            }
        )
        config = AiRoutingConfig.from_mapping(make_v3_settings())

        fast = AiService(config, client_factory=factory)
        complex_service = AiService(
            config,
            client_factory=factory,
            mode=AI_MODE_COMPLEX,
        )

        self.assertEqual(list(fast.stream("input")), ["fast"])
        self.assertEqual(list(complex_service.stream("input")), ["complex"])
        self.assertEqual(
            [profile.id for profile in factory.created],
            ["fast-id", "complex-id"],
        )

    def test_model_error_is_returned_without_trying_any_other_profile(self):
        timeout = AiTimeoutError("selected model timed out")
        factory = FakeClientFactory(
            {
                "fast-id": [timeout],
                "middle-id": ["must not run"],
                "complex-id": ["must not run"],
            }
        )
        service = AiService(
            AiRoutingConfig.from_mapping(make_v3_settings()),
            client_factory=factory,
        )

        with self.assertRaises(AiTimeoutError) as caught:
            list(service.stream("input"))

        self.assertIs(caught.exception, timeout)
        self.assertEqual(
            [profile.id for profile in factory.created],
            ["fast-id"],
        )

    def test_create_ai_service_defaults_to_fast_and_can_bind_complex(self):
        fast_factory = FakeClientFactory({"fast-id": ["fast"], "complex-id": ["wrong"]})
        complex_factory = FakeClientFactory(
            {"fast-id": ["wrong"], "complex-id": ["complex"]}
        )

        fast = create_ai_service(
            settings=make_v3_settings(),
            client_factory=fast_factory,
        )
        complex_service = create_ai_service(
            settings=make_v3_settings(),
            client_factory=complex_factory,
            mode=AI_MODE_COMPLEX,
        )

        self.assertEqual(list(fast.stream("input")), ["fast"])
        self.assertEqual(list(complex_service.stream("input")), ["complex"])

    def test_stream_callers_only_supply_input_and_optional_prompt_contract(self):
        parameters = inspect.signature(AiService.stream).parameters

        self.assertEqual(
            list(parameters),
            [
                "self",
                "input_data",
                "instructions",
                "response_schema",
                "schema_name",
            ],
        )
        for callable_object in (AiService.__init__, create_ai_service, test_ai_model):
            with self.subTest(callable_object=callable_object.__name__):
                self.assertNotIn(
                    "api_key", inspect.signature(callable_object).parameters
                )

    def test_generate_json_uses_selected_stream_and_validates_schema(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
            "additionalProperties": False,
        }
        factory = FakeClientFactory(
            {
                "fast-id": ['{"name":"node"}'],
                "middle-id": ["must not run"],
                "complex-id": ["must not run"],
            }
        )
        service = AiService(
            AiRoutingConfig.from_mapping(make_v3_settings()),
            client_factory=factory,
        )

        self.assertEqual(service.generate_json("input", schema), {"name": "node"})


class ModelProbeTests(unittest.TestCase):
    def test_probe_uses_exact_profile_stored_key_and_sends_one(self):
        transport = RecordingProbeTransport()

        result = test_ai_model(
            make_v3_settings()["models"][1],
            transport=transport,
            environ={},
        )

        self.assertIs(result, True)
        self.assertEqual(len(transport.calls), 1)
        url, headers, body, timeout, _ = transport.calls[0]
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(url, "https://middle.example/v1/responses")
        self.assertEqual(headers["Authorization"], "Bearer middle-secret")
        self.assertEqual(payload["model"], "middle-model")
        self.assertEqual(payload["input"], "1")
        self.assertIs(payload["stream"], True)
        self.assertEqual(payload["max_output_tokens"], 32)
        self.assertEqual(timeout, 20)


if __name__ == "__main__":
    unittest.main()
