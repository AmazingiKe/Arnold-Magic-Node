"""Arnold Magic Node 设置窗口。"""

import os
import shutil

from .. import default_config
from ..application import (
    AMS_Config,
    MAYA_ALT_MODIFIER,
    SMALL_FONT_SIZE,
    SoftwareState,
    SoftwareVersion,
    icon_path,
    is_modifier_pressed,
    language_loading,
    pluginFeedbackURL,
    pluginHelpDocumentURL,
    pluginHomeURL,
    pluginUpdateDownloadURL,
    settings_presets_path,
    settings_path,
)
from ..arnold_magic_core import (
    DataManager,
    FeedbackPrompt,
    PathDetection,
    process_sl_data,
)
from ..core.storage import ensure_directory
from ..core.paths import LANGUAGES_ROOT
from .qt import QAction, QtCore, QtGui, QtWidgets
from .workspace import delete_window_if_existe


class ArnoldMagicNodeSettingsPanel(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ArnoldMagicNodeSettingsPanel, self).__init__(parent)

        # 0. 初始化全局配置
        self.initial_global_config()

        # 1. 初始化窗口配置
        self.initialize_window_config()

        # 2. 创建菜单
        self.create_menu()

        # 3. 创建控件
        self.create_widgets()

        # 4. 创建布局
        self.create_layouts()

        # 5. 初始化控件
        self.initial_widgets_settings()

        # 显示窗口
        self.show()


    def initial_global_config(self):
        ### 实例各种模块

        self.dataM = DataManager()  # 数据管理模块

        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块

        ### 初始化配置数据
        self.config = self.dataM.load_json(
           os.path.normpath(os.path.join(settings_path, AMS_Config)))

        # 加载语言配置
        self.language = language_loading()['ArnoldMagicNode']['AMNSP_WIN']


        self.languages_folder_path = os.path.normpath(str(LANGUAGES_ROOT))  # 只读语言资源路径

    def initialize_window_config(self):

        WINDOWS_NAME = f"{self.language['initialize_window_config']['WINDOWS_NAME']}  {SoftwareState} : {SoftwareVersion}"  # Win名称

        delete_window_if_existe('ArnoldMagicNodeSettingsPanel')

        self.setObjectName('ArnoldMagicNodeSettingsPanel')
        self.setWindowTitle(WINDOWS_NAME)
        self.setWindowIcon(QtGui.QIcon(icon_path + "\\Logo_B.svg"))

        #...窗口长宽
        self.setMinimumHeight(800)
        self.setMinimumWidth(700)

    def create_menu(self):
        # 创建主菜单栏
        self.main_menu_bar = QtWidgets.QMenuBar(self)

        # 设置菜单及其动作
        self.settings_menu = self.main_menu_bar.addMenu(self.language['create_menu']['settings_menu']) # 设置

        # 创建“重置数据”动作
        self.reset_data_action = QAction(self.language['create_menu']['reset_data_action'], self) # 重置设置数据
        # 连接“重置数据”动作的触发信号到对应的槽函数
        self.reset_data_action.triggered.connect(lambda *args: (os.remove(os.path.join(settings_path, AMS_Config)),
                                                          default_config.Main_program()))


        self.settings_menu.addAction(self.reset_data_action)
        # 创建“语言设置”动作




        self.settings_presets_menu = QtWidgets.QMenu("预设", self)
        # 把它插入 menubar
        self.main_menu_bar.addMenu(self.settings_presets_menu)

        ensure_directory(settings_presets_path)

        # 遍历预设文件夹，获取所有预设文件名
        preset_files = [
            file_name
            for file_name in os.listdir(settings_presets_path)
            if file_name.lower().endswith(".json")
        ]
        # 遍历预设文件名列表，创建菜单项

        for preset_file in preset_files:
            preset_name = os.path.splitext(preset_file)[0]  # 去掉文件扩展名
            action = QAction(preset_name, self)
            self.settings_presets_menu.addAction(action)
            # 把默认参数 pf 传进去，body 只用 pf
            action.triggered.connect(lambda *args, pf=preset_name: self.load_settings_preset(pf))








        # —— 关键在这里 ——
        # 让这个 QMenu 自己响应右键
        # 为“预设”子菜单启用自定义上下文菜单策略，
        # 使其在用户右键点击时发出 customContextMenuRequested 信号
        self.settings_presets_menu.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # 将 customContextMenuRequested 信号连接到自定义的槽函数 on_settings_presets_context_menu
        # 当用户在 settings_presets_menu 内部右键时，Qt 会调用该槽并传入点击位置
        self.settings_presets_menu.customContextMenuRequested.connect(self.on_settings_presets_context_menu)

        # 关于菜单及其动作
        self.about_menu = self.main_menu_bar.addMenu(self.language['create_menu']['about_menu']) # 关于

        # 创建 插件主页菜单
        self.plugin_home = QAction(self.language['create_menu']['plugin_home'], self) # 插件主页
        self.plugin_home.triggered.connect(
            lambda *args:  QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginHomeURL)))

        # 创建 帮助/反馈菜单
        self.contact_feedback_action = QAction(self.language['create_menu']['contact_feedback_action'], self) # 联系/反馈
        self.contact_feedback_action.triggered.connect(
            lambda *args:  QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginFeedbackURL)))

        # 创建“帮助文档”动作并连接到打开帮助文档的槽函数
        self.help_document_action = QAction(self.language['create_menu']['help_document_action'], self) # 帮助文档
        self.help_document_action.triggered.connect(
            lambda *args: QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginHelpDocumentURL)))

        self.plugin_update_download_action = QAction(self.language['create_menu']['plugin_update_download_action'], self) # 插件更新下载
        self.plugin_update_download_action.triggered.connect(
            lambda *args: QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginUpdateDownloadURL)))

        # 将动作添加到关于菜单
        self.about_menu.addAction(self.plugin_home)
        self.about_menu.addAction(self.contact_feedback_action)
        self.about_menu.addAction(self.plugin_update_download_action)
        self.about_menu.addAction(self.help_document_action)


    def on_settings_presets_context_menu(self, pos: QtCore.QPoint):
        """
        在 settings_presets_menu 内部右键时触发
        pos 是菜单内部坐标
        """
        # 找到光标下对应的 QAction
        action = self.settings_presets_menu.actionAt(pos)
        if action is None:
            return

        # 你可以根据 action 区分不同的行为
        # 例如只对 modify_presets/delete_presets 弹菜单
        # if action == self.add_presets: …
        preset_name = action.text()

        # 添加预设
        self.add_presets    = QtWidgets.QAction('添加预设', self)
        self.add_presets.triggered.connect(lambda *args: self.add_settings_preset())

        # 修改预设
        self.modify_presets = QtWidgets.QAction('修改预设', self)
        self.modify_presets.triggered.connect(lambda *args: self.modify_settings_preset(preset_name))

        # 删除预设
        self.delete_presets = QtWidgets.QAction('删除预设', self)
        self.delete_presets.triggered.connect(lambda *args: self.delete_settings_preset(preset_name))

        # 打开预设文件夹
        self.open_presets_folder = QtWidgets.QAction('打开预设文件夹', self)
        self.open_presets_folder.triggered.connect(lambda *args: os.startfile(settings_presets_path))

        # 构造右键子菜单
        cmenu = QtWidgets.QMenu(self)
        # 举例：对任意项都提供“修改”和“删除”两项

        cmenu.addAction(self.add_presets)
        cmenu.addAction(self.modify_presets)
        cmenu.addAction(self.delete_presets)
        cmenu.addAction(self.open_presets_folder)
        # 在全局坐标下弹出
        cmenu.exec_( self.settings_presets_menu.mapToGlobal(pos) )

    # 加载预设文件
    def load_settings_preset(self, preset_file_name):
        # 构造预设文件所在的目录路径
        settings_presets_dir = settings_presets_path
        # 构造具体的预设文件路径
        preset_file_path = os.path.join(settings_presets_dir, preset_file_name +  ".json")

        # 如果预设文件不存在，直接返回
        if not os.path.isfile(preset_file_path):
            return

        # 构造当前配置文件的目标路径（将要替换的旧配置）
        old_target = os.path.join(settings_path, AMS_Config)
        ensure_directory(settings_path)
        # 如果旧配置文件存在，则先删除
        if os.path.exists(old_target):
            os.remove(old_target)

        # 复制预设文件到配置目录（settings_path），保留原文件名
        copied_path = shutil.copy2(preset_file_path, settings_path)

        # 将复制出来的文件重命名为 AMS_Config（正式配置文件名）
        old_path = copied_path  # 即 settings_path/preset_file_name
        new_path = old_target  # 即 settings_path/AMS_Config
        os.rename(old_path, new_path)

    # 添加预设文件
    def add_settings_preset(self,):
        """
        弹出对话框，输入新的预设名称，确认后复制当前配置到 settings_presets 目录，
        并在 settings_presets_menu 中添加对应 QAction。
        """
        # 1. 构造对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('添加预设')
        dialog.setModal(True)

        # 垂直布局：第一排输入框，第二排按钮
        layout = QtWidgets.QVBoxLayout(dialog)

        # 第一排：输入框
        line_edit = QtWidgets.QLineEdit(dialog)
        line_edit.setPlaceholderText('请输入预设名称')
        layout.addWidget(line_edit)

        # 第二排：确定、取消按钮
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton('确定', dialog)
        cancel_btn = QtWidgets.QPushButton('取消', dialog)
        btn_layout.addStretch(1)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # 连接按钮信号
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        # 2. 显示对话框并处理结果
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return  # 用户取消

        new_name = line_edit.text().strip()
        if not new_name:
            QtWidgets.QMessageBox.warning(self, '警告', '预设名称不能为空！')
            return

        # 3. 准备路径
        presets_dir = settings_presets_path
        ensure_directory(presets_dir)
        src = os.path.join(settings_path, AMS_Config)
        if not os.path.isfile(src):
            QtWidgets.QMessageBox.critical(self, '错误', '当前配置文件不存在，无法创建预设！')
            return

        dst = os.path.join(presets_dir, new_name + ".json")
        # 防止覆盖已有同名文件
        if os.path.exists(dst):
            reply = QtWidgets.QMessageBox.question(
                self, '覆盖确认',
                f'预设 "{new_name}" 已存在，是否覆盖？',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return

        # 4. 复制文件
        try:
            shutil.copy2(src, dst)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, '错误', f'复制失败：{e}')
            return

        # 5. 在菜单中添加新的 QAction
        action = QtWidgets.QAction(new_name, self)
        self.settings_presets_menu.addAction(action)
        action.triggered.connect(lambda *args, pf=new_name: self.load_settings_preset(pf))

    def modify_settings_preset(self, preset_file_name):
        """
        修改预设名称：弹出对话框输入新名称，重命名磁盘上的 JSON 文件，
        并更新菜单中对应 QAction 的文本和触发行为。
        """
        # 1. 找到对应的 QAction
        target_action = None
        for act in self.settings_presets_menu.actions():
            if act.text() == preset_file_name:
                target_action = act
                break
        if target_action is None:
            return  # 找不到就退出

        # 2. 弹出输入对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('修改预设名称')
        dialog.setModal(True)
        layout = QtWidgets.QVBoxLayout(dialog)

        line_edit = QtWidgets.QLineEdit(dialog)
        line_edit.setText(preset_file_name)
        layout.addWidget(line_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton('确定', dialog)
        cancel_btn = QtWidgets.QPushButton('取消', dialog)
        btn_layout.addStretch(1)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return

        new_name = line_edit.text().strip()
        if not new_name:
            QtWidgets.QMessageBox.warning(self, '警告', '预设名称不能为空！')
            return
        if new_name == preset_file_name:
            return  # 名称未改动

        # 3. 文件重命名
        presets_dir = settings_presets_path
        old_path = os.path.join(presets_dir, preset_file_name + ".json")
        new_path = os.path.join(presets_dir, new_name + ".json")
        if not os.path.isfile(old_path):
            QtWidgets.QMessageBox.critical(self, '错误', '原预设文件不存在！')
            return
        if os.path.exists(new_path):
            reply = QtWidgets.QMessageBox.question(
                self, '覆盖确认',
                f'已存在同名预设 "{new_name}"，是否覆盖？',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return
            os.remove(new_path)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, '错误', f'重命名失败：{e}')
            return

        # 4. 更新 QAction
        target_action.setText(new_name)
        try:
            target_action.triggered.disconnect()
        except TypeError:
            # 如果之前没有连接或无法断开，则忽略
            pass
        target_action.triggered.connect(lambda *args, pf=new_name: self.load_settings_preset(pf))

    def delete_settings_preset(self, preset_file_name):
        """
        删除预设：从磁盘删除 JSON 文件，并从菜单中移除对应 QAction。
        """
        # 1. 用户确认
        reply = QtWidgets.QMessageBox.question(
            self, '删除预设',
            f'确认要删除预设 "{preset_file_name}" 吗？此操作不可恢复。',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        # 2. 删除文件
        presets_dir = settings_presets_path
        file_path = os.path.join(presets_dir, preset_file_name + ".json")
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, '错误', f'删除文件失败：{e}')
                return
        else:
            QtWidgets.QMessageBox.warning(self, '警告', '预设文件不存在，可能已被删除。')

        # 3. 移除菜单项
        for act in self.settings_presets_menu.actions():
            if act.text() == preset_file_name:
                self.settings_presets_menu.removeAction(act)
                break

    def create_widgets(self):
        # 创建选项卡部件
        self.tab_widget = QtWidgets.QTabWidget()

        # 创建各个选项卡页面
        self.create_magic_connection_tab()
        self.create_color_space_tab()
        self.create_node_connection_tab()
        self.create_path_matching_tab()
        self.node_connection_mixer_tab()
        self.create_optimized_scene_node_name_tab()
        self.create_configure_ui_layout_tab()

    def create_layouts(self):
        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setMenuBar(self.main_menu_bar)
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    # 初始化控件的设置，例如设置默认值，连接信号和槽等
    def initial_widgets_settings(self):
        pass

    # 魔法连接的标签页面
    def create_magic_connection_tab(self):
        # _______________________________________________________________>>> 字体设置
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        # _______________________________________________________________>>> 创建内容区域
        # 创建一个用于存放内容的 QWidget
        content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content_widget)

        # _______________________________________________________________>>> [1] 连接设置
        self.add_line_with_text(layout, self.language['create_magic_connection_tab']['mfljsz_label'])  # "魔法连接设置"

        # 智能修改色彩空间选项
        self.auto_color_space_connection = QtWidgets.QCheckBox(
            self.language['create_magic_connection_tab']['auto_color_space_connection'])  # 连接时智能修改色彩空间

        # auto_color_space_connection 连接修改配置函数
        self.auto_color_space_connection.stateChanged.connect(lambda *args: self.modify_nested_config(
            key_path=['magic_conn_config', 'set_color_space'],
            cont=self.auto_color_space_connection.isChecked()))

        # 初始化连接时智能修改色彩空间控件值
        self.auto_color_space_connection.setChecked(
            self.config['magic_conn_config']['set_color_space'])

        layout.addWidget(self.auto_color_space_connection)

        # 智能 UDIM 选项
        self.magic_change_udim_options = QtWidgets.QCheckBox(
            self.language['create_magic_connection_tab']['magic_change_udim_options'])  # '连接时智能UDIM'

        # magic_change_udim_options 连接修改配置函数
        self.magic_change_udim_options.stateChanged.connect(lambda *args: self.modify_nested_config(
            key_path=['magic_conn_config', 'set_udim'],
            cont=self.magic_change_udim_options.isChecked()))

        # 初始化连接时智能UDIM控件值
        self.magic_change_udim_options.setChecked(
            self.config['magic_conn_config']['set_udim'])

        layout.addWidget(self.magic_change_udim_options)

        # 修改材质名称选项
        self.magic_change_material_name_options = QtWidgets.QCheckBox(
            self.language['create_magic_connection_tab']['magic_change_material_name_options'])  # '连接时修改材质名称'

        # magic_change_material_name_options 连接修改配置函数
        self.magic_change_material_name_options.stateChanged.connect(lambda *args: self.modify_nested_config(
            key_path=['magic_conn_config', 'set_material_name'],
            cont=self.magic_change_material_name_options.isChecked()))

        # 初始化连接时修改材质名称控件值
        self.magic_change_material_name_options.setChecked(
            self.config['magic_conn_config']['set_material_name'])

        layout.addWidget(self.magic_change_material_name_options)

        # _______________________________________________________________>>> [2] 自定义连接的贴图
        self.add_line_with_text(layout, self.language['create_magic_connection_tab']['zdyljdtt_label'])  # 自定义连接的贴图

        # 创建列表控件
        self.tex_first_filter_options_list = QtWidgets.QListWidget()

        # 设置tex_first_filter_options_list参数
        self.tex_first_filter_options_list.setFixedHeight(530)  # 设置大小
        self.tex_first_filter_options_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)  # 设置选择模式

        # 循环创建每一个选项
        for name, value in self.config['magic_conn_config']['conn_params'].items():
            item = QtWidgets.QListWidgetItem(name.capitalize())  # 让名称的第一个字母大写
            item.setFont(font)
            self.tex_first_filter_options_list.addItem(item)
            item.setSelected(value)  # 设置默认值

        # 绑定选择变更触发函数
        self.tex_first_filter_options_list.selectionModel().selectionChanged.connect(
            lambda *args: self.modify_tex_first_filter_options_list_config())

        layout.addWidget(self.tex_first_filter_options_list)

        # _______________________________________________________________>>> [3] 自定义过滤名字
        self.add_line_with_text(layout, self.language['create_magic_connection_tab']['zdyglmz_label'])  # 自定义过滤名字

        self.texture_filter_fields = {}

        # 循环创建每个通道的过滤输入框
        for channel, filters in self.config['texture_filter_params'].items():
            # 创建标题并设置样式
            channel_label = QtWidgets.QLabel(f"{channel.capitalize()} :")
            channel_label.setStyleSheet("font-weight: bold;")  # 加粗字体
            layout.addWidget(channel_label)

            # 创建输入框并设置初始文本
            self.texture_filter_fields[channel] = QtWidgets.QLineEdit(", ".join(filters))
            self.texture_filter_fields[channel].setText(
                str(filters).replace('[', '').replace(']', '').replace("'", "").replace(",", " , "))

            # 绑定文本修改触发函数
            self.texture_filter_fields[channel].textChanged.connect(
                lambda text, ch=channel: self.modify_texture_filter_fields_config(ch, text))

            layout.addWidget(self.texture_filter_fields[channel])

        # _______________________________________________________________>>> 滚动区域和选项卡
        # 创建 QScrollArea 并设置内容
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)  # 使滚动区域自适应内容大小
        scroll_area.setWidget(content_widget)  # 将内容部件设置为滚动区域的部件

        # 创建用于选项卡的 QWidget 并设置布局
        magic_connection_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(magic_connection_tab)
        tab_layout.addWidget(scroll_area)  # 将滚动区域添加到选项卡布局中

        # 将选项卡添加到 tab_widget
        self.tab_widget.addTab(magic_connection_tab, self.language['create_magic_connection_tab']['mflj_tab'])  # 魔法连接

    # 颜色空间的标签页面
    def create_color_space_tab(self):
        # _______________________________________________________________>>> 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        # _______________________________________________________________>>> 初始化变量
        config = self.config['color_space_params'] # 初始化颜色空间的函数

        # _______________________________________________________________>>> 创建用于存放内容的 QWidget
        content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content_widget)

        # [1] 自定义色彩空间
        self.add_line_with_text(layout, self.language['create_color_space_tab']['zdysckj_label'])  # 自定义色彩空间标签

        self.color_space_text = QtWidgets.QPlainTextEdit()

        # 设置 color_space_text 的内容
        self.color_space_text.setPlainText(
            str(config['config'])
            .replace('[', '')
            .replace(']', '')
            .replace("'", "")
            .replace(",", " , ")
        )

        # 设置窗口高度为 350
        self.color_space_text.setFixedHeight(350)

        # 设置字体
        self.color_space_text.setFont(font)

        # 连接函数槽，处理文本变更
        self.color_space_text.textChanged.connect(self.modify_color_space_text_config)

        layout.addWidget(self.color_space_text)

        # [2] 自动设置色彩空间
        self.add_line_with_text(layout, self.language['create_color_space_tab']['zdszsckj_label'])  # 自动设置色彩空间标签

        self.auto_color_space_options = {}

        # 用来存储图标变量
        AutoSetColorSpaceMenuName = {}

        channels = config['params']  # 示例通道列表

        for channel in channels:
            h_layout = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(f"{channel.capitalize()}:")
            label.setStyleSheet("font-weight: bold;")  # 设置标签字体加粗

            # 创建并设置下拉框
            AutoSetColorSpaceMenuName[channel] = QtWidgets.QComboBox()
            AutoSetColorSpaceMenuName[channel].addItems(config['config'])

            # 设置默认值
            AutoSetColorSpaceMenuName[channel].setCurrentText(config['params'][channel])

            # 设置激活函数，连接信号槽
            AutoSetColorSpaceMenuName[channel].currentIndexChanged.connect(
                lambda _, ch=channel: self.modify_nested_config(
                    key_path=['color_space_params', 'params', ch],
                    cont=AutoSetColorSpaceMenuName[ch].currentText()
                )
            )

            h_layout.addWidget(label)
            h_layout.addWidget(AutoSetColorSpaceMenuName[channel])
            layout.addLayout(h_layout)

        # 创建一个 QScrollArea，并将内容部件添加进去
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # 创建用于选项卡的 QWidget，并设置布局
        color_space_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(color_space_tab)
        tab_layout.addWidget(scroll_area)

        # 将选项卡添加到 tab_widget
        self.tab_widget.addTab(color_space_tab, self.language['create_color_space_tab']['sckj_label'])  # 颜色空间选项卡

    # 节点连接的标签页面
    def create_node_connection_tab(self):
        #_______________________________________________________________>>> 创建配置变量
        config = self.config['proc_node_config']

        #_______________________________________________________________>>> 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        #_______________________________________________________________>>> 节点连接选项卡
        node_connection_widget = QtWidgets.QWidget()
        node_connection_layout = QtWidgets.QVBoxLayout(node_connection_widget)

        # 使用 QScrollArea 实现滚动
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(scroll_content_widget)

        # [1] 自定义连接的节点
        self.add_line_with_text(layout, self.language['create_node_connection_tab']['zdljcljdsz_label'])  # 自动连接处理节点设置标签

        self.auto_node_connection_list = QtWidgets.QListWidget()
        self.auto_node_connection_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        # 添加节点列表项
        for channel, value in config['conn_params'].items():
            item = QtWidgets.QListWidgetItem(channel.capitalize())  # 名称首字母大写
            item.setSelected(True)
            item.setFont(font)
            self.auto_node_connection_list.addItem(item)
            item.setSelected(value)

        # 设置自动连接列表大小
        self.auto_node_connection_list.setFixedHeight(530)

        # 绑定修改配置函数
        self.auto_node_connection_list.selectionModel().selectionChanged.connect(
            lambda *args: self.modify_auto_node_connection_config()
        )

        layout.addWidget(self.auto_node_connection_list)

        # [2] 处理节点设置
        self.add_line_with_text(layout, self.language['create_node_connection_tab']['cljdsz_list'])  # 处理节点设置标签

        input_port_combo = {}
        output_port_combo = {}
        self.node_list_edit = {}

        # 动态创建节点连接设置
        for channel, data in config['params'].items():
            layout.addWidget(self.create_section_label(channel.capitalize() + ':'))  # 添加通道标题

            # 创建一个横向布局
            h_layout = QtWidgets.QHBoxLayout()

            # 创建输入端口多选框
            input_port_combo[channel] = QtWidgets.QComboBox()
            input_port_combo[channel].addItems(config['first_node_input'])  # 添加示例输入端口
            input_port_combo[channel].setCurrentText(config['params'][channel]['InputPort'])
            input_port_combo[channel].setFixedWidth(130)
            input_port_combo[channel].currentIndexChanged.connect(
                lambda _, ch=channel: self.modify_nested_config(
                    key_path=['proc_node_config', 'params', ch, 'InputPort'],
                    cont=input_port_combo[ch].currentText()
                )
            )

            # 创建节点输入列表编辑框
            self.node_list_edit[channel] = QtWidgets.QLineEdit()
            self.node_list_edit[channel].setText(
                str(config['params'][channel]['NodeList'])
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , ")
            )
            self.node_list_edit[channel].textChanged.connect(
                lambda text, ch=channel: self.modify_pro_node_list_config(ch, text)
            )

            # 创建输出端口多选框
            output_port_combo[channel] = QtWidgets.QComboBox()
            output_port_combo[channel].addItems(config['last_node_output'])  # 添加示例输出端口
            output_port_combo[channel].setCurrentText(config['params'][channel]['OutputPort'])
            output_port_combo[channel].setFixedWidth(130)
            output_port_combo[channel].currentIndexChanged.connect(
                lambda _, ch=channel: self.modify_nested_config(
                    key_path=['proc_node_config', 'params', ch, 'OutputPort'],
                    cont=output_port_combo[ch].currentText()
                )
            )

            # 创建添加节点按钮
            add_node_button = QtWidgets.QPushButton("<")
            add_node_button.setFixedWidth(30)
            add_node_button.setFixedHeight(28)
            add_node_button.clicked.connect(lambda *_, ch=channel: self.add_pro_node_to_list(ch))

            # 将组件添加到横向布局中
            h_layout.addWidget(input_port_combo[channel])
            h_layout.addWidget(self.node_list_edit[channel])
            h_layout.addWidget(output_port_combo[channel])
            h_layout.addWidget(add_node_button)

            layout.addLayout(h_layout)

        # 将内容添加到滚动区域
        scroll_area.setWidget(scroll_content_widget)
        node_connection_layout.addWidget(scroll_area)

        # 添加到选项卡
        self.tab_widget.addTab(node_connection_widget, self.language['create_node_connection_tab']['jdlj_tab'])  # 添加节点连接选项卡

    # 节点路径匹配页面
    def create_path_matching_tab(self):
        #_______________________________________________________________>>> 创建配置变量
        config = self.config['path_detection_params']

        #_______________________________________________________________>>> 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        #_______________________________________________________________>>> 加载路径检测配置
        path_detection_config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config)))['path_detection_params']

        # 创建节点路径匹配选项卡
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        path_matching_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(path_matching_widget)

        # [0] 连接时相关设置
        self.add_line_with_text(layout, self.language['create_path_matching_tab']['ljsxgsz_label'])  # 连接时相关设置标签

        # 创建复选框并绑定配置修改函数
        self.path_matching_checkbox = QtWidgets.QCheckBox(self.language['create_path_matching_tab']['path_matching_checkbox'])
        self.path_matching_checkbox.setChecked(config['set_color_space'])
        self.path_matching_checkbox.stateChanged.connect(lambda *args: self.modify_nested_config(key_path =['path_detection_params', 'set_color_space'],
                                                                                                 cont =  self.path_matching_checkbox.isChecked()))
        layout.addWidget(self.path_matching_checkbox)

        self.path_matching_change_udim_checkbox = QtWidgets.QCheckBox(self.language['create_path_matching_tab']['path_matching_change_udim_checkbox'])
        self.path_matching_change_udim_checkbox.setChecked(config['set_udim'])
        self.path_matching_change_udim_checkbox.stateChanged.connect(lambda *args: self.modify_nested_config(key_path =['path_detection_params', 'set_udim'],
                                                                                                             cont = self.path_matching_change_udim_checkbox.isChecked()))
        layout.addWidget(self.path_matching_change_udim_checkbox)

        self.path_matching_change_material_name_options = QtWidgets.QCheckBox(self.language['create_path_matching_tab']['path_matching_change_material_name_options'])
        self.path_matching_change_material_name_options.setChecked(config['set_material_name'])
        self.path_matching_change_material_name_options.stateChanged.connect(lambda *args: self.modify_nested_config(key_path=['path_detection_params', 'set_material_name'],
                                                                                                                     cont = self.path_matching_change_material_name_options.isChecked()))
        layout.addWidget(self.path_matching_change_material_name_options)

        self.path_disable_feedback_options = QtWidgets.QCheckBox(self.language['create_path_matching_tab']['path_disable_feedback_options'])
        self.path_disable_feedback_options.setChecked(config['disable_feedback'])
        self.path_disable_feedback_options.stateChanged.connect(lambda *args: self.modify_nested_config(key_path= ['path_detection_params', 'disable_feedback'],
                                                                                                        cont = self.path_disable_feedback_options.isChecked()))
        layout.addWidget(self.path_disable_feedback_options)

        # [1] 排除格式
        self.add_line_with_text(layout, "前期格式筛选")



        self.exclude_formats_list_text = QtWidgets.QPlainTextEdit()

        self.exclude_formats_list_text.setPlainText(str(config['exclude_formats']).
                                            replace('[', '').
                                            replace(']', '').
                                            replace("'", "").
                                            replace(",", " , "))
        self.exclude_formats_list_text.setFont(font)
        self.exclude_formats_list_text.textChanged.connect(lambda *args: self.modify_nested_config(key_path= ['path_detection_params', 'exclude_formats'],
                                                                                           cont= [item.replace(' ', '') for item in self.exclude_formats_list_text.toPlainText().split(",")], ))



        layout.addWidget(self.exclude_formats_list_text)





        # [2] 排除名称
        self.add_line_with_text(layout, self.language['create_path_matching_tab']['sxgczpchywzdwj_label'])  # 排除含有文字的文件标签

        self.exclude_list_text = QtWidgets.QPlainTextEdit()
        self.exclude_list_text.setPlainText(str(config['exclude']).
                                            replace('[', '').
                                            replace(']', '').
                                            replace("'", "").
                                            replace(",", " , "))
        self.exclude_list_text.setFont(font)
        self.exclude_list_text.textChanged.connect(lambda *args: self.modify_nested_config(key_path= ['path_detection_params', 'exclude'],
                                                                                           cont= [item.replace(' ', '') for item in self.exclude_list_text.toPlainText().split(",")], ))
        layout.addWidget(self.exclude_list_text)

        # [3] 格式名称
        self.add_line_with_text(layout, self.language['create_path_matching_tab']['zjxxsdjcsyczfczdtdnc_label'])  # 移除字符串中特定内容标签

        self.detection_excluded_list = QtWidgets.QPlainTextEdit()
        self.detection_excluded_list.setPlainText(str(config['detection_excluded']).
                                                  replace('[', '').
                                                  replace(']', '').
                                                  replace("'", "").
                                                  replace(",", " , "))
        self.detection_excluded_list.setFont(font)
        self.detection_excluded_list.textChanged.connect(lambda *args: self.modify_nested_config(key_path= ['path_detection_params','detection_excluded'],
                                                                                                 cont= [item.replace(' ', '') for item in self.detection_excluded_list.toPlainText().split(",")], ))
        layout.addWidget(self.detection_excluded_list)

        # [4] 匹配时相关设置
        self.add_line_with_text(layout, self.language['create_path_matching_tab']['ppsxgsz_label'])  # 匹配时相关设置标签

        self.auto_max_val_checkbox = QtWidgets.QCheckBox(self.language['create_path_matching_tab']['auto_max_val_checkbox'])
        self.auto_max_val_checkbox.setChecked(config['auto_max_val'])
        self.auto_max_val_checkbox.stateChanged.connect(lambda *args: (self.modify_nested_config(key_path = ['path_detection_params','auto_max_val'],
                                                                                                 cont = self.auto_max_val_checkbox.isChecked()),
                                                                       self.update_similarity_max_slider_ui()))
        layout.addWidget(self.auto_max_val_checkbox)
        self.auto_max_val_checkbox.setToolTip(self.language['create_path_matching_tab']['auto_max_val_checkbox_tip'])

        self.add_line_with_text(layout, self.language['create_path_matching_tab']['ppysqz_label'])  # 匹配元素权重标签

        # 初始化滑杆的权重值
        slider_values = {
            'name_weight': config['name_weight'],
            'resolution_weight': config['resolution_weight'],
            'format_weight': config['format_weight'],
            'creation_time_weight': config['creation_time_weight'],
        }

        # 定义更新权重的函数
        def update_weight(slider_name, value):
            current_value = value / 1000.0
            slider_values[slider_name] = current_value
            remaining = 1.0 - current_value
            other_sliders = {k: v for k, v in slider_values.items() if k != slider_name}
            total_other_values = sum(other_sliders.values())
            if total_other_values == 0:
                for key in other_sliders:
                    slider_values[key] = remaining / len(other_sliders)
            else:
                for key in other_sliders:
                    proportion = other_sliders[key] / total_other_values
                    slider_values[key] = remaining * proportion
            update_ui_and_config()

        # 定义更新UI和配置文件的函数
        def update_ui_and_config():
            self.name_weight_slider.blockSignals(True)
            self.resolution_weight_slider.blockSignals(True)
            self.format_weight_slider.blockSignals(True)
            self.creation_time_weight_slider.blockSignals(True)
            self.name_weight_slider.setValue(int(slider_values['name_weight'] * 1000))
            self.name_weight_label.setText("{:.3f}".format(slider_values['name_weight']))
            self.resolution_weight_slider.setValue(int(slider_values['resolution_weight'] * 1000))
            self.resolution_weight_label.setText("{:.3f}".format(slider_values['resolution_weight']))
            self.format_weight_slider.setValue(int(slider_values['format_weight'] * 1000))
            self.format_weight_label.setText("{:.3f}".format(slider_values['format_weight']))
            self.creation_time_weight_slider.setValue(int(slider_values['creation_time_weight'] * 1000))
            self.creation_time_weight_label.setText("{:.3f}".format(slider_values['creation_time_weight']))
            self.name_weight_slider.blockSignals(False)
            self.resolution_weight_slider.blockSignals(False)
            self.format_weight_slider.blockSignals(False)
            self.creation_time_weight_slider.blockSignals(False)
            self.modify_nested_config(key_path= ['path_detection_params','name_weight'], cont = slider_values['name_weight'], )
            self.modify_nested_config(key_path= ['path_detection_params','resolution_weight'], cont =slider_values['resolution_weight'], )
            self.modify_nested_config(key_path= ['path_detection_params','format_weight'], cont =slider_values['format_weight'], )
            self.modify_nested_config(key_path= ['path_detection_params','creation_time_weight'], cont =slider_values['creation_time_weight'], )

        # 创建权重滑杆和标签
        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['mzqz_label']))  # 名字权重标签
        name_weight_layout = QtWidgets.QHBoxLayout()
        self.name_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.name_weight_slider.setMinimum(0)
        self.name_weight_slider.setMaximum(1000)
        self.name_weight_slider.setValue(int(slider_values['name_weight'] * 1000))
        name_weight_layout.addWidget(self.name_weight_slider)
        self.name_weight_label = QtWidgets.QLabel("{:.3f}".format(slider_values['name_weight']))
        name_weight_layout.addWidget(self.name_weight_label)
        layout.addLayout(name_weight_layout)
        self.name_weight_slider.valueChanged.connect(lambda value: update_weight('name_weight', value))

        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['fblqz_label']))  # 分辨率权重标签
        resolution_weight_layout = QtWidgets.QHBoxLayout()
        self.resolution_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.resolution_weight_slider.setMinimum(0)
        self.resolution_weight_slider.setMaximum(1000)
        self.resolution_weight_slider.setValue(int(slider_values['resolution_weight'] * 1000))
        resolution_weight_layout.addWidget(self.resolution_weight_slider)
        self.resolution_weight_label = QtWidgets.QLabel("{:.3f}".format(slider_values['resolution_weight']))
        resolution_weight_layout.addWidget(self.resolution_weight_label)
        layout.addLayout(resolution_weight_layout)
        self.resolution_weight_slider.valueChanged.connect(lambda value: update_weight('resolution_weight', value))

        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['gsqz_label']))  # 格式权重标签
        format_weight_layout = QtWidgets.QHBoxLayout()
        self.format_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.format_weight_slider.setMinimum(0)
        self.format_weight_slider.setMaximum(1000)
        self.format_weight_slider.setValue(int(slider_values['format_weight'] * 1000))
        format_weight_layout.addWidget(self.format_weight_slider)
        self.format_weight_label = QtWidgets.QLabel("{:.3f}".format(slider_values['format_weight']))
        format_weight_layout.addWidget(self.format_weight_label)
        layout.addLayout(format_weight_layout)
        self.format_weight_slider.valueChanged.connect(lambda value: update_weight('format_weight', value))

        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['cjsjqz_label']))  # 创建时间权重标签
        creation_time_weight_layout = QtWidgets.QHBoxLayout()
        self.creation_time_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.creation_time_weight_slider.setMinimum(0)
        self.creation_time_weight_slider.setMaximum(1000)
        self.creation_time_weight_slider.setValue(int(slider_values['creation_time_weight'] * 1000))
        creation_time_weight_layout.addWidget(self.creation_time_weight_slider)
        self.creation_time_weight_label = QtWidgets.QLabel("{:.3f}".format(slider_values['creation_time_weight']))
        creation_time_weight_layout.addWidget(self.creation_time_weight_label)
        layout.addLayout(creation_time_weight_layout)
        self.creation_time_weight_slider.valueChanged.connect(lambda value: update_weight('creation_time_weight', value))

        self.add_line_with_text(layout, self.language['create_path_matching_tab']['xsdjs_label'])  # 相似度的计算标签

        # 创建相似度最大值滑杆和标签
        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['similarity_max_slider_label']))  # 相似度阈值标签
        similarity_max_layout = QtWidgets.QHBoxLayout()
        self.similarity_max_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.similarity_max_slider.setMinimum(0)
        self.similarity_max_slider.setMaximum(1000)
        self.similarity_max_slider.setValue(int(config['similarity_max'] * 1000))
        similarity_max_layout.addWidget(self.similarity_max_slider)
        self.similarity_max_label = QtWidgets.QLabel("{:.3f}".format(config['similarity_max']))
        similarity_max_layout.addWidget(self.similarity_max_label)
        layout.addLayout(similarity_max_layout)
        self.similarity_max_slider.setToolTip(self.language['create_path_matching_tab']['similarity_max_slider_tip'])

        # 1，更新显示文本数值
        # 2，更新配置的里的数据
        self.similarity_max_slider.valueChanged.connect(lambda value: (self.similarity_max_label.setText(str("{:.3f}".format(value* 0.001))),
                                                                  self.modify_nested_config(key_path= ['path_detection_params','similarity_max'],
                                                                                            cont = value* 0.001)))
        # 去初始化禁用相似度阈值
        self.update_similarity_max_slider_ui()

        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['similarity_range_slider_label']))  # 相似度容差范围标签
        similarity_range_layout = QtWidgets.QHBoxLayout()
        self.similarity_range_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.similarity_range_slider.setMinimum(0)
        self.similarity_range_slider.setMaximum(1000)
        self.similarity_range_slider.setValue(int(config['similarity_range'] * 1000))
        similarity_range_layout.addWidget(self.similarity_range_slider)
        self.similarity_range_label = QtWidgets.QLabel("{:.3f}".format(config['similarity_range']))
        similarity_range_layout.addWidget(self.similarity_range_label)
        layout.addLayout(similarity_range_layout)
        self.similarity_range_slider.setToolTip(self.language['create_path_matching_tab']['similarity_range_slider_tip'])


        # 1，更新显示文本数值
        # 2，更新配置的里的数据
        self.similarity_range_slider.valueChanged.connect(lambda value: (self.similarity_range_label.setText(str("{:.3f}".format(value* 0.001))),
                                                                  self.modify_nested_config(key_path= ['path_detection_params','similarity_range'],
                                                                                            cont = value* 0.001)))
        # 创建天数范围容差滑杆和标签
        layout.addWidget(QtWidgets.QLabel(self.language['create_path_matching_tab']['day_range_slider_label']))  # 天数范围容差值标签
        day_range_layout = QtWidgets.QHBoxLayout()
        self.day_range_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.day_range_slider.setMinimum(1)
        self.day_range_slider.setMaximum(1000)
        self.day_range_slider.setValue(int(config['creation_day_range_tolerance']))
        day_range_layout.addWidget(self.day_range_slider)
        self.day_range_label = QtWidgets.QLabel(str(config['creation_day_range_tolerance']))
        day_range_layout.addWidget(self.day_range_label)
        layout.addLayout(day_range_layout)
        self.day_range_slider.setToolTip('test')

        # 1，更新显示文本数值
        # 2，更新配置的里的数据
        self.day_range_slider.valueChanged.connect(lambda value: (self.day_range_label.setText(str(value)),
                                                                  self.modify_nested_config(key_path= ['path_detection_params','creation_day_range_tolerance'],
                                                                                            cont = value)))

        # 将 path_matching_widget 设置为 scroll_area 的子组件
        scroll_area.setWidget(path_matching_widget)

        # 添加到选项卡
        self.tab_widget.addTab(scroll_area, self.language['create_path_matching_tab']['jdljpp_tab'])  # 节点路径匹配选项卡

    # 节点连接混合器页面
    def node_connection_mixer_tab(self):
        # _______________________________________________________________>>> 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)
        font.setBold(True)

        # _______________________________________________________________>>> 加载路径检测配置
        config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )['node_connection_mixer_config']

        # 外层容器
        content_widget = QtWidgets.QWidget()
        content_lay = QtWidgets.QVBoxLayout(content_widget)
        content_lay.setAlignment(QtCore.Qt.AlignTop)

        # 计算最大行高，用于限制 QTextEdit 的高度
        metrics = QtGui.QFontMetrics(font)
        line_h = metrics.lineSpacing()
        max_lines = 5
        max_height = line_h * max_lines + 12  # 12px 额外padding

        # [1] 快速连接 输入端口
        self.add_line_with_text(content_lay, '快速连接 输入端口')
        self.input_port_line = QtWidgets.QPlainTextEdit()
        self.input_port_line.setPlainText(
            str(config['quick_connect_node_parms']['input_port'])
            .replace('[', '')
            .replace(']', '')
            .replace("'", "")
            .replace(",", " , ")
        )
        self.input_port_line.textChanged.connect(lambda *args: self.modify_nested_config(key_path= ['node_connection_mixer_config', 'quick_connect_node_parms', 'input_port'],
                                                                                           cont= [item.replace(' ', '') for item in self.input_port_line.toPlainText().split(",")]))

        self.input_port_line.setFont(font)
        # 限制最大高度 & 垂直固定
        self.input_port_line.setMaximumHeight(max_height)
        sp1 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Fixed
        )
        self.input_port_line.setSizePolicy(sp1)
        content_lay.addWidget(self.input_port_line)

        # [2] 快速连接 输出端口
        self.add_line_with_text(content_lay, '快速连接 输出端口')
        self.output_prot_line = QtWidgets.QPlainTextEdit()
        self.output_prot_line.setPlainText(
            str(config['quick_connect_node_parms']['out_port'])
            .replace('[', '')
            .replace(']', '')
            .replace("'", "")
            .replace(",", " , ")
        )
        self.output_prot_line.textChanged.connect(lambda *args: self.modify_nested_config(key_path= ['node_connection_mixer_config', 'quick_connect_node_parms', 'out_port'],
                                                                                           cont= [item.replace(' ', '') for item in self.output_prot_line.toPlainText().split(",")]))
        self.output_prot_line.setFont(font)
        # 限制最大高度 & 垂直固定
        self.output_prot_line.setMaximumHeight(max_height)
        sp2 = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Fixed
        )
        self.output_prot_line.setSizePolicy(sp2)
        content_lay.addWidget(self.output_prot_line)

        # # [3] 快速连接 优先组合
        # self.add_line_with_text(content_lay, '快速连接 优先组合')



        # 把 content_widget 放进滚动区域
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        # 显式设置滚动条策略
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setWidget(content_widget)

        # 整个 tab
        tab = QtWidgets.QWidget()
        tab_lay = QtWidgets.QVBoxLayout(tab)
        tab_lay.addWidget(scroll)

        self.tab_widget.addTab(tab, '节点连接混合器')






    # 优化场景节点名称页面

    def create_optimized_scene_node_name_tab(self):

        # __________________________________________________________________________>>> 创建配置变量
        config = self.config['optimized_scene_node_name']

        # __________________________________________________________________________>>> 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置字体加粗

        # __________________________________________________________________________>>> 创建用于存放内容的 QWidget
        content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content_widget)
        layout.setAlignment(QtCore.Qt.AlignTop)  # 设置布局对齐方式为靠上

        # 定义添加配置的函数
        def add_config():
            # 向配置文件中添加一个新的替换参数
            self.config['optimized_scene_node_name']['replace_param'].append(
                {
                    'target_cont': '',  # 替换目标内容
                    'replace_cont': '',  # 替换后内容
                    'case_sensitive': False,  # 是否大小写敏感
                    "switch_checkbox": True  # 是否启用
                }
            )
            # 更新配置文件
            self.modify_nested_config(
                key_path=['optimized_scene_node_name', 'replace_param'],
                cont=self.config['optimized_scene_node_name']['replace_param']
            )

        # __________________________________________________________________________>>> 创建 '添加' 按钮
        add_button = QtWidgets.QPushButton('添加')
        add_button.clicked.connect(lambda *args: add_config())
        layout.addWidget(add_button)

        # __________________________________________________________________________>>> 创建用于存放套件的容器
        suites_container = QtWidgets.QWidget()
        suites_layout = QtWidgets.QVBoxLayout(suites_container)
        suites_layout.setAlignment(QtCore.Qt.AlignTop)  # 将布局对齐方式设置为靠上
        layout.addWidget(suites_container)

        # 用于存储所有套件的列表
        self.suites = []

        # __________________________________________________________________________>>> 定义更新索引号的函数
        def update_indices():
            for index, suite in enumerate(self.suites, start=1):
                suite['index_label'].setText(str(index))  # 更新每个套件的索引标签

        # __________________________________________________________________________>>> 定义添加套件的函数
        def add_suite(switch=True, case_sensitive=False, target_cont="", replace_cont=""):
            # 创建一个套件的 QWidget
            suite_widget = QtWidgets.QWidget()
            suite_layout = QtWidgets.QHBoxLayout(suite_widget)
            suite_layout.setContentsMargins(5, 5, 5, 5)
            suite_layout.setSpacing(10)

            # 设置套件样式
            suite_widget.setStyleSheet('''
                QWidget {
                    background-color: rgb(60, 60, 60);
                    border: 1px solid rgb(86, 86, 86);
                    border-width: 2px;
                    border-radius: 8px;
                    padding: 8px;
                }
                QLabel {
                    color: white;
                }
            ''')

            # 创建套件的组件
            index_label = QtWidgets.QLabel()  # 显示索引号
            index_label.setFixedWidth(30)

            switch_checkbox = QtWidgets.QCheckBox('E')  # 启用开关
            switch_checkbox.setChecked(switch)

            # 连接信号到槽函数
            switch_checkbox.stateChanged.connect(lambda *args:self.modify_nested_config(
                                                             key_path = ['optimized_scene_node_name',
                                                                         'replace_param',
                                                                         self.suites.index(suite_info),
                                                                         'switch_checkbox'],
                                                             cont = (switch_checkbox.isChecked())))



            case_insensitive_checkbox = QtWidgets.QCheckBox('R')  # 大小写敏感选项
            case_insensitive_checkbox.setChecked(case_sensitive)
            # 连接信号到槽函数
            case_insensitive_checkbox.stateChanged.connect(lambda *args:self.modify_nested_config(
                                                             key_path = ['optimized_scene_node_name',
                                                                         'replace_param',
                                                                         self.suites.index(suite_info),
                                                                         'case_sensitive'],
                                                             cont = (case_insensitive_checkbox.isChecked())))

            replacement_target_input = QtWidgets.QLineEdit()  # 替换目标输入框
            replacement_target_input.setPlaceholderText('替换目标')
            replacement_target_input.setText(target_cont)
            replacement_target_input.textChanged.connect(lambda *args:self.modify_nested_config(
                                                             key_path = ['optimized_scene_node_name',
                                                                         'replace_param',
                                                                         self.suites.index(suite_info),
                                                                         'target_cont'],
                                                             cont = (str(replacement_target_input.text()))))
            arrow_label = QtWidgets.QLabel('→')  # 箭头符号

            replacement_content_input = QtWidgets.QLineEdit()  # 替换内容输入框
            replacement_content_input.setPlaceholderText('替换内容')
            replacement_content_input.setText(replace_cont)
            replacement_content_input.textChanged.connect(lambda *args:self.modify_nested_config(
                                                             key_path = ['optimized_scene_node_name',
                                                                         'replace_param',
                                                                         self.suites.index(suite_info),
                                                                         'replace_cont'],
                                                             cont = (str(replacement_content_input.text()))))
            delete_button = QtWidgets.QPushButton('删除')  # 删除按钮

            # 将组件添加到布局
            suite_layout.addWidget(index_label)
            suite_layout.addWidget(switch_checkbox)
            suite_layout.addWidget(case_insensitive_checkbox)
            suite_layout.addWidget(replacement_target_input)
            suite_layout.addWidget(arrow_label)
            suite_layout.addWidget(replacement_content_input)
            suite_layout.addWidget(delete_button)

            # 将套件添加到容器布局
            suites_layout.addWidget(suite_widget)

            # 存储套件信息
            suite_info = {
                'widget': suite_widget,
                'index_label': index_label,
                'switch_checkbox': switch_checkbox,
                'case_insensitive_checkbox': case_insensitive_checkbox,
                'replacement_target_input': replacement_target_input,
                'replacement_content_input': replacement_content_input,
                'delete_button': delete_button
            }

            self.suites.append(suite_info)

            # 定义删除套件的函数
            def delete_suite():
                # 获取被删除套件的索引和信息
                suite_index = self.suites.index(suite_info)
                target_content = suite_info['replacement_target_input'].text()
                replace_content = suite_info['replacement_content_input'].text()
                case_sensitive = suite_info['case_insensitive_checkbox'].isChecked()

                # 从配置文件中删除对应的数据
                self.config['optimized_scene_node_name']['replace_param'].pop(suite_index)

                self.modify_nested_config(
                    key_path=['optimized_scene_node_name', 'replace_param'],
                    cont=self.config['optimized_scene_node_name']['replace_param']
                )

                # 从布局中移除套件，并释放资源
                suites_layout.removeWidget(suite_widget)
                suite_widget.deleteLater()

                # 从套件列表中移除，并更新索引
                self.suites.remove(suite_info)
                update_indices()

            # 绑定删除按钮到删除函数
            delete_button.clicked.connect(delete_suite)

            # 更新索引号
            update_indices()

        # 将 '添加' 按钮连接到添加套件的函数
        add_button.clicked.connect(add_suite)

        # 遍历配置文件中的数据，并添加现有套件
        for param in config['replace_param']:
            add_suite(
                switch=param['switch_checkbox'],
                case_sensitive=param['case_sensitive'],
                target_cont=param['target_cont'],
                replace_cont=param['replace_cont']
            )

        # __________________________________________________________________________>>> 创建 QScrollArea
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)  # 设置为可调整大小
        scroll_area.setWidget(content_widget)

        # __________________________________________________________________________>>> 创建选项卡并设置布局
        optimized_scene_node_name_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(optimized_scene_node_name_tab)
        tab_layout.addWidget(scroll_area)

        # 将选项卡添加到主选项卡部件
        self.tab_widget.addTab(optimized_scene_node_name_tab, '优化名称')

    # 建界面与布局设置页面
    def create_configure_ui_layout_tab(self):
        # 加载语言配置
        configure_ui_layout_lang = self.language['create_configure_ui_layout_tab']

        # 创建节点连接选项卡
        configure_ui_layout_widget = QtWidgets.QWidget()
        configure_ui_layout_layout = QtWidgets.QVBoxLayout(configure_ui_layout_widget)

        # 设置可滚动区域
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QtWidgets.QWidget()

        # 设置滚动区域内布局并对齐
        layout = QtWidgets.QVBoxLayout(scroll_content_widget)
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        # 添加标题文本
        self.add_line_with_text(layout, configure_ui_layout_lang['yyszd_label'])
        layout.addWidget(QtWidgets.QLabel(configure_ui_layout_lang['yy_label']))

        # 创建语言切换菜单
        self.language_combo_box = QtWidgets.QComboBox()

        # 加载语言文件列表
        languages_list = self.load_language_files(self.languages_folder_path)

        # 填充语言选择框
        for lang in languages_list:
            self.language_combo_box.addItem(lang)

        # 设置语言切换事件
        self.language_combo_box.currentIndexChanged.connect(
            lambda *args: self.change_language(self.languages_folder_path)
        )

        # 加载语言配置文件并设置默认语言
        lang_config_path = os.path.join(settings_path, 'language_config.json')
        lang_config = self.dataM.load_json(lang_config_path)

        # 检查配置并设置语言菜单默认值
        for file_name in os.listdir(self.languages_folder_path):
            if lang_config['language_config'] == file_name.replace('.json', ''):
                lang = self.dataM.load_json(os.path.join(self.languages_folder_path, file_name))
                self.language_combo_box.setCurrentText(lang['language_type'])

        layout.addWidget(self.language_combo_box)

        # 将滚动内容添加到滚动区域并放入主布局
        scroll_area.setWidget(scroll_content_widget)
        configure_ui_layout_layout.addWidget(scroll_area)

        # 添加选项卡到界面
        self.tab_widget.addTab(configure_ui_layout_widget, configure_ui_layout_lang['jmybjsz_tab'])

    # 创建标签
    def create_section_label(self, text):
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(11)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        label = QtWidgets.QLabel(text)
        label.setFont(font)
        return label


    def add_line_with_text(self, layout, text):
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小

        layout.addSpacing(4)
        # 创建一个水平布局，用于放置分割线和文字
        h_layout = QtWidgets.QHBoxLayout()

        # 设置内边距和间距，减少分割线和文字之间的距离
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(5)  # 设置分割线和文字的间距

        # 创建左边的分割线
        left_line = QtWidgets.QFrame()
        left_line.setFrameShape(QtWidgets.QFrame.HLine)
        left_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        h_layout.addWidget(left_line)

        # 添加文字
        label = QtWidgets.QLabel(text)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFont(font)
        h_layout.addWidget(label)

        # 创建右边的分割线
        right_line = QtWidgets.QFrame()
        right_line.setFrameShape(QtWidgets.QFrame.HLine)
        right_line.setFrameShadow(QtWidgets.QFrame.Sunken)
        h_layout.addWidget(right_line)

        # 设置左侧和右侧分割线的伸缩因子，使它们与文字等宽
        h_layout.setStretch(0, 1)
        h_layout.setStretch(2, 1)

        # 将水平布局添加到主布局中
        layout.addLayout(h_layout)
        layout.addSpacing(8)

    # 更新相似度最大值滑杆是否需要被禁用
    def update_similarity_max_slider_ui(self):
        if self.config['path_detection_params']['auto_max_val']:
            self.similarity_max_slider.setEnabled(False)
        else:
            self.similarity_max_slider.setEnabled(True)
    # --------------------保存设置内容的函数 开始

    # -----通用
    def modify_config(self, key, cont, file_name = AMS_Config):

        config = self.dataM.load_json(
            os.path.join(settings_path, file_name))

        config[key] = cont

        self.dataM.save_json(
            os.path.join(settings_path, file_name), config)

        ### 初始化配置数据
        self.config = self.dataM.load_json(
           os.path.normpath(os.path.join(settings_path, AMS_Config)))

    def modify_nested_config(self, key_path, cont):
        """
        修改配置文件的特定键值。

        参数:
        value -- 要设置的新值
        key_path -- 包含要修改的键的路径，以列表形式传递，例如 ["ProcSet_Options", "MagicConnectionSetColorSpace"]

        功能:
        1. 加载配置数据。
        2. 根据提供的键路径找到并修改对应的值。
        3. 保存修改后的配置数据。
        """

        # 加载 JSON 配置数据
        config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )

        # 根据给定的键路径逐层访问数据
        current_level = config
        for key in key_path[:-1]:  # 遍历到倒数第二个键
            current_level = current_level[key]  # 进入下一层级

        # 设置最终键的值为新值
        current_level[key_path[-1]] = cont

        # 保存修改后的配置数据
        self.dataM.save_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config)),
            config
        )

        ### 初始化配置数据
        self.config = self.dataM.load_json(
           os.path.normpath(os.path.join(settings_path, AMS_Config)))

        # --------------------保存设置内容的函数
    # -----通用

    # 修改 tex_first_filter_options_list 通道是否要魔法连接的配置文件
    def modify_tex_first_filter_options_list_config(self):
        def main():
            # 获取选中的项
            selected_items = self.tex_first_filter_options_list.selectedItems()

            # 如果没有选中项，则直接返回
            if not selected_items:
                return

            # 提取选中的内容
            selected_values = [item.text() for item in selected_items]
            # 将选中的内容转换为全大写
            selected_values_uppercase = [s.upper() for s in selected_values]

            # 遍历处理数据中的每个通道
            for channel in self.config['magic_conn_config']['conn_params']:
                # 检查当前通道（大写）是否在选中的大写值中
                if channel.upper() in selected_values_uppercase:
                    # 如果匹配，更新配置文件为真
                    self.modify_nested_config(key_path = ['magic_conn_config', 'conn_params', channel],
                                              cont = True)
                else:
                    # 如果不匹配，更新配置文件为假
                    self.modify_nested_config(key_path = ['magic_conn_config', 'conn_params', channel],
                                              cont = False)


        # 使用定时器确保 main 函数在事件队列的下一次迭代中执行
        QtCore.QTimer.singleShot(0, lambda *args:main())

    # 修改 texture_filter_fields 过滤配置文件
    def modify_texture_filter_fields_config(self, channel, val):

        # 处理写入值，并强制转为大写
        output_list = [item.strip().upper() for item in val.split(",")]

        # 保存修改值
        self.modify_nested_config(key_path = ['texture_filter_params', channel],
                                  cont = output_list)

        # 刷新输入框
        self.texture_filter_fields[channel].setText(
                str(output_list)
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , "))


    # 修改 color_space_text 过滤配置文件
    def modify_color_space_text_config(self):
        val = self.color_space_text.toPlainText()

        # 处理写入值，并强制转为大写
        output_list = [item.strip() for item in val.split(",")]

        # 保存修改值
        self.modify_nested_config(key_path = ['color_space_params', 'config'],
                                  cont = output_list)

    def modify_auto_node_connection_config(self):
        def main():
            # 获取选中的项
            selected_items = self.auto_node_connection_list.selectedItems()

            # 如果没有选中项，则直接返回
            if not selected_items:
                return

            # 提取选中的内容
            selected_values = [item.text() for item in selected_items]
            # 将选中的内容转换为全大写
            selected_values_uppercase = [s.upper() for s in selected_values]

            # 遍历处理数据中的每个通道
            for channel in self.config['proc_node_config']['conn_params']:
                # 检查当前通道（大写）是否在选中的大写值中
                if channel.upper() in selected_values_uppercase:
                    # 如果匹配，更新配置文件为真
                    self.modify_nested_config(key_path = ['proc_node_config', 'conn_params', channel],
                                              cont = True)
                else:
                    # 如果不匹配，更新配置文件为假
                    self.modify_nested_config(key_path = ['proc_node_config', 'conn_params', channel],
                                              cont =False)

        # 使用定时器确保 main 函数在事件队列的下一次迭代中执行
        QtCore.QTimer.singleShot(0, main)

    def modify_pro_node_list_config(self, channel, val):
        # 处理写入值，并强制转为大写
        output_list = [item.strip() for item in val.split(",")]

        # 保存修改值
        self.modify_nested_config(key_path = ['proc_node_config','params', channel, 'NodeList'],
                                  cont = output_list)

        # 刷新输入框
        self.node_list_edit[channel].setText(
            str(output_list)
            .replace('[', '')
            .replace(']', '')
            .replace("'", "")
            .replace(",", " , "))

    def add_pro_node_to_list(self, channel):


        # 按住alt键可以清除全部的输入
        if is_modifier_pressed(MAYA_ALT_MODIFIER):
            output_list = self.config["proc_node_config"]["params"][channel]["NodeList"]
            output_list.pop()
        else:
            # 获取选择到的节点
            try:
                select_node = list(process_sl_data().keys())[0]
            except AttributeError:
                return self.feedback.CP('添加到处理节点输入框 ->无法获取选择节点数据')

            output_list = self.config["proc_node_config"]["params"][channel]["NodeList"]
            output_list.append(select_node)

            self.modify_nested_config(key_path = ['proc_node_config', 'params', channel, 'NodeList'],
                                      cont = output_list)

        self.node_list_edit[channel].setText(str(output_list)
        .replace('[', '')
        .replace(']', '')
        .replace("'", "")
        .replace(",", " , "))




    # --------------------保存设置内容的函数 结束

    # 加载语言文件
    def load_language_files(self, folder_path):


        languages_list = []

        # 遍历文件夹中的所有JSON文件
        for file_name in os.listdir(folder_path):

            lang = self.dataM.load_json(os.path.join(folder_path, file_name))
            languages_list.append(lang['language_type'])

        return languages_list

    # 更改语言配置文件
    def change_language(self, language_folder):

        # 获取当前选择的语言
        selected_lang = self.language_combo_box.currentText()

        # 语言配置路径
        lang_config_path = os.path.join(settings_path, 'language_config.json')

        # 加载语言配置文件
        lang_config = self.dataM.load_json(lang_config_path)

        # 遍历文件夹中的所有JSON文件
        for file_name in os.listdir(language_folder):
            lang = self.dataM.load_json(os.path.join(language_folder, file_name))
            if selected_lang == lang['language_type']:
                # 修改语言文件
                lang_config['language_config'] = file_name.replace('.json', '')

                self.feedback.CP(f'语言已修改成:{lang["language_type"]}')

        # 保存修改过后的语言文件
        self.dataM.save_json(lang_config_path, lang_config)
