import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from arnold_magic_node.tools.ai_credentials import (  # noqa: E402
    clear_all_session_api_keys,
    get_session_api_key,
    set_session_api_key,
)
try:  # Maya provides PySide; keep the standard-library suite runnable without it.
    from arnold_magic_node.ui._qt_compat import QtWidgets  # noqa: E402
except ImportError:  # pragma: no cover - depends on the test host
    QtWidgets = None

if QtWidgets is not None:
    from arnold_magic_node.ui.ai_settings_widget import (  # noqa: E402
        AiSettingsWidget,
    )
else:  # pragma: no cover - depends on the test host
    AiSettingsWidget = None


LANGUAGE = {
    "tab": "AI Settings",
    "connection_section": "Connection",
    "api_style_label": "API style",
    "responses_option": "Responses API",
    "chat_completions_option": "Chat Completions",
    "base_url_label": "Base URL",
    "model_label": "Model",
    "api_key_env_label": "API Key environment variable",
    "api_key_env_hint": "Only the variable name is saved.",
    "limits_section": "Limits",
    "timeout_seconds_label": "Timeout seconds",
    "max_output_tokens_label": "Maximum output tokens",
    "max_request_bytes_label": "Maximum request bytes",
    "max_response_bytes_label": "Maximum response bytes",
    "chat_token_parameter_label": "Chat token parameter",
    "session_key_section": "Session API Key",
    "session_key_label": "API Key",
    "session_key_placeholder": "Stored only for this Maya session",
    "session_key_hint": "The key is never written to disk.",
    "session_target": "Session key target: {origin}",
    "local_key_disabled": "Local HTTP never receives any API Key.",
    "session_configured": "Session key configured",
    "session_not_configured": "No session key",
    "environment_configured": "Environment variable {env} detected",
    "environment_not_configured": "Environment variable {env} not detected",
    "save_button": "Save AI settings",
    "clear_key_button": "Clear session key",
    "saved_message": "AI settings saved",
    "cleared_message": "Session key cleared",
    "error_prefix": "Unable to save AI settings: ",
}


