import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from arnold_magic_node.ui._qt_compat import QtCore, QtWidgets
    from arnold_magic_node.ui.ai_settings_widget import AiSettingsWidget
except ImportError:
    QtCore = None
    QtWidgets = None
    AiSettingsWidget = None


LANGUAGE = {
    "tab": "AI Settings",
    "models_section": "Models",
    "model_name_header": "Model",
    "model_input_placeholder": "Model name",
    "add_model_button": "Add",
    "remove_model_button": "Remove",
    "move_up_button": "Up",
    "move_down_button": "Down",
    "test_model_button": "Test selected model",
    "model_test_hint": 'Test sends "1" to this model.',
    "test_pending": "Testing",
    "test_success": "Available",
    "test_failed": "Failed",
    "selection_section": "Mode models",
    "fast_model_label": "Fast model",
    "complex_model_label": "Complex model",
    "editor_section": "Selected model configuration",
    "model_name_label": "Model name",
    "api_style_label": "OpenAI API protocol",
    "responses_option": "OpenAI Responses API",
    "chat_completions_option": "OpenAI Chat Completions",
    "base_url_label": "API website",
    "api_key_label": "API Key",
    "api_key_hint": "The key is stored as plaintext in AI_Settings.json.",
    "timeout_seconds_label": "Timeout",
    "max_output_tokens_label": "Maximum output tokens",
    "max_request_bytes_label": "Maximum request bytes",
    "max_response_bytes_label": "Maximum response bytes",
    "chat_token_parameter_label": "Chat token parameter",
    "save_button": "Save",
    "saved_message": "Saved",
    "error_prefix": "Error: ",
}


def make_model(
    model_id,
    model,
    base_url,
    api_key,
    api_style="responses",
    timeout_seconds=30,
    chat_token_parameter="max_tokens",
):
    return {
        "id": model_id,
        "model": model,
        "base_url": base_url,
        "api_style": api_style,
        "api_key": api_key,
        "timeout_seconds": timeout_seconds,
        "max_output_tokens": 2048,
        "max_request_bytes": 1024 * 1024,
        "max_response_bytes": 2 * 1024 * 1024,
        "chat_token_parameter": chat_token_parameter,
    }


V3_SETTINGS = {
    "schema_version": 3,
    "models": [
        make_model(
            "model-a",
            "fast-model",
            "https://fast.example/v1",
            "fast-plain-key",
        ),
        make_model(
            "model-b",
            "middle-model",
            "https://middle.example/v1",
            "middle-plain-key",
        ),
        make_model(
            "model-c",
            "complex-model",
            "https://complex.example/v1",
            "complex-plain-key",
            api_style="chat_completions",
            timeout_seconds=90,
            chat_token_parameter="max_completion_tokens",
        ),
    ],
    "fast_model_id": "model-a",
    "complex_model_id": "model-c",
}


