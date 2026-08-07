"""设置窗口中的有序 AI 模型配置页。"""

import copy
import threading
import uuid

from ..tools.ai_client import AiError
from ..tools.ai_routing import AiRoutingConfig, MAX_MODELS, test_ai_model
from ..tools.ai_settings import load_ai_settings, save_ai_settings
from ._qt_compat import QtCore, QtWidgets


class _AsyncDispatcher(QtCore.QObject):
    """把后台线程的无敏感结果安全派发回 Qt 主线程。"""

    dispatch = QtCore.Signal(object, object)

    def __init__(self, parent=None):
        super(_AsyncDispatcher, self).__init__(parent)
        self.dispatch.connect(self._invoke)

    @QtCore.Slot(object, object)
    def _invoke(self, callback, value):
        callback(value)


class AiSettingsWidget(QtWidgets.QWidget):
    """编辑独立模型配置，并为 fast/complex 各绑定一个模型。"""

    def __init__(
        self,
        paths,
        language,
        environ=None,
        model_tester=None,
        background_runner=None,
        parent=None,
    ):
        super(AiSettingsWidget, self).__init__(parent)
        self.paths = paths
        self.language = language
        self.environ = environ
        self.settings = load_ai_settings(paths=paths)
        self._models = copy.deepcopy(self.settings["models"])
        self._fast_model_id = self.settings["fast_model_id"]
        self._complex_model_id = self.settings["complex_model_id"]
        self._loading_editor = False
        self._model_test_in_progress = False
        self._model_test_generation = 0
        self._next_model_test_id = 0
        self._active_model_test_id = None
        self._async_dispatcher = _AsyncDispatcher(self)
        self._model_tester = model_tester or self._test_model
        self._background_runner = background_runner or self._run_in_background

        self._create_widgets()
        self._create_layout()
        self._load_settings_into_widgets()
        self._connect_signals()
        self._update_controls()

    def _create_widgets(self):
        self.models_tree = QtWidgets.QTreeWidget()
        self.models_tree.setObjectName("aiModelsTree")
        self.models_tree.setColumnCount(1)
        self.models_tree.setHeaderLabels([self.language["model_name_header"]])

        self.new_model_name_input = QtWidgets.QLineEdit()
        self.new_model_name_input.setObjectName("aiNewModelNameInput")
        self.new_model_name_input.setPlaceholderText(
            self.language["model_input_placeholder"]
        )
        self.add_model_button = QtWidgets.QPushButton(self.language["add_model_button"])
        self.add_model_button.setObjectName("aiAddModelButton")
        self.remove_model_button = QtWidgets.QPushButton(
            self.language["remove_model_button"]
        )
        self.remove_model_button.setObjectName("aiRemoveModelButton")
        self.move_up_button = QtWidgets.QPushButton(self.language["move_up_button"])
        self.move_up_button.setObjectName("aiMoveModelUpButton")
        self.move_down_button = QtWidgets.QPushButton(self.language["move_down_button"])
        self.move_down_button.setObjectName("aiMoveModelDownButton")
        self.test_model_button = QtWidgets.QPushButton(
            self.language["test_model_button"]
        )
        self.test_model_button.setObjectName("aiTestSelectedModelButton")
        self.model_test_status_label = QtWidgets.QLabel("")
        self.model_test_status_label.setObjectName("aiModelTestStatusLabel")

        self.fast_model_combo = QtWidgets.QComboBox()
        self.fast_model_combo.setObjectName("aiFastModelCombo")
        self.complex_model_combo = QtWidgets.QComboBox()
        self.complex_model_combo.setObjectName("aiComplexModelCombo")

        self.model_name_input = QtWidgets.QLineEdit()
        self.model_name_input.setObjectName("aiModelNameInput")
        self.model_base_url_input = QtWidgets.QLineEdit()
        self.model_base_url_input.setObjectName("aiModelBaseUrlInput")
        self.model_api_style_combo = QtWidgets.QComboBox()
        self.model_api_style_combo.setObjectName("aiModelApiStyleCombo")
        self.model_api_style_combo.addItem(
            self.language["responses_option"], "responses"
        )
        self.model_api_style_combo.addItem(
            self.language["chat_completions_option"], "chat_completions"
        )
        self.model_api_key_input = QtWidgets.QLineEdit()
        self.model_api_key_input.setObjectName("aiModelApiKeyInput")
        self.model_api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.model_timeout_seconds_spin = QtWidgets.QDoubleSpinBox()
        self.model_timeout_seconds_spin.setObjectName("aiModelTimeoutSecondsSpin")
        self.model_timeout_seconds_spin.setRange(1, 300)
        self.model_timeout_seconds_spin.setDecimals(1)
        self.model_timeout_seconds_spin.setSingleStep(1)

        self.model_max_output_tokens_spin = QtWidgets.QSpinBox()
        self.model_max_output_tokens_spin.setObjectName("aiModelMaxOutputTokensSpin")
        self.model_max_output_tokens_spin.setRange(1, 1000000)
        self.model_max_request_bytes_spin = QtWidgets.QSpinBox()
        self.model_max_request_bytes_spin.setObjectName("aiModelMaxRequestBytesSpin")
        self.model_max_request_bytes_spin.setRange(1, 10 * 1024 * 1024)
        self.model_max_response_bytes_spin = QtWidgets.QSpinBox()
        self.model_max_response_bytes_spin.setObjectName("aiModelMaxResponseBytesSpin")
        self.model_max_response_bytes_spin.setRange(1, 10 * 1024 * 1024)
        self.model_chat_token_parameter_combo = QtWidgets.QComboBox()
        self.model_chat_token_parameter_combo.setObjectName(
            "aiModelChatTokenParameterCombo"
        )
        self.model_chat_token_parameter_combo.addItem("max_tokens", "max_tokens")
        self.model_chat_token_parameter_combo.addItem(
            "max_completion_tokens", "max_completion_tokens"
        )

        self.save_button = QtWidgets.QPushButton(self.language["save_button"])
        self.save_button.setObjectName("aiSaveButton")
        self.save_status_label = QtWidgets.QLabel("")
        self.save_status_label.setObjectName("aiSaveStatusLabel")

    def _create_layout(self):
        root_layout = QtWidgets.QVBoxLayout(self)

        models_group = QtWidgets.QGroupBox(self.language["models_section"])
        models_layout = QtWidgets.QVBoxLayout(models_group)
        models_layout.addWidget(self.models_tree)

        add_layout = QtWidgets.QHBoxLayout()
        add_layout.addWidget(self.new_model_name_input)
        add_layout.addWidget(self.add_model_button)
        models_layout.addLayout(add_layout)

        order_layout = QtWidgets.QHBoxLayout()
        order_layout.addWidget(self.remove_model_button)
        order_layout.addWidget(self.move_up_button)
        order_layout.addWidget(self.move_down_button)
        order_layout.addStretch(1)
        models_layout.addLayout(order_layout)

        test_layout = QtWidgets.QHBoxLayout()
        test_layout.addWidget(self.test_model_button)
        test_layout.addWidget(self.model_test_status_label)
        test_layout.addStretch(1)
        models_layout.addLayout(test_layout)
        test_hint = QtWidgets.QLabel(self.language["model_test_hint"])
        test_hint.setWordWrap(True)
        models_layout.addWidget(test_hint)

        selection_group = QtWidgets.QGroupBox(self.language["selection_section"])
        selection_layout = QtWidgets.QFormLayout(selection_group)
        selection_layout.addRow(
            self.language["fast_model_label"], self.fast_model_combo
        )
        selection_layout.addRow(
            self.language["complex_model_label"], self.complex_model_combo
        )

        editor_group = QtWidgets.QGroupBox(self.language["editor_section"])
        self.editor_group = editor_group
        editor_layout = QtWidgets.QFormLayout(editor_group)
        editor_layout.addRow(self.language["model_name_label"], self.model_name_input)
        editor_layout.addRow(
            self.language["api_style_label"], self.model_api_style_combo
        )
        editor_layout.addRow(self.language["base_url_label"], self.model_base_url_input)
        editor_layout.addRow(self.language["api_key_label"], self.model_api_key_input)
        api_key_hint = QtWidgets.QLabel(self.language["api_key_hint"])
        api_key_hint.setWordWrap(True)
        editor_layout.addRow(api_key_hint)
        editor_layout.addRow(
            self.language["timeout_seconds_label"],
            self.model_timeout_seconds_spin,
        )
        editor_layout.addRow(
            self.language["max_output_tokens_label"],
            self.model_max_output_tokens_spin,
        )
        editor_layout.addRow(
            self.language["max_request_bytes_label"],
            self.model_max_request_bytes_spin,
        )
        editor_layout.addRow(
            self.language["max_response_bytes_label"],
            self.model_max_response_bytes_spin,
        )
        editor_layout.addRow(
            self.language["chat_token_parameter_label"],
            self.model_chat_token_parameter_combo,
        )

        body_layout = QtWidgets.QHBoxLayout()
        body_layout.addWidget(models_group, 1)
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(selection_group)
        right_layout.addWidget(editor_group)
        right_layout.addStretch(1)
        body_layout.addLayout(right_layout, 2)
        root_layout.addLayout(body_layout)

        save_layout = QtWidgets.QHBoxLayout()
        save_layout.addWidget(self.save_button)
        save_layout.addWidget(self.save_status_label)
        save_layout.addStretch(1)
        root_layout.addLayout(save_layout)

    def _connect_signals(self):
        self.models_tree.currentItemChanged.connect(self._on_selection_changed)
        self.new_model_name_input.returnPressed.connect(self.add_model)
        self.add_model_button.clicked.connect(self.add_model)
        self.remove_model_button.clicked.connect(self.remove_selected_model)
        self.move_up_button.clicked.connect(lambda *args: self.move_selected_model(-1))
        self.move_down_button.clicked.connect(lambda *args: self.move_selected_model(1))
        self.test_model_button.clicked.connect(self.test_selected_model)
        self.fast_model_combo.currentIndexChanged.connect(self._on_fast_model_changed)
        self.complex_model_combo.currentIndexChanged.connect(
            self._on_complex_model_changed
        )
        self.model_name_input.textChanged.connect(self._update_selected_profile)
        self.model_base_url_input.textChanged.connect(self._update_selected_profile)
        self.model_api_key_input.textChanged.connect(self._update_selected_profile)
        self.model_api_style_combo.currentIndexChanged.connect(
            self._update_selected_profile
        )
        self.model_timeout_seconds_spin.valueChanged.connect(
            self._update_selected_profile
        )
        self.model_max_output_tokens_spin.valueChanged.connect(
            self._update_selected_profile
        )
        self.model_max_request_bytes_spin.valueChanged.connect(
            self._update_selected_profile
        )
        self.model_max_response_bytes_spin.valueChanged.connect(
            self._update_selected_profile
        )
        self.model_chat_token_parameter_combo.currentIndexChanged.connect(
            self._update_selected_profile
        )
        self.save_button.clicked.connect(self.save_settings)

    @staticmethod
    def _set_combo_data(combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _load_settings_into_widgets(self):
        self._rebuild_model_views(self._models[0]["id"])

    def _rebuild_model_views(self, selected_id):
        model_ids = [profile["id"] for profile in self._models]
        if model_ids:
            if self._fast_model_id not in model_ids:
                self._fast_model_id = model_ids[0]
            if self._complex_model_id not in model_ids:
                self._complex_model_id = model_ids[0]
        self.models_tree.blockSignals(True)
        self.fast_model_combo.blockSignals(True)
        self.complex_model_combo.blockSignals(True)
        try:
            self.models_tree.clear()
            self.fast_model_combo.clear()
            self.complex_model_combo.clear()
            selected_item = None
            for profile in self._models:
                item = QtWidgets.QTreeWidgetItem([profile["model"]])
                item.setData(0, QtCore.Qt.UserRole, profile["id"])
                self.models_tree.addTopLevelItem(item)
                self.fast_model_combo.addItem(profile["model"], profile["id"])
                self.complex_model_combo.addItem(profile["model"], profile["id"])
                if profile["id"] == selected_id:
                    selected_item = item
            self._set_combo_data(self.fast_model_combo, self._fast_model_id)
            self._set_combo_data(self.complex_model_combo, self._complex_model_id)
            if selected_item is None and self.models_tree.topLevelItemCount():
                selected_item = self.models_tree.topLevelItem(0)
            self.models_tree.setCurrentItem(selected_item)
        finally:
            self.models_tree.blockSignals(False)
            self.fast_model_combo.blockSignals(False)
            self.complex_model_combo.blockSignals(False)
        self._load_selected_profile()
        self._update_controls()

    def _current_model_id(self):
        item = self.models_tree.currentItem()
        if item is None:
            return None
        return item.data(0, QtCore.Qt.UserRole)

    def _profile_by_id(self, model_id):
        for profile in self._models:
            if profile["id"] == model_id:
                return profile
        return None

    def _current_profile(self):
        return self._profile_by_id(self._current_model_id())

    def _current_index(self):
        model_id = self._current_model_id()
        for index, profile in enumerate(self._models):
            if profile["id"] == model_id:
                return index
        return -1

    def _on_selection_changed(self, current, previous):
        del current, previous
        self._invalidate_model_test()
        self._load_selected_profile()
        self._update_controls()

    def _load_selected_profile(self):
        profile = self._current_profile()
        self._loading_editor = True
        try:
            if profile is None:
                self.model_name_input.clear()
                self.model_base_url_input.clear()
                self.model_api_key_input.clear()
                return
            self.model_name_input.setText(profile["model"])
            self.model_base_url_input.setText(profile["base_url"])
            self._set_combo_data(self.model_api_style_combo, profile["api_style"])
            self.model_api_key_input.setText(profile["api_key"])
            self.model_timeout_seconds_spin.setValue(profile["timeout_seconds"])
            self.model_max_output_tokens_spin.setValue(profile["max_output_tokens"])
            self.model_max_request_bytes_spin.setValue(profile["max_request_bytes"])
            self.model_max_response_bytes_spin.setValue(profile["max_response_bytes"])
            self._set_combo_data(
                self.model_chat_token_parameter_combo,
                profile["chat_token_parameter"],
            )
        finally:
            self._loading_editor = False
        self._update_chat_token_parameter_state()

    def _update_selected_profile(self, *args):
        del args
        if self._loading_editor:
            return
        profile = self._current_profile()
        if profile is None:
            return
        profile.update(
            {
                "model": self.model_name_input.text(),
                "base_url": self.model_base_url_input.text(),
                "api_style": self.model_api_style_combo.currentData(),
                "api_key": self.model_api_key_input.text(),
                "timeout_seconds": self.model_timeout_seconds_spin.value(),
                "max_output_tokens": self.model_max_output_tokens_spin.value(),
                "max_request_bytes": self.model_max_request_bytes_spin.value(),
                "max_response_bytes": self.model_max_response_bytes_spin.value(),
                "chat_token_parameter": (
                    self.model_chat_token_parameter_combo.currentData()
                ),
            }
        )
        current_item = self.models_tree.currentItem()
        if current_item is not None:
            current_item.setText(0, profile["model"])
        for combo in (self.fast_model_combo, self.complex_model_combo):
            index = combo.findData(profile["id"])
            if index >= 0:
                combo.setItemText(index, profile["model"])
        self._update_chat_token_parameter_state()
        self._invalidate_model_test()

    def _update_chat_token_parameter_state(self):
        self.model_chat_token_parameter_combo.setEnabled(
            self._current_profile() is not None
            and self.model_api_style_combo.currentData() == "chat_completions"
        )

    def _on_fast_model_changed(self, index):
        del index
        model_id = self.fast_model_combo.currentData()
        if model_id is not None:
            self._fast_model_id = model_id

    def _on_complex_model_changed(self, index):
        del index
        model_id = self.complex_model_combo.currentData()
        if model_id is not None:
            self._complex_model_id = model_id

    @staticmethod
    def _new_model_profile(name):
        return {
            "id": "model_{}".format(uuid.uuid4().hex),
            "model": name,
            "base_url": "https://api.openai.com/v1",
            "api_style": "responses",
            "api_key": "",
            "timeout_seconds": 60,
            "max_output_tokens": 4096,
            "max_request_bytes": 1024 * 1024,
            "max_response_bytes": 2 * 1024 * 1024,
            "chat_token_parameter": "max_tokens",
        }

    def add_model(self, *args):
        del args
        name = self.new_model_name_input.text().strip()
        if not name or len(self._models) >= MAX_MODELS:
            return False
        profile = self._new_model_profile(name)
        self._models.append(profile)
        self.new_model_name_input.clear()
        self._invalidate_model_test()
        self._rebuild_model_views(profile["id"])
        return True

    def remove_selected_model(self, *args):
        del args
        index = self._current_index()
        if index < 0 or len(self._models) <= 1:
            return False
        removed = self._models.pop(index)
        replacement = self._models[min(index, len(self._models) - 1)]
        if self._fast_model_id == removed["id"]:
            self._fast_model_id = replacement["id"]
        if self._complex_model_id == removed["id"]:
            self._complex_model_id = replacement["id"]
        self._invalidate_model_test()
        self._rebuild_model_views(replacement["id"])
        return True

    def move_selected_model(self, offset):
        index = self._current_index()
        destination = index + offset
        if index < 0 or destination < 0 or destination >= len(self._models):
            return False
        profile = self._models.pop(index)
        self._models.insert(destination, profile)
        self._invalidate_model_test()
        self._rebuild_model_views(profile["id"])
        return True

    def _test_model(self, profile):
        return test_ai_model(profile, environ=self.environ)

    def _run_in_background(self, task, on_success, on_error):
        dispatcher = self._async_dispatcher

        def dispatch(callback, value):
            try:
                dispatcher.dispatch.emit(callback, value)
            except RuntimeError:
                # 窗口可能在请求结束前已被 Qt 销毁。
                pass

        def worker():
            try:
                result = task()
            except Exception:  # noqa: BLE001 - Qt 边界只回传无敏感失败状态
                dispatch(on_error, None)
            else:
                dispatch(on_success, result)

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def test_selected_model(self, *args):
        del args
        profile = self._current_profile()
        if profile is None or self._model_test_in_progress:
            return False
        snapshot = copy.deepcopy(profile)
        selected_id = snapshot["id"]
        generation = self._model_test_generation
        self._next_model_test_id += 1
        job_id = self._next_model_test_id
        self._active_model_test_id = job_id
        self._model_test_in_progress = True
        self.model_test_status_label.setText(self.language["test_pending"])
        self._update_controls()

        def task():
            return self._model_tester(snapshot)

        self._background_runner(
            task,
            lambda result: self._finish_model_test(
                job_id, generation, selected_id, bool(result)
            ),
            lambda error: self._finish_model_test(
                job_id, generation, selected_id, False
            ),
        )
        return True

    def _finish_model_test(self, job_id, generation, selected_id, succeeded):
        if job_id != self._active_model_test_id:
            return
        self._active_model_test_id = None
        self._model_test_in_progress = False
        if (
            generation == self._model_test_generation
            and selected_id == self._current_model_id()
        ):
            self.model_test_status_label.setText(
                self.language["test_success"]
                if succeeded
                else self.language["test_failed"]
            )
        self._update_controls()

    def _invalidate_model_test(self):
        self._model_test_generation += 1
        self.model_test_status_label.clear()
        self._update_controls()

    def _update_controls(self):
        if not hasattr(self, "models_tree"):
            return
        index = self._current_index()
        has_selection = index >= 0
        idle = not self._model_test_in_progress
        self.add_model_button.setEnabled(idle and len(self._models) < MAX_MODELS)
        self.remove_model_button.setEnabled(
            idle and has_selection and len(self._models) > 1
        )
        self.move_up_button.setEnabled(idle and has_selection and index > 0)
        self.move_down_button.setEnabled(
            idle and has_selection and index < len(self._models) - 1
        )
        self.test_model_button.setEnabled(idle and has_selection)
        self.save_button.setEnabled(idle)
        self.editor_group.setEnabled(has_selection)

    def _collect_settings(self):
        return {
            "schema_version": 3,
            "models": copy.deepcopy(self._models),
            "fast_model_id": self._fast_model_id,
            "complex_model_id": self._complex_model_id,
        }

    def _set_save_status(self, message, success):
        color = "#2e7d32" if success else "#c62828"
        self.save_status_label.setStyleSheet("color: {};".format(color))
        self.save_status_label.setText(message)

    def save_settings(self, *args):
        del args
        updated_settings = self._collect_settings()
        selected_id = self._current_model_id()
        try:
            normalized = AiRoutingConfig.from_mapping(updated_settings).to_mapping()
            save_ai_settings(normalized, paths=self.paths)
        except (AiError, OSError, TypeError, ValueError) as error:
            self._set_save_status(self.language["error_prefix"] + str(error), False)
            return False
        self.settings = copy.deepcopy(normalized)
        self._models = copy.deepcopy(normalized["models"])
        self._fast_model_id = normalized["fast_model_id"]
        self._complex_model_id = normalized["complex_model_id"]
        self._rebuild_model_views(selected_id)
        self._set_save_status(self.language["saved_message"], True)
        return True


__all__ = ["AiSettingsWidget"]