@unittest.skipIf(QtWidgets is None, "PySide is unavailable outside Maya")
class AiSettingsWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = (
            QtWidgets.QApplication.instance()
            or QtWidgets.QApplication([])
        )

    def setUp(self):
        clear_all_session_api_keys()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.paths = SimpleNamespace(
            settings_path=str(Path(self.directory.name) / "settings")
        )
        self.environment = {}
        self.widget = AiSettingsWidget(
            paths=self.paths,
            language=LANGUAGE,
            environ=self.environment,
        )
        self.addCleanup(self.widget.close)
        self.addCleanup(clear_all_session_api_keys)

    def test_loads_persistent_fields_without_revealing_a_key(self):
        self.environment["OPENAI_API_KEY"] = "environment-secret"
        self.widget.refresh_credential_status()

        self.assertEqual(self.widget.api_style_combo.currentData(), "responses")
        self.assertEqual(
            self.widget.base_url_input.text(),
            "https://api.openai.com/v1",
        )
        self.assertEqual(self.widget.model_input.text(), "gpt-5.6-terra")
        self.assertEqual(
            self.widget.api_key_env_input.text(), "OPENAI_API_KEY"
        )
        self.assertEqual(self.widget.session_api_key_input.text(), "")
        self.assertEqual(
            self.widget.session_api_key_input.echoMode(),
            QtWidgets.QLineEdit.Password,
        )
        self.assertNotIn(
            "environment-secret", self.widget.credential_status_label.text()
        )
        self.assertIn(
            LANGUAGE["environment_configured"].format(env="OPENAI_API_KEY"),
            self.widget.credential_status_label.text(),
        )
        self.assertFalse(self.widget.chat_token_parameter_combo.isEnabled())

    def test_chat_style_enables_chat_token_parameter(self):
        chat_index = self.widget.api_style_combo.findData(
            "chat_completions"
        )

        self.widget.api_style_combo.setCurrentIndex(chat_index)

        self.assertTrue(self.widget.chat_token_parameter_combo.isEnabled())

    def test_save_persists_all_fields_but_keeps_key_in_session_only(self):
        self.widget.api_style_combo.setCurrentIndex(
            self.widget.api_style_combo.findData("chat_completions")
        )
        self.widget.base_url_input.setText(
            "https://compatible.example/v1"
        )
        self.widget.model_input.setText("compatible-model")
        self.widget.api_key_env_input.setText("COMPATIBLE_AI_KEY")
        self.widget.timeout_seconds_spin.setValue(45)
        self.widget.max_output_tokens_spin.setValue(2048)
        self.widget.max_request_bytes_spin.setValue(524288)
        self.widget.max_response_bytes_spin.setValue(1048576)
        self.widget.chat_token_parameter_combo.setCurrentIndex(
            self.widget.chat_token_parameter_combo.findData(
                "max_completion_tokens"
            )
        )
        self.widget.session_api_key_input.setText("session-secret")

        self.assertIn(
            "https://compatible.example:443",
            self.widget.session_target_label.text(),
        )
        self.widget.save_button.click()

        settings_path = Path(self.paths.settings_path) / "AI_Settings.json"
        persisted = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["api_style"], "chat_completions")
        self.assertEqual(persisted["base_url"], "https://compatible.example/v1")
        self.assertEqual(persisted["model"], "compatible-model")
        self.assertEqual(persisted["api_key_env"], "COMPATIBLE_AI_KEY")
        self.assertEqual(persisted["timeout_seconds"], 45)
        self.assertEqual(persisted["max_output_tokens"], 2048)
        self.assertEqual(persisted["max_request_bytes"], 524288)
        self.assertEqual(persisted["max_response_bytes"], 1048576)
        self.assertEqual(
            persisted["chat_token_parameter"], "max_completion_tokens"
        )
        self.assertNotIn("api_key", persisted)
        self.assertNotIn("session-secret", settings_path.read_text(encoding="utf-8"))
        self.assertEqual(self.environment, {})
        self.assertEqual(
            get_session_api_key("https://compatible.example/v2"),
            "session-secret",
        )
        self.assertEqual(self.widget.session_api_key_input.text(), "")
        self.assertNotIn("session-secret", self.widget.save_status_label.text())

    def test_invalid_remote_http_does_not_overwrite_settings_or_store_key(self):
        settings_path = Path(self.paths.settings_path) / "AI_Settings.json"
        original = settings_path.read_text(encoding="utf-8")
        self.widget.base_url_input.setText("http://api.example.com/v1")
        self.widget.session_api_key_input.setText("must-not-leak")

        self.widget.save_button.click()

        self.assertEqual(settings_path.read_text(encoding="utf-8"), original)
        self.assertIsNone(
            get_session_api_key("https://api.example.com/v1")
        )
        self.assertNotIn("must-not-leak", self.widget.save_status_label.text())
        self.assertTrue(self.widget.save_status_label.text().startswith(
            LANGUAGE["error_prefix"]
        ))

    def test_local_http_disables_session_key_and_clear_removes_old_origin(self):
        set_session_api_key(
            "https://api.openai.com/v1",
            "temporary-secret",
        )
        self.widget.refresh_credential_status()
        self.widget.base_url_input.setText("http://127.0.0.1:1234/v1")

        self.assertFalse(self.widget.session_api_key_input.isEnabled())
        self.assertEqual(
            self.widget.session_target_label.text(),
            LANGUAGE["local_key_disabled"],
        )

        self.widget.clear_session_key_button.click()

        self.assertIsNone(
            get_session_api_key("https://api.openai.com/v1")
        )
        self.assertNotIn(
            "temporary-secret", self.widget.credential_status_label.text()
        )

    def test_changing_https_origin_discards_an_unsaved_session_key(self):
        self.widget.session_api_key_input.setText("openai-only-secret")

        self.widget.base_url_input.setText("https://compatible.example/v1")

        self.assertEqual(self.widget.session_api_key_input.text(), "")
        self.widget.save_button.click()
        self.assertIsNone(
            get_session_api_key("https://compatible.example/v1")
        )

    def test_invalid_endpoint_discards_an_unsaved_session_key(self):
        self.widget.session_api_key_input.setText("openai-only-secret")

        self.widget.base_url_input.setText("not-a-url")

        self.assertEqual(self.widget.session_api_key_input.text(), "")
        self.widget.base_url_input.setText("https://compatible.example/v1")
        self.widget.save_button.click()
        self.assertIsNone(
            get_session_api_key("https://compatible.example/v1")
        )


if __name__ == "__main__":
    unittest.main()