class RecordingModelTester(object):
    def __init__(self, result=True, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def __call__(self, profile):
        self.calls.append(profile)
        if self.error is not None:
            raise self.error
        return self.result


class SynchronousRunner(object):
    def __call__(self, task, on_success, on_error):
        try:
            result = task()
        except Exception as error:  # noqa: BLE001 - UI error boundary test double
            on_error(error)
        else:
            on_success(result)


class DeferredRunner(object):
    def __init__(self):
        self.pending = []

    def __call__(self, task, on_success, on_error):
        self.pending.append((task, on_success, on_error))

    def succeed(self):
        task, on_success, _ = self.pending.pop(0)
        on_success(task())


def tree_models(tree):
    return [
        tree.topLevelItem(index).text(0) for index in range(tree.topLevelItemCount())
    ]


def combo_ids(combo):
    return [combo.itemData(index) for index in range(combo.count())]


@unittest.skipIf(QtWidgets is None, "PySide is unavailable outside Maya")
class AiSettingsWidgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
            []
        )

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.paths = SimpleNamespace(
            settings_path=str(Path(self.directory.name) / "settings")
        )
        self.settings_path = Path(self.paths.settings_path) / "AI_Settings.json"
        self.settings_path.parent.mkdir(parents=True)
        self.settings_path.write_text(json.dumps(V3_SETTINGS), encoding="utf-8")
        self.model_tester = RecordingModelTester()
        self.runner = SynchronousRunner()
        self.widget = AiSettingsWidget(
            paths=self.paths,
            language=LANGUAGE,
            model_tester=self.model_tester,
            background_runner=self.runner,
        )
        self.addCleanup(self.widget.close)

        self.tree = self._find(QtWidgets.QTreeWidget, "aiModelsTree")
        self.add_input = self._find(QtWidgets.QLineEdit, "aiNewModelNameInput")
        self.add_button = self._find(QtWidgets.QPushButton, "aiAddModelButton")
        self.remove_button = self._find(QtWidgets.QPushButton, "aiRemoveModelButton")
        self.up_button = self._find(QtWidgets.QPushButton, "aiMoveModelUpButton")
        self.down_button = self._find(QtWidgets.QPushButton, "aiMoveModelDownButton")
        self.test_button = self._find(
            QtWidgets.QPushButton, "aiTestSelectedModelButton"
        )
        self.test_status = self._find(QtWidgets.QLabel, "aiModelTestStatusLabel")
        self.fast_combo = self._find(QtWidgets.QComboBox, "aiFastModelCombo")
        self.complex_combo = self._find(QtWidgets.QComboBox, "aiComplexModelCombo")
        self.model_name = self._find(QtWidgets.QLineEdit, "aiModelNameInput")
        self.base_url = self._find(QtWidgets.QLineEdit, "aiModelBaseUrlInput")
        self.api_style = self._find(QtWidgets.QComboBox, "aiModelApiStyleCombo")
        self.api_key = self._find(QtWidgets.QLineEdit, "aiModelApiKeyInput")
        self.timeout = self._find(QtWidgets.QDoubleSpinBox, "aiModelTimeoutSecondsSpin")
        self.max_output = self._find(QtWidgets.QSpinBox, "aiModelMaxOutputTokensSpin")
        self.max_request = self._find(QtWidgets.QSpinBox, "aiModelMaxRequestBytesSpin")
        self.max_response = self._find(
            QtWidgets.QSpinBox, "aiModelMaxResponseBytesSpin"
        )
        self.chat_parameter = self._find(
            QtWidgets.QComboBox, "aiModelChatTokenParameterCombo"
        )

    def _find(self, widget_type, object_name):
        widget = self.widget.findChild(widget_type, object_name)
        self.assertIsNotNone(widget, object_name)
        return widget

    def _select(self, index):
        item = self.tree.topLevelItem(index)
        self.tree.setCurrentItem(item)
        return item

    def test_loads_one_ordered_name_list_two_single_selectors_and_profile_editor(self):
        self.assertEqual(self.tree.columnCount(), 1)
        self.assertEqual(
            tree_models(self.tree), ["fast-model", "middle-model", "complex-model"]
        )
        self.assertEqual(combo_ids(self.fast_combo), ["model-a", "model-b", "model-c"])
        self.assertEqual(
            combo_ids(self.complex_combo), ["model-a", "model-b", "model-c"]
        )
        self.assertEqual(self.fast_combo.currentData(), "model-a")
        self.assertEqual(self.complex_combo.currentData(), "model-c")

        self._select(2)

        self.assertEqual(self.model_name.text(), "complex-model")
        self.assertEqual(self.base_url.text(), "https://complex.example/v1")
        self.assertEqual(self.api_style.currentData(), "chat_completions")
        self.assertEqual(self.api_key.text(), "complex-plain-key")
        self.assertEqual(self.api_key.echoMode(), QtWidgets.QLineEdit.Password)
        self.assertEqual(self.timeout.value(), 90)
        self.assertEqual(self.chat_parameter.currentData(), "max_completion_tokens")
        self.assertTrue(self.chat_parameter.isEnabled())

    def test_old_queue_rotation_session_and_environment_controls_are_removed(self):
        removed_names = (
            "aiDefaultModeCombo",
            "aiFastModelsTree",
            "aiComplexModelsTree",
            "aiFastRotateCheckBox",
            "aiComplexRotateCheckBox",
            "aiApiKeyEnvInput",
            "aiSessionApiKeyInput",
            "aiClearSessionKeyButton",
        )
        for object_name in removed_names:
            with self.subTest(object_name=object_name):
                self.assertIsNone(self.widget.findChild(QtCore.QObject, object_name))

    def test_editing_selected_profile_updates_name_and_persists_plaintext_key(self):
        self._select(1)
        self.model_name.setText("renamed-model")
        self.base_url.setText("https://renamed.example/v1")
        self.api_key.setText("renamed-plain-secret")
        self.timeout.setValue(55)

        self.assertEqual(tree_models(self.tree)[1], "renamed-model")
        self.assertEqual(self.fast_combo.itemText(1), "renamed-model")
        self.assertEqual(self.complex_combo.itemText(1), "renamed-model")
        self.assertTrue(self.widget.save_settings())
        persisted_text = self.settings_path.read_text(encoding="utf-8")
        persisted = json.loads(persisted_text)

        self.assertEqual(persisted["models"][1]["id"], "model-b")
        self.assertEqual(persisted["models"][1]["model"], "renamed-model")
        self.assertEqual(
            persisted["models"][1]["base_url"], "https://renamed.example/v1"
        )
        self.assertEqual(persisted["models"][1]["api_key"], "renamed-plain-secret")
        self.assertIn("renamed-plain-secret", persisted_text)

    def test_add_and_reorder_keep_ids_and_mode_selections(self):
        self.add_input.setText("added-model")
        self.add_button.click()
        added_id = self.tree.currentItem().data(0, QtCore.Qt.UserRole)

        self.assertEqual(tree_models(self.tree)[-1], "added-model")
        self.assertEqual(combo_ids(self.fast_combo)[-1], added_id)
        self.fast_combo.setCurrentIndex(self.fast_combo.findData(added_id))
        self.complex_combo.setCurrentIndex(self.complex_combo.findData(added_id))

        self.up_button.click()
        self.up_button.click()

        self.assertEqual(tree_models(self.tree)[1], "added-model")
        self.assertEqual(combo_ids(self.fast_combo)[1], added_id)
        self.assertEqual(self.fast_combo.currentData(), added_id)
        self.assertEqual(self.complex_combo.currentData(), added_id)

    def test_delete_referenced_model_selects_nearest_replacement_for_both_modes(self):
        self.fast_combo.setCurrentIndex(self.fast_combo.findData("model-b"))
        self.complex_combo.setCurrentIndex(self.complex_combo.findData("model-b"))
        self._select(1)

        self.remove_button.click()

        self.assertEqual(tree_models(self.tree), ["fast-model", "complex-model"])
        self.assertEqual(self.fast_combo.currentData(), "model-c")
        self.assertEqual(self.complex_combo.currentData(), "model-c")

    def test_last_model_cannot_be_removed(self):
        self._select(2)
        self.remove_button.click()
        self._select(1)
        self.remove_button.click()
        self._select(0)

        self.assertEqual(self.tree.topLevelItemCount(), 1)
        self.assertFalse(self.remove_button.isEnabled())
        self.remove_button.click()
        self.assertEqual(self.tree.topLevelItemCount(), 1)

    def test_chat_parameter_only_enables_for_selected_chat_profile(self):
        self._select(0)
        self.assertFalse(self.chat_parameter.isEnabled())

        self.api_style.setCurrentIndex(self.api_style.findData("chat_completions"))
        self.assertTrue(self.chat_parameter.isEnabled())

        self.api_style.setCurrentIndex(self.api_style.findData("responses"))
        self.assertFalse(self.chat_parameter.isEnabled())

    def test_selected_model_test_uses_only_exact_plaintext_profile_snapshot(self):
        self._select(1)

        self.test_button.click()

        self.assertEqual(len(self.model_tester.calls), 1)
        selected = self.model_tester.calls[0]
        self.assertEqual(selected["id"], "model-b")
        self.assertEqual(selected["api_key"], "middle-plain-key")
        self.assertEqual(self.test_status.text(), "Available")
        self.assertNotIn("middle-plain-key", self.test_status.text())

    def test_model_test_failure_never_displays_raw_error_or_key(self):
        self.model_tester.error = RuntimeError(
            "provider leaked middle-plain-key and private response"
        )
        self._select(1)

        self.test_button.click()

        self.assertEqual(self.test_status.text(), "Failed")
        self.assertNotIn("middle-plain-key", self.test_status.text())
        self.assertNotIn("private response", self.test_status.text())

    def test_late_model_test_result_is_discarded_after_profile_change(self):
        deferred = DeferredRunner()
        self.widget.close()
        self.widget = AiSettingsWidget(
            paths=self.paths,
            language=LANGUAGE,
            model_tester=self.model_tester,
            background_runner=deferred,
        )
        self.addCleanup(self.widget.close)
        tree = self.widget.findChild(QtWidgets.QTreeWidget, "aiModelsTree")
        status = self.widget.findChild(QtWidgets.QLabel, "aiModelTestStatusLabel")
        tree.setCurrentItem(tree.topLevelItem(0))

        self.widget.findChild(
            QtWidgets.QPushButton, "aiTestSelectedModelButton"
        ).click()
        self.widget.findChild(QtWidgets.QLineEdit, "aiModelNameInput").setText(
            "changed-while-testing"
        )
        deferred.succeed()

        self.assertEqual(status.text(), "")

    def test_profile_change_during_probe_cannot_start_a_second_request(self):
        deferred = DeferredRunner()
        self.widget.close()
        self.widget = AiSettingsWidget(
            paths=self.paths,
            language=LANGUAGE,
            model_tester=self.model_tester,
            background_runner=deferred,
        )
        self.addCleanup(self.widget.close)
        tree = self.widget.findChild(QtWidgets.QTreeWidget, "aiModelsTree")
        test_button = self.widget.findChild(
            QtWidgets.QPushButton, "aiTestSelectedModelButton"
        )
        save_button = self.widget.findChild(QtWidgets.QPushButton, "aiSaveButton")
        tree.setCurrentItem(tree.topLevelItem(0))

        test_button.click()
        self.widget.findChild(QtWidgets.QLineEdit, "aiModelNameInput").setText(
            "changed-while-testing"
        )
        test_button.click()

        self.assertEqual(len(deferred.pending), 1)
        self.assertFalse(test_button.isEnabled())
        self.assertFalse(save_button.isEnabled())
        deferred.succeed()
        self.assertTrue(test_button.isEnabled())

    def test_save_reloads_backend_normalized_profile_values_into_ui(self):
        self._select(0)
        self.model_name.setText("  trimmed-model  ")
        self.api_key.setText("  trimmed-secret  ")

        self.assertTrue(self.widget.save_settings())
        persisted = json.loads(self.settings_path.read_text(encoding="utf-8"))

        self.assertEqual(self.model_name.text(), "trimmed-model")
        self.assertEqual(tree_models(self.tree)[0], "trimmed-model")
        self.assertEqual(self.api_key.text(), "trimmed-secret")
        self.assertEqual(persisted["models"][0]["model"], "trimmed-model")
        self.assertEqual(persisted["models"][0]["api_key"], "trimmed-secret")

    def test_dangling_mode_references_are_repaired_to_first_visible_model(self):
        broken = dict(V3_SETTINGS)
        broken["fast_model_id"] = "missing-fast"
        broken["complex_model_id"] = "missing-complex"
        self.settings_path.write_text(json.dumps(broken), encoding="utf-8")
        self.widget.close()
        self.widget = AiSettingsWidget(
            paths=self.paths,
            language=LANGUAGE,
            model_tester=self.model_tester,
            background_runner=self.runner,
        )
        self.addCleanup(self.widget.close)
        fast_combo = self.widget.findChild(QtWidgets.QComboBox, "aiFastModelCombo")
        complex_combo = self.widget.findChild(
            QtWidgets.QComboBox, "aiComplexModelCombo"
        )

        self.assertEqual(fast_combo.currentData(), "model-a")
        self.assertEqual(complex_combo.currentData(), "model-a")
        self.assertTrue(self.widget.save_settings())
        persisted = json.loads(self.settings_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["fast_model_id"], "model-a")
        self.assertEqual(persisted["complex_model_id"], "model-a")


if __name__ == "__main__":
    unittest.main()
