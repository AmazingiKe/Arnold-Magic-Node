"""设置窗口中的 AI 接口配置页。"""

from ..tools.ai_client import AiError
from ..tools.ai_credentials import (
    api_origin,
    clear_session_api_key,
    get_session_api_key,
    has_environment_api_key,
)
from ..tools.ai_settings import (
    load_ai_settings,
    save_ai_settings_with_session_key,
)
from ._qt_compat import QtCore, QtWidgets


class AiSettingsWidget(QtWidgets.QWidget):
    """编辑持久 AI 设置，并管理按 origin 隔离的会话密钥。"""

    def __init__(self, paths, language, environ=None, parent=None):
        super(AiSettingsWidget, self).__init__(parent)
        self.paths = paths
        self.language = language
        self.environ = environ
        self.settings = load_ai_settings(paths=paths)
        self._pending_session_key_origin = None

        self._create_widgets()
        self._create_layout()
        self._load_settings_into_widgets()
        self._connect_signals()
        self._update_chat_token_parameter_state()
        self.update_endpoint_state()

    def _create_widgets(self):
        self.api_style_combo = QtWidgets.QComboBox()
        self.api_style_combo.setObjectName("aiApiStyleCombo")
        self.api_style_combo.addItem(
            self.language["responses_option"], "responses"
        )
        self.api_style_combo.addItem(
            self.language["chat_completions_option"],
            "chat_completions",
        )

        self.base_url_input = QtWidgets.QLineEdit()
        self.base_url_input.setObjectName("aiBaseUrlInput")
        self.model_input = QtWidgets.QLineEdit()
        self.model_input.setObjectName("aiModelInput")
        self.api_key_env_input = QtWidgets.QLineEdit()
        self.api_key_env_input.setObjectName("aiApiKeyEnvInput")

        self.chat_token_parameter_combo = QtWidgets.QComboBox()
        self.chat_token_parameter_combo.setObjectName(
            "aiChatTokenParameterCombo"
        )
        self.chat_token_parameter_combo.addItem(
            "max_tokens", "max_tokens"
        )
        self.chat_token_parameter_combo.addItem(
            "max_completion_tokens", "max_completion_tokens"
        )

        self.timeout_seconds_spin = QtWidgets.QDoubleSpinBox()
        self.timeout_seconds_spin.setObjectName("aiTimeoutSecondsSpin")
        self.timeout_seconds_spin.setRange(1, 300)
        self.timeout_seconds_spin.setDecimals(1)
        self.timeout_seconds_spin.setSingleStep(1)

        self.max_output_tokens_spin = QtWidgets.QSpinBox()
        self.max_output_tokens_spin.setObjectName("aiMaxOutputTokensSpin")
        self.max_output_tokens_spin.setRange(1, 1000000)

        self.max_request_bytes_spin = QtWidgets.QSpinBox()
        self.max_request_bytes_spin.setObjectName("aiMaxRequestBytesSpin")
        self.max_request_bytes_spin.setRange(1, 10 * 1024 * 1024)
        self.max_request_bytes_spin.setSingleStep(64 * 1024)

        self.max_response_bytes_spin = QtWidgets.QSpinBox()
        self.max_response_bytes_spin.setObjectName("aiMaxResponseBytesSpin")
        self.max_response_bytes_spin.setRange(1, 10 * 1024 * 1024)
        self.max_response_bytes_spin.setSingleStep(64 * 1024)

        self.session_api_key_input = QtWidgets.QLineEdit()
        self.session_api_key_input.setObjectName("aiSessionApiKeyInput")
        self.session_api_key_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.session_api_key_input.setPlaceholderText(
            self.language["session_key_placeholder"]
        )

        self.session_target_label = QtWidgets.QLabel()
        self.session_target_label.setObjectName("aiSessionTargetLabel")
        self.session_target_label.setWordWrap(True)
        self.credential_status_label = QtWidgets.QLabel()
        self.credential_status_label.setObjectName(
            "aiCredentialStatusLabel"
        )
        self.credential_status_label.setWordWrap(True)

        self.save_button = QtWidgets.QPushButton(
            self.language["save_button"]
        )
        self.save_button.setObjectName("aiSaveButton")
        self.clear_session_key_button = QtWidgets.QPushButton(
            self.language["clear_key_button"]
        )
        self.clear_session_key_button.setObjectName(
            "aiClearSessionKeyButton"
        )
        self.save_status_label = QtWidgets.QLabel()
        self.save_status_label.setObjectName("aiSaveStatusLabel")
        self.save_status_label.setWordWrap(True)

    def _create_layout(self):
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setAlignment(QtCore.Qt.AlignTop)

        connection_group = QtWidgets.QGroupBox(
            self.language["connection_section"]
        )
        connection_form = QtWidgets.QFormLayout(connection_group)
        connection_form.addRow(
            self.language["api_style_label"], self.api_style_combo
        )
        connection_form.addRow(
            self.language["base_url_label"], self.base_url_input
        )
        connection_form.addRow(
            self.language["model_label"], self.model_input
        )
        connection_form.addRow(
            self.language["api_key_env_label"], self.api_key_env_input
        )
        api_key_env_hint = QtWidgets.QLabel(
            self.language["api_key_env_hint"]
        )
        api_key_env_hint.setWordWrap(True)
        connection_form.addRow(api_key_env_hint)
        connection_form.addRow(
            self.language["chat_token_parameter_label"],
            self.chat_token_parameter_combo,
        )
        content_layout.addWidget(connection_group)

        limits_group = QtWidgets.QGroupBox(self.language["limits_section"])
        limits_form = QtWidgets.QFormLayout(limits_group)
        limits_form.addRow(
            self.language["timeout_seconds_label"],
            self.timeout_seconds_spin,
        )
        limits_form.addRow(
            self.language["max_output_tokens_label"],
            self.max_output_tokens_spin,
        )
        limits_form.addRow(
            self.language["max_request_bytes_label"],
            self.max_request_bytes_spin,
        )
        limits_form.addRow(
            self.language["max_response_bytes_label"],
            self.max_response_bytes_spin,
        )
        content_layout.addWidget(limits_group)

        session_group = QtWidgets.QGroupBox(
            self.language["session_key_section"]
        )
        session_layout = QtWidgets.QVBoxLayout(session_group)
        session_form = QtWidgets.QFormLayout()
        session_form.addRow(
            self.language["session_key_label"],
            self.session_api_key_input,
        )
        session_layout.addLayout(session_form)
        session_hint = QtWidgets.QLabel(self.language["session_key_hint"])
        session_hint.setWordWrap(True)
        session_layout.addWidget(session_hint)
        session_layout.addWidget(self.session_target_label)
        session_layout.addWidget(self.credential_status_label)
        content_layout.addWidget(session_group)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.clear_session_key_button)
        button_layout.addWidget(self.save_button)
        content_layout.addLayout(button_layout)
        content_layout.addWidget(self.save_status_label)
        content_layout.addStretch(1)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content)
        root_layout = QtWidgets.QVBoxLayout(self)
        root_layout.addWidget(scroll_area)

    def _load_settings_into_widgets(self):
        self._set_combo_data(
            self.api_style_combo, self.settings["api_style"]
        )
        self.base_url_input.setText(self.settings["base_url"])
        self.model_input.setText(self.settings["model"])
        self.api_key_env_input.setText(self.settings["api_key_env"])
        self.timeout_seconds_spin.setValue(
            float(self.settings["timeout_seconds"])
        )
        self.max_output_tokens_spin.setValue(
            int(self.settings["max_output_tokens"])
        )
        self.max_request_bytes_spin.setValue(
            int(self.settings["max_request_bytes"])
        )
        self.max_response_bytes_spin.setValue(
            int(self.settings["max_response_bytes"])
        )
        self._set_combo_data(
            self.chat_token_parameter_combo,
            self.settings["chat_token_parameter"],
        )

    def _connect_signals(self):
        self.api_style_combo.currentIndexChanged.connect(
            lambda *args: self._update_chat_token_parameter_state()
        )
        self.base_url_input.textChanged.connect(
            lambda *args: self.update_endpoint_state()
        )
        self.api_key_env_input.textChanged.connect(
            lambda *args: self.refresh_credential_status()
        )
        self.session_api_key_input.textChanged.connect(
            self._track_pending_session_key_origin
        )
        self.save_button.clicked.connect(
            lambda *args: self.save_settings()
        )
        self.clear_session_key_button.clicked.connect(
            lambda *args: self.clear_session_key()
        )

    @staticmethod
    def _set_combo_data(combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _update_chat_token_parameter_state(self):
        self.chat_token_parameter_combo.setEnabled(
            self.api_style_combo.currentData() == "chat_completions"
        )

    def _track_pending_session_key_origin(self, api_key):
        if not api_key:
            self._pending_session_key_origin = None
            return

        try:
            origin = api_origin(self.base_url_input.text().strip())
        except AiError:
            self.session_api_key_input.clear()
            return

        if not origin.startswith("https://"):
            self.session_api_key_input.clear()
            return
        self._pending_session_key_origin = origin

    def update_endpoint_state(self):
        base_url = self.base_url_input.text().strip()
        try:
            origin = api_origin(base_url)
        except AiError:
            self.session_api_key_input.clear()
            self.session_api_key_input.setEnabled(False)
            self.session_target_label.setText(
                self.language["session_target"].format(origin="-")
            )
            self.refresh_credential_status()
            return

        if origin.startswith("http://"):
            self.session_api_key_input.clear()
            self.session_api_key_input.setEnabled(False)
            self.session_target_label.setText(
                self.language["local_key_disabled"]
            )
        else:
            if (
                self.session_api_key_input.text()
                and self._pending_session_key_origin != origin
            ):
                self.session_api_key_input.clear()
            self.session_api_key_input.setEnabled(True)
            self.session_target_label.setText(
                self.language["session_target"].format(origin=origin)
            )
        self.refresh_credential_status()

    def refresh_credential_status(self):
        base_url = self.base_url_input.text().strip()
        api_key_env = self.api_key_env_input.text().strip()
        try:
            session_configured = get_session_api_key(base_url) is not None
        except AiError:
            session_configured = False
        try:
            environment_configured = has_environment_api_key(
                api_key_env,
                environ=self.environ,
            )
        except AiError:
            environment_configured = False

        session_text = self.language[
            "session_configured"
            if session_configured
            else "session_not_configured"
        ]
        environment_text = self.language[
            "environment_configured"
            if environment_configured
            else "environment_not_configured"
        ].format(env=api_key_env or "-")
        self.credential_status_label.setText(
            "{}\n{}".format(session_text, environment_text)
        )

    def _collect_settings(self):
        timeout_seconds = self.timeout_seconds_spin.value()
        if timeout_seconds.is_integer():
            timeout_seconds = int(timeout_seconds)
        settings = dict(self.settings)
        settings.update(
            {
                "api_style": self.api_style_combo.currentData(),
                "base_url": self.base_url_input.text().strip(),
                "model": self.model_input.text().strip(),
                "api_key_env": self.api_key_env_input.text().strip(),
                "timeout_seconds": timeout_seconds,
                "max_output_tokens": self.max_output_tokens_spin.value(),
                "max_request_bytes": self.max_request_bytes_spin.value(),
                "max_response_bytes": self.max_response_bytes_spin.value(),
                "chat_token_parameter": (
                    self.chat_token_parameter_combo.currentData()
                ),
            }
        )
        return settings

    def _set_save_status(self, text, succeeded):
        color = "#8bc34a" if succeeded else "#ef5350"
        self.save_status_label.setStyleSheet("color: {};".format(color))
        self.save_status_label.setText(text)

    def save_settings(self):
        updated_settings = self._collect_settings()
        previous_base_url = self.settings["base_url"]
        api_key = self.session_api_key_input.text()
        try:
            save_ai_settings_with_session_key(
                updated_settings,
                previous_base_url=previous_base_url,
                api_key=api_key,
                paths=self.paths,
            )
        except (AiError, OSError, TypeError, ValueError) as error:
            self._set_save_status(
                self.language["error_prefix"] + str(error),
                False,
            )
            return False

        self.settings = updated_settings
        self.session_api_key_input.clear()
        self.update_endpoint_state()
        self._set_save_status(self.language["saved_message"], True)
        return True

    def clear_session_key(self):
        base_urls = {
            self.settings.get("base_url"),
            self.base_url_input.text().strip(),
        }
        cleared = False
        for base_url in base_urls:
            if not base_url:
                continue
            try:
                cleared = clear_session_api_key(base_url) or cleared
            except AiError:
                continue
        self.session_api_key_input.clear()
        self.refresh_credential_status()
        self._set_save_status(self.language["cleared_message"], True)
        return cleared


__all__ = ["AiSettingsWidget"]
