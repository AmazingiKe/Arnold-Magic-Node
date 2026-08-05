##############################################################################################
# # ++ 导入所需的库和模块

# 1. Maya 库
import maya.cmds as cmds  # 导入 Maya 的 cmds 模块，用于执行 Maya 命令和操作场景
import maya.OpenMayaUI as omui  # 导入 Maya 的 OpenMayaUI 模块，用于操作 Maya 的用户界面
import mtoa.aovs as aovs

# 2. 文件与系统操作
import os  # 提供与操作系统交互的功能，如文件路径操作、目录遍历等
import importlib  # 用于动态导入和重新加载模块，支持模块的按需加载
import shutil


# 3. PySide 库
# 导入 PySide 库，根据可用版本导入 PySide2 或 PySide6
try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance

from contextlib import contextmanager
from .core.paths import ICONS_ROOT, PROJECT_ROOT
# ------------------------------------------
# 获取脚本路径
script_path = os.path.normpath(str(PROJECT_ROOT)) # 获取当前脚本的目录路径
# ------------------------------------------

# 9. 自定义库导入
# 使用项目唯一的模块名，避免 Maya 进程中其他名为 core 的模块污染导入缓存。
from . import arnold_magic_core as core
importlib.reload(core)  # 在开发阶段，重新加载模块以反映对库的更改
from .arnold_magic_core import *
from .arnold_magic_core import DataManager

from . import default_config
from .core.storage import ensure_directory

##############################################################################################

# --------------------初始变量开始

# _______________________________________________________________>>> 插件状态
SoftwareState = "Release"  # 插件状态
# _______________________________________________________________>>> 插件版本号
SoftwareVersion = "1.2.02" # 插件版本号


pluginHomeURL = r"https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69"
pluginFeedbackURL = r"https://flowus.cn/form/7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69"
pluginUpdateDownloadURL = r'https://flowus.cn/amazingike/share/84422156-5158-4b73-9a5f-c5cadbb6625a?code=LZVF69'
pluginHelpDocumentURL = r'https://flowus.cn/amazingike/share/6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69'

datas_path = os.path.normpath(os.path.join(script_path, "Datas"))  # 定义数据文件夹路径 -> 全局变量

settings_path = os.path.normpath(os.path.join(datas_path, "settings"))  # 定义设置配置文件夹路径 -> 全局变量

icon_path = os.path.normpath(str(ICONS_ROOT))  # 定义图标路径 -> 全局变量

render_preset_path = os.path.normpath(os.path.join(datas_path, "render_presets"))  # 定义渲染预设文件夹路径 -> 全局变量

AMS_Config = "Arnold_Magic_Settings.json" # Arnold_Magic_Settings

# 定义全局字体大小变量
SMALL_FONT_SIZE = 10
NORMAL_FONT_SIZE = 14
MEDIUM_FONT_SIZE = 16
LARGE_FONT_SIZE = 18
EXTRA_LARGE_FONT_SIZE = 24
# --------------------初始变量结束

MAYA_SHIFT_MODIFIER = 1
MAYA_ALT_MODIFIER = 8


def is_modifier_pressed(modifier, modifiers=None):
    """检测 Maya 当前的修饰键状态。"""
    if modifiers is None:
        modifiers = cmds.getModifiers()
    return bool(modifiers & modifier)



# --------------------初始变量结束

# 获取Maya主窗口
def get_maya_main_window():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr),QtWidgets.QWidget)

def language_loading():
    dataM = DataManager()

    # 加载语言配置文件并获取 'language_config' 键的值
    language_config = dataM.load_json(
        os.path.join(script_path, 'Datas', 'settings', 'language_config.json'))['language_config']

    # 动态加载相应语言的JSON文件
    language = dataM.load_json(
        os.path.join(script_path, 'Datas', 'languages', f'{language_config}.json'))

    return language


#______________________________________________________________________________>>> 插件设置按钮qt写
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


        self.languages_folder_path = os.path.join(script_path, 'Datas', 'languages')  # 语言文件夹路径

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

        settings_presets_path  = os.path.join(datas_path, "settings_presets")  # 预设文件夹路径
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
        self.open_presets_folder.triggered.connect(lambda *args: os.startfile(os.path.join(datas_path, "settings_presets")))

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
        settings_presets_dir = os.path.join(datas_path, "settings_presets")
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
        presets_dir = os.path.join(datas_path, "settings_presets")
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
        presets_dir = os.path.join(datas_path, "settings_presets")
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
        presets_dir = os.path.join(datas_path, "settings_presets")
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
        lang_config_path = os.path.join(script_path, 'Datas', 'settings', 'language_config.json')

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

#______________________________________________________________________________>>>AOV灯光组管理器

@contextmanager
def block_updates_and_signals(widget):
    widget.setUpdatesEnabled(False)
    widget.blockSignals(True)
    try:
        yield
    finally:
        widget.blockSignals(False)
        widget.setUpdatesEnabled(True)
        widget.viewport().update()


class AOVLightGroupTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(AOVLightGroupTreeWidget, self).__init__(parent)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QTreeWidget.ExtendedSelection)
        self.setUniformRowHeights(True)
        self.itemClicked.connect(self.enable_drag_drop_flags)

    def enable_drag_drop_flags(self, item):
        if item.parent() is None:
            flags = item.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable
        else:
            flags = item.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEditable
            flags &= ~QtCore.Qt.ItemIsDropEnabled
        item.setFlags(flags)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        add_action = menu.addAction("添加父级")
        add_action.triggered.connect(self.add_parent)

        selected = self.selectedItems()
        delete_action = menu.addAction("删除父级")
        if len(selected) == 1 and selected[0].parent() is None:
            delete_action.triggered.connect(lambda: self.delete_parent(selected[0]))
            delete_action.setEnabled(True)
        else:
            delete_action.setEnabled(False)
        menu.exec_(event.globalPos())

    def add_parent(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return

        new_parent = QtWidgets.QTreeWidgetItem()
        new_parent.setText(0, "new_light_group")
        new_parent.setFlags(new_parent.flags() | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable)
        self.addTopLevelItem(new_parent)

        new_parent.setIcon(0, QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png')))

        with block_updates_and_signals(self):
            sorted_items = sorted(selected_items, key=self.get_item_index, reverse=True)
            for item in sorted_items:
                # 仅移动子级项，跳过父级项
                if item.parent() is None:
                    continue
                old_parent = item.parent()
                old_parent.removeChild(item)
                new_parent.addChild(item)
        new_parent.setExpanded(True)

    def delete_parent(self, parent_item):
        if parent_item.parent() is not None:
            return

        children = []
        while parent_item.childCount() > 0:
            child = parent_item.takeChild(0)
            children.append(child)

        with block_updates_and_signals(self):
            for child in children:
                self.addTopLevelItem(child)
            index = self.indexOfTopLevelItem(parent_item)
            if index != -1:
                self.takeTopLevelItem(index)

    def get_item_index(self, item):
        parent = item.parent()
        return parent.indexOfChild(item) if parent else self.indexOfTopLevelItem(item)

    def _is_ancestor(self, item, target):
        parent = target.parent() if target else None
        while parent:
            if parent == item:
                return True
            parent = parent.parent()
        return False

    # 合并两个validate_drop方法为一个更完善的版本
    def validate_drop(self, target, items, drop_indicator_pos):
        """
        验证拖放操作是否符合以下规则：
        1. 禁止拖拽到自身或祖先
        2. 若拖放到某项（OnItem），则只允许拖到顶级项
        3. 若拖放到项上方/下方，新位置的父项必须为顶级项
        4. 父级项不能拖放到子级项内部或成为子级项
        """
        # 禁止拖拽到自身或祖先
        for item in items:
            if self._is_ancestor(item, target):
                return False

        # 处理 OnItem 放置
        if drop_indicator_pos == QtWidgets.QAbstractItemView.OnItem:
            # 仅允许拖放到顶级父级
            if target and self.get_item_depth(target) >= 1:
                return False

        # 处理 Above/Below 放置
        elif drop_indicator_pos in (QtWidgets.QAbstractItemView.AboveItem, QtWidgets.QAbstractItemView.BelowItem):
            # 如果目标存在且是子级，检查其父级是否允许放置
            if target and target.parent() is not None:
                parent = target.parent()
                # 确保父级是顶级项
                if parent.parent() is not None:
                    return False

        # 检查被拖动的父级项是否被非法放置
        for item in items:
            if item.parent() is None:  # 父级项
                # 禁止将父级拖放到其他项内部
                if drop_indicator_pos == QtWidgets.QAbstractItemView.OnItem:
                    return False
                # 禁止将父级拖放到子级附近（会成为子级）
                if target and target.parent() is not None:
                    return False

        return True

    def dropEvent(self, event):
        # 在原有基础上增加更新逻辑
        expanded_state = self._get_expanded_state()
        super(AOVLightGroupTreeWidget, self).dropEvent(event)

        # 获取被移动的项及其新父级
        moved_items = self.selectedItems()
        new_parent = self.itemAt(event.pos())

        with block_updates_and_signals(self):
            for item in moved_items:
                # 如果移动到新的父级下
                if new_parent and new_parent.parent() is None:
                    self.update_light_group(item, new_parent.text(0))
                # 如果移动到顶层
                elif new_parent is None:
                    self.update_light_group(item, "")

        self._restore_expanded_state(expanded_state)

        # 在enable_drag_drop_flags中确保父级可编辑

    def _get_expanded_state(self):
        state = {}
        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            state[id(item)] = item.isExpanded()
            iterator += 1
        return state

    def _restore_expanded_state(self, state):
        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            item.setExpanded(state.get(id(item), False))
            iterator += 1

    def startDrag(self, supported_actions):
        """
        开始拖动操作，构造 QDrag 对象，
        并使用选中项的 MIME 数据启动拖动。
        """
        drag = QtGui.QDrag(self)
        mime_data = self.model().mimeData(self.selectedIndexes())
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.MoveAction)


    def get_item_depth(self, item):
        """
        计算项在树中的深度，根节点深度为 0。
        遍历项的父链，计数每一级父项。
        """
        depth = 0
        parent = item.parent()
        while parent:
            depth += 1
            parent = parent.parent()
        return depth


class AOVLightGroupManager(QtWidgets.QDialog):

    def __init__(self, parent = get_maya_main_window()):

        super(AOVLightGroupManager, self).__init__(parent)

        # 创建实例类
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData()  # 提取数据模块
        self.dataM = DataManager()  # 储存模块


        self.WINDOWS_NAME = f"AOV灯光组管理器  {SoftwareState} : {SoftwareVersion}"


        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('AOVLightGroupManager')

        self.setObjectName('AOVLightGroupManager')
        self.setWindowTitle(self.WINDOWS_NAME)

        # ...窗口长宽
        self.setMinimumSize(1200, 800)  # 设置一个比较小的最小尺寸
        self.setWindowIcon(QtGui.QIcon(icon_path + "\\LightManagerShelf_200.png"))

        # 窗口标志（隐藏放大/缩小按钮）
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        # 初始化数据
        self._initial_settings()
        self._create_widgets()
        self._create_menu()
        self._create_layouts()

    def _initial_settings(self):
        # 缓存文件
        cache = ["RGBA"]

        self.cache_path = os.path.join(script_path, "Datas", "aov_light_group_manager", "cache.json")

        # 如果缓存文件不存在则创建
        if not os.path.exists(self.cache_path):
            self.dataM.save_json(self.cache_path, cache)

    def _create_widgets(self):
        # 刷新按钮
        self.refresh_light_group_tree_button = QtWidgets.QPushButton()
        self.refresh_light_group_tree_button.setIcon(QtGui.QIcon(os.path.join(icon_path, "ResetMode_200.png")))
        self.refresh_light_group_tree_button.setFixedHeight(40)
        self.refresh_light_group_tree_button.setFixedWidth(40)
        self.refresh_light_group_tree_button.setIconSize(QtCore.QSize(32, 32))
        self.refresh_light_group_tree_button.clicked.connect(lambda *args : self._refresh_light_group_tree(icon_path))

        # 选择场景中的灯光
        self.select_lights_button = QtWidgets.QPushButton()
        self.select_lights_button.setIcon(QtGui.QIcon(os.path.join(icon_path, "aiAreaLight.svg")))
        self.select_lights_button.setFixedHeight(40)
        self.select_lights_button.setFixedWidth(40)
        self.select_lights_button.setIconSize(QtCore.QSize(32, 32))
        self.select_lights_button.clicked.connect(lambda *args: self._get_selected_lights_in_group())
        # 灯光搜索框
        self.light_group_search_input = QtWidgets.QLineEdit()
        self.light_group_search_input.setFixedWidth(480)
        self.light_group_search_input.setFixedHeight(40)

        # 添加搜索框文本变化信号连接
        self.light_group_search_input.textChanged.connect(lambda *args :self._filter_light_group_tree())


        # 使用QtreeWidget控件创建一个类似Maya的节点树
        self.light_group_tree_widget = AOVLightGroupTreeWidget(self)
        self.light_group_tree_widget.setHeaderLabels(['AOV灯光组'])

        # 设置灯光树的大小
        self.light_group_tree_widget.setFixedWidth(600)
        # self.light_group_tree_widget.setFixedHeight(700)

        # 刷新灯光组树
        self._refresh_light_group_tree(icon_path)

        # 节点树连接的函数
        self.light_group_tree_widget.itemChanged.connect(
            lambda *args:(
                self.update_light_group_data(),
                self._select_lights()))

        # 节点树的缩放滑轨
        self.light_group_tree_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.light_group_tree_slider.setFixedWidth(600)
        # 获取默认大小
        light_group_tree_slider_font = self.light_group_tree_widget.font().pixelSize()
        # 计算出默认值的的最小一倍和最大一倍
        self.light_group_tree_slider.setMinimum(1)
        self.light_group_tree_slider.setMaximum(light_group_tree_slider_font + light_group_tree_slider_font)
        # 并设置成材质列表的默认大小到滑杆上
        self.light_group_tree_slider.setValue(light_group_tree_slider_font - 8)
        # 滑杆绑定函数
        self.light_group_tree_slider.valueChanged.connect(lambda *args: self.handle_zoom_change())

        AOV_list = ['RGBA', 'coat', 'coat_direct', 'coat_indirect', 'diffuse', 'diffuse_direct', 'diffuse_indirect',
         'direct', 'indirect', 'sheen', 'sheen_albedo', 'sheen_direct', 'sheen_indirect', 'specular', 'specular_albedo',
         'specular_direct', 'specular_indirect', 'sss', 'sss_albedo',
         'sss_direct', 'sss_indirect', 'transmission', 'transmission_albedo', 'transmission_direct',
         'transmission_indirect', 'volume', 'volume_Z', 'volume_albedo', 'volume_direct',
         'volume_indirect', 'volume_opacity']

        # AOV选择列表
        self.aov_select_list_widget = QtWidgets.QListWidget(self)

        # 把aov列表加入到aov列表控件中
        self.aov_select_list_widget.addItems(AOV_list)

        self.aov_select_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.aov_select_list_widget.setFixedWidth(600)

        self.aov_select_list_widget.currentItemChanged.connect(lambda *args: self._modify_aov_select_list_cache())
        # 设置初始选中项
        self._select_aov_select_list_texts(self.dataM.load_json(self.cache_path))


        # 功能按钮
        self.every_cerate_aov_group_button = QtWidgets.QPushButton("创建所有AOV灯光组")
        self.every_cerate_aov_group_button.clicked.connect(lambda *args:(self._create_parent_for_child_items()))
        self.clear_all_lighet_group_button = QtWidgets.QPushButton("清除所有灯光组")
        self.clear_all_lighet_group_button.clicked.connect(lambda *args: self._clear_all_light_groups())
        self.clear_aov_button = QtWidgets.QPushButton("清除AOV中的灯光组")

        self.clear_aov_button.clicked.connect(lambda *args: self._clear_custom_aovs())
        self.create_aov_button = QtWidgets.QPushButton("创建AOV灯光组")
        self.create_aov_button.clicked.connect(lambda *args: self._create_aov_light_group())

    def _create_menu(self):
        pass

    def _create_layouts(self):
        Main_Layout = QtWidgets.QHBoxLayout()




        # 灯光组树布局
        light_group_tree_layout = QtWidgets.QVBoxLayout()
        light_group_tree_function_layout = QtWidgets.QHBoxLayout()
        light_group_tree_function_layout.addWidget(self.refresh_light_group_tree_button)
        light_group_tree_function_layout.addWidget(self.select_lights_button)
        light_group_tree_function_layout.addWidget(self.light_group_search_input)
        light_group_tree_layout.addLayout(light_group_tree_function_layout)
        light_group_tree_layout.addWidget(self.light_group_tree_slider)
        light_group_tree_layout.addWidget(self.light_group_tree_widget)


        aov_select_list_layout = QtWidgets.QVBoxLayout()


        aov_select_list_button_layout_01 = QtWidgets.QHBoxLayout()
        aov_select_list_layout.addLayout(aov_select_list_button_layout_01)
        aov_select_list_button_layout_01.addWidget(self.every_cerate_aov_group_button)
        aov_select_list_button_layout_01.addWidget(self.clear_all_lighet_group_button)

        aov_select_list_layout_02 = QtWidgets.QHBoxLayout()
        aov_select_list_layout.addLayout(aov_select_list_layout_02)
        aov_select_list_layout_02.addWidget(self.aov_select_list_widget)

        aov_select_list_button_layout_03 = QtWidgets.QVBoxLayout()
        aov_select_list_layout.addLayout(aov_select_list_button_layout_03)
        aov_select_list_button_layout_03.addWidget(self.clear_aov_button)
        aov_select_list_button_layout_03.addWidget(self.create_aov_button)

        Main_Layout.addLayout(light_group_tree_layout)
        Main_Layout.addLayout(aov_select_list_layout)

        self.setLayout(Main_Layout)

    # 刷新灯光组树的内容
    def _refresh_light_group_tree(self, icon_path=None):
        """按AOV灯光组结构刷新树控件"""

        # 获取场景中的阿诺德灯光
        lights_and_type = self.getnodedata.get_scene_arnold_lights_and_type()
        light_groups = self.getnodedata.get_light_group(lights_and_type)

        # 清空当前 QTreeWidget 内容
        self.light_group_tree_widget.clear()

        # 图标路径字典 (可以替换为实际的图标路径)
        icon_paths = {
            'aiAreaLight': os.path.join(icon_path, 'aiAreaLight.svg'),
            'aiSkyDomeLight': os.path.join(icon_path, 'aiSkyDomeLight.svg'),
            'aiPhotometricLight': os.path.join(icon_path, 'aiPhotometricLight.svg'),
            'aiMeshLight': os.path.join(icon_path, 'aiMeshLight.svg'),
            'aiLightPortal': os.path.join(icon_path, 'aiLightPortal.svg'),
            'directionalLight' :  os.path.join(icon_path, 'directionalLight'),
            'spotLight' :  os.path.join(icon_path, 'spotLight'),
            'areaLight' :  os.path.join(icon_path, 'areaLight'),
            'pointLight': os.path.join(icon_path, 'pointLight'),
            'default': os.path.join(icon_path, 'aiAreaLight.svg')  # 如果找不到对应的图标就用这个
        }

        # 父级节点的通用图标
        parent_icon = QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png'))

        # 创建树形结构
        for light_group, lights in light_groups.items():


            parent_item = QtWidgets.QTreeWidgetItem(self.light_group_tree_widget, [light_group])
            parent_item.setIcon(0, parent_icon)  # 设置父级节点图标
            parent_item.setFlags(
                QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsSelectable |
                QtCore.Qt.ItemIsDropEnabled
            )

            # 添加子节点
            for light in lights:
                child_item = QtWidgets.QTreeWidgetItem(parent_item, [light])
                child_item.setFlags(
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable |
                    QtCore.Qt.ItemIsDragEnabled
                )

                # 设置子节点的图标
                light_type = lights_and_type[light]
                icon_path = icon_paths.get(light_type, icon_paths['default'])
                child_item.setIcon(0, QtGui.QIcon(icon_path))

        self.light_group_tree_widget.expandAll()

    # aov搜索框函数
    def _filter_light_group_tree(self):
        """根据搜索框内容过滤灯光组树"""
        keyword = self.light_group_search_input.text().lower().strip()

        # 遍历所有顶级项（父级灯光组）
        for i in range(self.light_group_tree_widget.topLevelItemCount()):
            parent_item = self.light_group_tree_widget.topLevelItem(i)
            parent_matched = keyword in parent_item.text(0).lower()
            any_child_matched = False

            # 遍历子级灯光项
            for j in range(parent_item.childCount()):
                child_item = parent_item.child(j)
                child_matched = keyword in child_item.text(0).lower()
                child_item.setHidden(not child_matched)

                if child_matched:
                    any_child_matched = True

            # 设置父级可见性：父级匹配或任意子级匹配时显示
            parent_visible = parent_matched or any_child_matched
            parent_item.setHidden(not parent_visible)

            # 自动展开匹配的父级
            if parent_visible:
                parent_item.setExpanded(True)

        # 处理空关键字情况
        if not keyword:
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                parent_item = self.light_group_tree_widget.topLevelItem(i)
                parent_item.setHidden(False)
                parent_item.setExpanded(True)  # 恢复默认展开状态
                for j in range(parent_item.childCount()):
                    parent_item.child(j).setHidden(False)

    #  获取灯光组树控件有什么内容
    def _get_all_items(self):
        def traverse_items(item):
            data = {
                "text": item.text(0),  # 获取第0列的文本
                "children": []
            }
            for i in range(item.childCount()):
                child_item = item.child(i)
                data["children"].append(traverse_items(child_item))
            return data

        root_data = []
        for i in range(self.light_group_tree_widget.topLevelItemCount()):
            root_item = self.light_group_tree_widget.topLevelItem(i)
            root_data.append(traverse_items(root_item))

        return root_data

    # 更新场景灯光的组
    def update_light_group_data(self,):
        """更新灯光组数据，根据当前树状结构同步到 Maya 灯光节点。"""

        # 获取灯光组树的数据
        items = self._get_all_items()

        # 对灯光组进行更新
        for item in items:
            if item['children']:  # 父级节点存在子节点
                current_light_group = item['text']  # 当前灯光组的名称

                for light_child_item in item['children']:
                    light_name = light_child_item['text']  # 灯光名称
                    try:
                        old_light_group = cmds.getAttr(f"{light_name}.aiAov")  # 获取旧灯光组

                        if current_light_group != old_light_group:
                            if isinstance(current_light_group, str):
                                cmds.setAttr(f"{light_name}.aiAov", current_light_group, type="string")
                            else:
                                self.feedback.CPW(f"灯光组名称必须为字符串，当前为：{type(current_light_group)}")

                    except Exception as e:
                        self.feedback.CPW(f"更新灯光 '{light_name}' 的灯光组 '{current_light_group}' 失败: {e}")

    # 选择到灯光
    def _select_lights(self):
        """选择"""
        # 获取灯光组树的所有选中项
        selected_items = self.light_group_tree_widget.selectedItems()

        # 创建一个列表来存储所有选中的灯光名称
        selected_lights = []

        for item in selected_items:
            try:
                light_name = item.text(0)
                if cmds.objExists(light_name):  # 检查对象是否存在
                    selected_lights.append(light_name)
            except Exception as e:
                print(f"错误：无法选择 {item.text(0)} - {e}")

        # 如果存在有效的灯光对象列表，则一次性选择
        if selected_lights:
            cmds.select(selected_lights, replace=True)  # 全选
        else:
            cmds.select(clear=True)  # 如果列表为空，清除选择

    # 处理滑动条变化事件
    def handle_zoom_change(self):
        """处理滑动条变化事件"""
        # 假设滑动条范围是 50-200（表示50%到200%）
        scale_factor = self.light_group_tree_slider.value()
        font = QtGui.QFont()
        font.setPointSize(scale_factor)
        self.light_group_tree_widget.setFont(font)
        # 设置图标大小
        icon_size = scale_factor* 2
        self.light_group_tree_widget.setIconSize(QtCore.QSize(icon_size, icon_size))

    # 获取到场景选择灯光然后在选择灯光组
    def  _get_selected_lights_in_group(self):
        """
        获取当前场景中选择的灯光，并根据其所属的灯光组进行分类。
        返回一个列表，包含选中灯光组中与当前选择灯光匹配的灯光。
        """
        selected_lights = cmds.ls(selection=True, type='transform')  # 获取当前选择的物体

        matching_lights = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self.light_group_tree_widget)

        while iterator.value():
            item = iterator.value()
            item.setSelected(False)  # 取消所有节点的选择状态

            light_group_name = item.text(0)  # 假设灯光组名称在第 0 列

            # 如果节点名称与选中灯光匹配，就把它加入列表
            if light_group_name in selected_lights:
                item.setSelected(True)
                matching_lights.append(light_group_name)

            iterator += 1

        return matching_lights  # 返回一个列表，包含匹配的灯光名称

    # 选择aov
    def _select_aov_select_list_texts(self, texts):  # texts 是一个字符串列表
        self.aov_select_list_widget.clearSelection()  # 清除所有选择
        for text in texts:
            items = self.aov_select_list_widget.findItems(text, QtCore .Qt.MatchExactly)  # 查找完全匹配的项
            for item in items:
                item.setSelected(True)  # 标记为选中

    # 创建AOV灯光组
    def _create_aov_light_group(self):
        """
        创建AOV灯光组系统，将选中的灯光分组绑定到指定AOV通道
        流程：
        1. 获取用户选择的灯光组和AOV通道配置
        2. 遍历每个灯光组，为其创建对应的AOV通道
        3. 避免重复创建已存在的AOV节点
        4. 设置AOV节点参数
        """
        # 获取用户选择的灯光组配置
        selected_groups = self._get_all_items()
        # 从缓存加载AOV通道配置数据
        aov_channels = self.dataM.load_json(self.cache_path)

        # 遍历每个灯光组配置
        for group in selected_groups:
            # 跳过空组（根据业务逻辑需要可以调整）
            if not group['children']:
                continue

            # 获取当前灯光组名称
            light_group_name = group['text']

            # 跳过默认灯光组（根据业务逻辑需要可以调整）
            if light_group_name == 'default':
                continue

            # 为每个AOV通道创建对应的灯光组AOV
            for channel in aov_channels:
                # 生成符合规范的AOV名称（通道_灯光组）
                aov_name = f"{channel}_{light_group_name}"

                # 检查AOV是否已存在（优化后的检查方式）
                if self._aov_exists(aov_name):
                    print(f"AOV '{aov_name}' 已存在，跳过创建")
                    continue

                try:
                    # 创建AOV节点并配置参数
                    self._create_configured_aov(aov_name)
                    print(f"成功创建AOV：{aov_name}")
                except Exception as e:
                    print(f"创建AOV '{aov_name}' 失败：{str(e)}")
                    continue

    # 检查AOV是否存在
    def _aov_exists(self, aov_name):
        """
        检查指定名称的AOV是否已存在
        :param aov_name: 需要检查的AOV名称
        :return: bool - 是否存在
        """
        # 获取场景中所有aiAOV节点
        existing_aovs = cmds.ls(type='aiAOV') or []

        # 检查名称是否匹配（比遍历属性更高效）
        return any(cmds.getAttr(f"{aov}.name") == aov_name for aov in existing_aovs)

    # 创建并配置AOV节点
    def _create_configured_aov(self, aov_name):
        """
        创建并配置单个AOV节点
        :param aov_name: 需要创建的AOV名称
        """
        # 创建AOV节点（使用Arnold API接口）
        aov_interface = aovs.AOVInterface()
        new_aov = aov_interface.addAOV(aov_name)

        # 构造节点名称（arnold默认命名规则）
        aov_node = f"aiAOV_{aov_name}"

        # 参数配置（根据需求可扩展更多参数）
        # 6 = RGBA类型（根据实际需要确认数值是否正确）
        # 注意：Maya 2020+版本建议使用aov_interface.set_aov_type(...)方法
        if cmds.objExists(aov_node):
            cmds.setAttr(f"{aov_node}.type", 6)  # 设置AOV类型
            cmds.setAttr(f"{aov_node}.enabled", True)  # 启用AOV
        else:
            raise RuntimeError(f"AOV节点 {aov_node} 创建失败")
        # 储存配置文件


    # 为所有没有父级的子级项创建同名父级，并将子级移动至其下
    def _create_parent_for_child_items(self):
        """
        为没有父级的子级项或default组内的子级项创建同名父级，并将子级移动至其下
        规则：
        1. 为没有父级的灯光项创建同名父级组
        2. 为default组内的灯光项创建同名父级组（即使它们已经有父级）
        3. 其它已有父级的灯光项保持不变
        4. 确保有default父级组存在
        5. 删除除default外的空父级组
        """
        self.update_light_group_data()  # 同步数据到Maya
        parent_icon = QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png'))  # 父级图标

        with block_updates_and_signals(self.light_group_tree_widget):
            # 查找default父级
            default_parent = None
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                top_item = self.light_group_tree_widget.topLevelItem(i)
                if top_item.text(0) == "default":
                    default_parent = top_item
                    break

            # 如果default父级不存在，创建一个
            if not default_parent:
                default_parent = QtWidgets.QTreeWidgetItem()
                default_parent.setText(0, "default")
                default_parent.setIcon(0, parent_icon)
                self.light_group_tree_widget.addTopLevelItem(default_parent)
                default_parent.setExpanded(True)

            # 收集需要处理的子级项（无父级的项或default组内的项）
            items_to_process = []
            default_children = []

            # 先收集所有顶级项（没有父级的灯光项）
            top_level_items = []
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                item = self.light_group_tree_widget.topLevelItem(i)
                # 检查是否为灯光项（无子项的项）
                if item.childCount() == 0:
                    top_level_items.append(item)

            # 收集default组内的子级项
            for j in range(default_parent.childCount()):
                default_children.append(default_parent.child(j))

            # 合并需要处理的项
            items_to_process.extend(top_level_items)
            items_to_process.extend(default_children)

            # 处理每个需要移动的子级项
            for child_item in items_to_process:
                child_name = child_item.text(0)

                # 跳过处理名为"default"的子项，防止循环引用
                if child_name == "default":
                    continue

                # 查找是否已有同名父级
                existing_parent = None
                for i in range(self.light_group_tree_widget.topLevelItemCount()):
                    top_item = self.light_group_tree_widget.topLevelItem(i)
                    if top_item.text(0) == child_name and top_item != child_item:
                        existing_parent = top_item
                        break

                # 处理找到的同名父级或创建新父级
                if existing_parent:
                    # 父级已存在则移动子项
                    current_parent = child_item.parent()
                    if current_parent:
                        current_parent.removeChild(child_item)
                    else:  # 顶级项
                        index = self.light_group_tree_widget.indexOfTopLevelItem(child_item)
                        if index != -1:
                            self.light_group_tree_widget.takeTopLevelItem(index)
                    existing_parent.addChild(child_item)
                else:
                    # 创建新父级并设置属性
                    new_parent = QtWidgets.QTreeWidgetItem()
                    new_parent.setText(0, child_name)
                    new_parent.setIcon(0, parent_icon)

                    # 先处理从原父级移除
                    current_parent = child_item.parent()
                    if current_parent:
                        current_parent.removeChild(child_item)
                    else:  # 顶级项
                        index = self.light_group_tree_widget.indexOfTopLevelItem(child_item)
                        if index != -1:
                            self.light_group_tree_widget.takeTopLevelItem(index)

                    # 添加到新父级并将新父级添加到树
                    new_parent.addChild(child_item)
                    self.light_group_tree_widget.addTopLevelItem(new_parent)
                    new_parent.setExpanded(True)

            # 删除空父级（排除"default"）
            for i in range(self.light_group_tree_widget.topLevelItemCount() - 1, -1, -1):
                top_item = self.light_group_tree_widget.topLevelItem(i)
                if top_item.childCount() == 0 and top_item.text(0) != "default":
                    self.light_group_tree_widget.takeTopLevelItem(i)

        # 完成后同步更新
        self.update_light_group_data()

    # 清除所有父级并将灯光移动到默认default组
    def _clear_all_light_groups(self):
        """
        清除非default父级的所有灯光组，将子项移动到default父级下
        流程：
        1. 确保default父级存在
        2. 收集所有非default父级
        3. 将子项移动到default父级下
        4. 删除空父级
        """
        self.update_light_group_data()  # 同步初始数据
        with block_updates_and_signals(self.light_group_tree_widget):
            # 获取或创建default父级
            default_parent = None
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                item = self.light_group_tree_widget.topLevelItem(i)
                if item.text(0) == "default":
                    default_parent = item
                    break
            # 若不存在则创建default父级
            if not default_parent:
                default_parent = QtWidgets.QTreeWidgetItem()
                default_parent.setText(0, "default")
                default_parent.setIcon(0, QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png')))
                self.light_group_tree_widget.addTopLevelItem(default_parent)
                default_parent.setExpanded(True)
            # 收集所有需要删除的非default父级
            parents_to_remove = []
            for i in range(self.light_group_tree_widget.topLevelItemCount()):
                item = self.light_group_tree_widget.topLevelItem(i)
                if item.text(0) != "default":
                    parents_to_remove.append(item)
            # 处理每个待删除父级的子项
            for parent in parents_to_remove:
                # 移动所有子项到default父级
                while parent.childCount() > 0:
                    child = parent.takeChild(0)  # 取出第一个子项
                    default_parent.addChild(child)
                # 删除空父级
                index = self.light_group_tree_widget.indexOfTopLevelItem(parent)
                if index != -1:
                    self.light_group_tree_widget.takeTopLevelItem(index)
            # 确保default父级至少有一个子项
            if default_parent.childCount() == 0:
                default_child = QtWidgets.QTreeWidgetItem()
                default_child.setText(0, "default_light")
                default_parent.addChild(default_child)
        self.update_light_group_data()  # 最终数据同步

    # 清除通过插件创建的所有自定义AOV通道
    def _clear_custom_aovs(self):
        """
        清除通过插件创建的所有自定义AOV通道
        - 仅删除名称符合"通道_灯光组"格式的AOV节点
        - 保留RGBA/P/Z/N等基础通道
        - 支持同时清理多个灯光组配置
        """
        # 获取用户选择的通道配置（从缓存加载）
        selected_channels = self.dataM.load_json(self.cache_path)

        # 获取场景中所有aiAOV节点
        all_aovs = cmds.ls(type='aiAOV') or []

        # 遍历处理每个AOV节点
        deleted_aovs = []
        for aov_node in all_aovs:
            try:
                aov_name = cmds.getAttr(f"{aov_node}.name")
                # 匹配规则：通道名_任意字符 且通道名在用户选择列表中
                if any(aov_name.startswith(f"{channel}_") for channel in selected_channels):
                    cmds.delete(aov_node)
                    deleted_aovs.append(aov_name)
            except Exception as e:
                self.feedback.CPW(f"清理AOV失败: {aov_node} - {str(e)}")

        # 反馈清理结果
        result_msg = f"已清理自定义AOV通道 [{len(deleted_aovs)}个]:\n" + "\n".join(deleted_aovs)
        self.feedback.CPW(result_msg if deleted_aovs else "未找到需要清理的自定义AOV通道")


    # 异步保存 AOV 选择列表的缓存数据到指定文件路径中
    def _modify_aov_select_list_cache(self):
        """
        异步保存 AOV 选择列表的缓存数据到指定文件路径中。

        此方法使用 QtCore.QTimer.singleShot(0, ...) 进行异步调用，
        确保在 UI 操作（例如点击或选择改变）完成后再执行保存操作，
        避免阻塞或数据不完整的情况。

        工作流程：
        1. 获取 QListWidget 中所有被选中的项。
        2. 提取每个选中项的文本内容并生成列表。
        3. 使用 self.dataM.save_json() 方法将数据保存到缓存文件路径。
        """

        def modify_cache():
            # 从 QListWidget 中获取当前选中的项列表
            selected_items = self.aov_select_list_widget.selectedItems()

            # 提取每个选中项的文本内容，组成新的缓存数据列表
            new_cache_data = [item.text() for item in selected_items]

            # 将缓存数据保存到指定路径 (self.cache_path)
            self.dataM.save_json(self.cache_path, new_cache_data)

        # 使用 Qt 的定时器单次调用机制来延迟执行保存操作
        QtCore.QTimer.singleShot(0, lambda *args: modify_cache())


def delete_window_if_existe(window_name):
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == window_name:
            widget.close()
            widget.deleteLater()

def  AOVLightGroupManagerInstance():
    aov_light_group_manager = AOVLightGroupManager()
    aov_light_group_manager.show()







#______________________________________________________________________________>>> 贴图批量导入器
class TextureBatchImporterWin:
    def __init__(self):
        WIN_TITLE = "TextureBatchImporterWin  Beta:1.0"

        # 判断窗口是否存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)

        # 创建主窗口
        self.window = cmds.workspaceControl(WIN_TITLE, retain=False, floating=True,w=300,h=300)








        # 显示窗口
        cmds.showWindow(self.window)

        def create_widgets(self):
            pass

# 设置uv模式
def uv_preset_menu(uv_preset):
    # 初始化反馈模块
    feedback = FeedbackPrompt() # 错误提示模块

    # 加载语言数据
    AMDUI_WIN_language = language_loading()['ArnoldMagicNode']['AMDUI_WIN']['create_widgets']
    UVPM_language = language_loading()['ArnoldMagicNode']['UVPM']

    # 处理选中的节点数据
    select_node = process_sl_data()

    if select_node is None:
        return

    if 'file' not in select_node:
        feedback.CPW(UVPM_language["04"])  # 请选择纹理节点
        return

    uv_mode_list = {AMDUI_WIN_language['uv_preset'][0]:0,
                    AMDUI_WIN_language['uv_preset'][1]:1,
                    AMDUI_WIN_language['uv_preset'][2]:2,
                    AMDUI_WIN_language['uv_preset'][3]:3,
                    AMDUI_WIN_language['uv_preset'][4]:4}

    for i in uv_mode_list:
        if i == uv_preset:
            try:
                # 遍历选中的节点文件，设置UV模式
                for sl_node in select_node["file"]:
                    cmds.setAttr(sl_node + ".uvTilingMode",uv_mode_list[i])
                    feedback.CP(f'{UVPM_language["01"]}<{sl_node}>{UVPM_language["02"]}{i}')
                return
            except Exception as e:
                # 捕获并输出异常信息
                feedback.CPW(f'{UVPM_language["03"]} :{e}')

# 设置颜色空间
def color_space_preset_menu(color_space_preset):
    feedback = FeedbackPrompt() # 错误提示模块
    select_node = process_sl_data() # 选择到的节点

    lang = language_loading()['ArnoldMagicNode']['CSPM']

    if select_node == None:
        return

    if 'file' not in select_node:
        feedback.CPW(lang['01']) # '请选纹理贴图节点'
        return

    for i in select_node['file']:
        cmds.setAttr(i + '.colorSpace', color_space_preset, type='string')
        feedback.CP(f"{lang['02']}<{i}>{lang['02']}<{color_space_preset}>") # 已经把 设置成

# 自动设置颜色空间
def AutoSet_TexColorSpace():
    ### 实例模块
    dataM = DataManager() # 数据管理模块
    NodePro = NodeProcessor()
    feedback = FeedbackPrompt()

    lang = language_loading()['ArnoldMagicNode']['ASTCS']

    # 加载数据
    texture_processing_data = dataM.load_json(
        os.path.join(settings_path, AMS_Config))

    FilterData = texture_processing_data["texture_filter_params"] # 过滤贴图的数据

    select_node = process_sl_data()

    if select_node == None:
        return

    if 'file' not in select_node:
        feedback.CP(lang['01']) # 请选纹理贴图节点
        return

    NodePro.AutoSetTexColorSpace(texture_processing_data['color_space_params']['params'] , select_node['file'], FilterData)

# 自动设置UDIM
def auto_set_file_node_udim():
    NodePro = NodeProcessor()
    feedback = FeedbackPrompt()
    select_node = process_sl_data()

    lang = language_loading()['ArnoldMagicNode']['ASFNU']

    if select_node == None:
        return

    if 'file' not in select_node:
        feedback.CP(lang['01']) # 请选纹理贴图节点
        return

    NodePro.auto_set_udim(select_node['file'])

# !!!!!!!!!!如果要绑定到键位需要另外调整，需要让他有个写出路径，然后读取路径

direct_node_select = False
# 连接到一次输出节点可以把任意节点输出到这个输出节点上
class direct_connection_button(object):

    def __init__(self):
        global direct_node_select

        # 初始化节点
        self.initial_global_config()


        self.select_node = process_sl_data()

        # 如果没有选择节点会直接退出函数
        if self.select_node == None:
            return


        for i in self.select_node:
            if i == "shadingEngine":
                direct_node_select = self.select_node[i][0]
                self.feedback.CP(f"{self.lang['__init__']['01']}<{direct_node_select}>") # 节点设置成功
                return

        if direct_node_select == False:
            self.feedback.CP(self.lang['__init__']['02']) # 请先选择输出节点
            return


        self.connection_node()

    def initial_global_config(self):
        self.feedback = FeedbackPrompt() # 错误提示模块
        self.lang = language_loading()['ArnoldMagicNode']['DC_Button']


    def connection_node(self):
        # 可以自行添加输出端口名字
        out_name = ["outColor","outAlpha","outValue"]

        cnlang = self.lang['connection_node']


        for i in self.select_node:
            for out in out_name:
                # 获取输出节点的输入端口是什么
                shadingEngine_input = cmds.listConnections(direct_node_select,  source=True, destination=False, plugs=True)

                # 获取输入节点名字
                shadingEngine_input_node_name = None
                try:
                    shadingEngine_input_node_name = shadingEngine_input[0].split('.')
                    shadingEngine_input_node_name = shadingEngine_input_node_name[0]
                except:
                    pass

                # 如果选择节点名字一样就会执行，如果不一样就不会执行
                if shadingEngine_input_node_name == self.select_node[i][0]:
                    # 这个判断是为了切换["outColor","outAlpha"]的，如果是outColor就退出一次循环只循环outAlpha的
                    if shadingEngine_input == None:
                        pass
                    else:
                        # 使用 '.' 作为分隔符分割字符串
                        shadingEngine_input = shadingEngine_input[0].split('.')

                        # 获取 '.' 后面的部分
                        shadingEngine_input_out = shadingEngine_input[1]

                        if shadingEngine_input_out == out:
                            continue

                node_name = self.select_node[i][0]

                try:
                    cmds.connectAttr(node_name+'.'+out, direct_node_select+'.'+"surfaceShader", f=True)
                    return
                except:
                    self.feedback.CPW(f"{cnlang['01']}<{node_name}:{out}>{cnlang['02']}<{direct_node_select}:shadingEngine>{cnlang['03']}") # 你的 节点无法连接到 节点上

# 统一UV节点
def unify_uv_node_button():

    # 如果没有选择节点会返回None，返回None会关闭函数
    if process_sl_data() == None:
        return
    else:
        node_pro = NodeProcessor()
        if process_sl_data().get('place2dTexture') is None:
            uv_list = None
        else:
            uv_list = process_sl_data()['place2dTexture']

        if 'file' not in process_sl_data():
            return

        node_pro.unify_uv_node(process_sl_data()['file'], uv_list)

# ___________________________________________________________>>>预设存储等的功能

# 渲染预设菜单设置
class rendering_preset_menu(object):

    def __init__(self, menu_sl_val):
        # _______________________________________________________________________>>> 初始化实例和模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.dataM = DataManager()  # 数据管理模块实例

        # _______________________________________________________________________>>> 初始化常用变量
        self.attribute_types = ["bool", "int", "float", "string"]  # 属性类型列表
        self.rederer_attribute_types = ["bool", "float", "string"]  # 渲染器属性类型列表

        # _______________________________________________________________________>>> 初始化配置变量并加载数据
        # 加载渲染设置数据
        self.Render_settings_Data = self.dataM.load_json(
            os.path.normpath(
                os.path.join(datas_path, 'render_presets', menu_sl_val + '.json')
            )
        )
        # 读取渲染配置参数
        config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )['render_preset_params']

        # 语言变量
        self.lang = language_loading()['ArnoldMagicNode']['RenderPM']

        # _______________________________________________________________________>>> 检查并应用配置参数

        # 处理默认渲染属性写入
        if config['default_rendering_properties_write_options']:
            try:
                self.set_default_rendering_properties()  # 设置默认渲染属性
                self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["01"]}') # | 默认渲染属性成功写入
            except Exception as e:
                self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["02"]} {e}') # | 设置默认渲染属性时出错:

        # 检查MAYA节点是否被默认创建了，如果没有会直接退出函数
        if not cmds.objExists('defaultArnoldRenderOptions'):
            self.feedback.CPW({self.lang["__init__"]["03"]}) # 没检测到默认阿诺德渲染器节点，无法写入阿诺德的内容请切换渲染器先
            return

        # 处理渲染属性写入
        if config.get('rendering_properties_write_options'):
            try:
                self.set_rendering_properties()  # 设置渲染属性
                self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["04"]}') # | 阿诺德渲染属性成功写入
            except Exception as e:
                self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["05"]} {e}') # | 设置渲染属性时出错:

        # 处理AOV属性写入
        if config.get('AOV_properties_properties_write_options'):
            try:
                self.del_original_AOV()  # 删除原有的AOV属性
            except Exception as e:
                self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["06"]} {e}') # | 删除原有AOV属性时出错:

            try:
                # 检查是否有AOV属性，如果有则写入，否则提示
                aov_properties = self.Render_settings_Data.get('AOV_properties')
                if aov_properties:
                    self.set_AOV()  # 写入AOV属性
                    self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["07"]}') # | 阿诺德AOV属性成功写入
                else:
                    self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["08"]}') # | 配置里没有AOV，将不会写入AOV参数
            except Exception as e:
                self.feedback.CP(f'<{menu_sl_val}> {self.lang["__init__"]["09"]} {e}') # | 处理AOV属性时出错:

    # 设置阿诺德默认参数
    def set_default_rendering_properties(self):
        for i in self.Render_settings_Data['default_rendering_properties']:
            for key, val in self.Render_settings_Data['default_rendering_properties'][i].items():
                try:
                    cmds.setAttr(f'{i}.{key}', val)
                except:
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f'{i}.{key}', val, type= attribute_type)
                        except:
                            pass

    # 阿诺德预设参数
    def set_rendering_properties(self):
        for i in self.Render_settings_Data['rendering_properties']:
            for key, val in self.Render_settings_Data['rendering_properties'][i].items():
                try:
                    cmds.setAttr(f'{i}.{key}', val)
                except:
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f'{i}.{key}', val, type= attribute_type)
                        except:
                            pass

    # 设置AOV
    def set_AOV(self):
        Aov_data_file = self.Render_settings_Data['AOV_properties']

        # 如果有cryptomatteAOV就创建cryptomatte节点
        for aov_name in Aov_data_file:
            aov_name = aov_name.upper()
            searchObj = re.search('CRYPTO' , aov_name, re.IGNORECASE)
            if searchObj:
                cryptomatte_node_name = cmds.shadingNode('cryptomatte', app=True)
                break

        aov_list_index = 0
        for aiAov_name in Aov_data_file:

            # 创建aiAov_node节点
            aiAov_node = cmds.shadingNode("aiAOV", app= True, name= Aov_data_file[aiAov_name][0]['aov_name'])

            # 设置Aov节点
            for attr_name in Aov_data_file[aiAov_name][1]['aov_attributes']:

                # 尝试用不同的类型设置
                try:
                    # 尝试不指定类型的设置
                    cmds.setAttr(f"{aiAov_node}.{attr_name}", Aov_data_file[aiAov_name][1]['aov_attributes'][attr_name])

                except Exception as e:
                    # 如果不指定类型的设置失败，尝试不同类型的设置
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f"{aiAov_node}.{attr_name}", Aov_data_file[aiAov_name][1]['aov_attributes'][attr_name],type=attribute_type)
                            break
                        except Exception as e:
                            pass


            # 创建driver节点
            driver_node = cmds.shadingNode("aiAOVDriver", app= True, name= Aov_data_file[aiAov_name][2]['driver']['driver_name'])


            # 设置driver节点
            for attr_name in Aov_data_file[aiAov_name][2]['driver']['driver_attribute']:


                try:
                    # 尝试用不同的类型设置
                    cmds.setAttr(f"{driver_node}.{attr_name}",  Aov_data_file[aiAov_name][2]['driver']['driver_attribute'][attr_name])

                except Exception as e:
                    # 如果不指定类型的设置失败，尝试不同类型的设置
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f"{driver_node}.{attr_name}",  Aov_data_file[aiAov_name][2]['driver']['driver_attribute'][attr_name],type=attribute_type)
                            break
                        except Exception as e:
                            pass



            # 把driver连接到aiAov_node
            cmds.connectAttr(driver_node + ".message", aiAov_node + ".outputs[0].driver")

            # 创建filter节点
            filter_node = cmds.shadingNode("aiAOVFilter", app= True, name= Aov_data_file[aiAov_name][3]['filter']['filter_name'])

            # 设置filter节点
            for attr_name in Aov_data_file[aiAov_name][3]['filter']['filter_attribute']:


                try:
                    # 尝试用不同的类型设置
                    cmds.setAttr(f"{filter_node}.{attr_name}",  Aov_data_file[aiAov_name][3]['filter']['filter_attribute'][attr_name])

                except Exception as e:
                    # 如果不指定类型的设置失败，尝试不同类型的设置
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f"{filter_node}.{attr_name}",  Aov_data_file[aiAov_name][3]['filter']['filter_attribute'][attr_name],type=attribute_type)
                            break
                        except Exception as e:
                            pass

            # 把filter连接到aiAov_node
            cmds.connectAttr(filter_node + ".message", aiAov_node + ".outputs[0].filter")


            # 把aiAov_node连接到defaultArnoldRenderOptions
            cmds.connectAttr(aiAov_node + ".message", f'defaultArnoldRenderOptions.aovList[{aov_list_index}]',force= True)


            # 判断如果是crypto的话就进行连接crypto节点
            searchObj = re.search('CRYPTO' , aiAov_name.upper(), re.IGNORECASE)
            if searchObj:
                cmds.connectAttr(cryptomatte_node_name + ".outColor", f'{aiAov_node}.defaultValue',force= True)

            aov_list_index += 1

    # 删除原始的AOV
    def del_original_AOV(self):
        del_name_node = []

        # OLD
        # nodes_to_keep = ["defaultArnoldFilter", "defaultArnoldDriver", "defaultArnoldDisplayDriver"]

        # NEW
        nodes_to_keep = [
            "persp", "top", "front", "side", "defaultLightSet", "defaultObjectSet",
            "defaultLayer", "layerManager", "dof1", "dynController1",
            "globalCacheControl", "hardwareRenderGlobals", "hardwareRenderingGlobals",
            "defaultHardwareRenderGlobals", "ikSystem", "lambert1", "lightLinker1",
            "particleCloud1", "characterPartition", "renderPartition",
            "poseInterpolatorManager", "sequenceManager1", "shaderGlow1",
            "shapeEditorManager", "standardSurface1", "strokeGlobals", "time1",
            "defaultViewColorManager", "defaultArnoldDisplayDriver",
            "defaultArnoldDriver", "defaultArnoldFilter", "defaultArnoldRenderOptions"
                        ]

        aiAov_name_list = cmds.listConnections("defaultArnoldRenderOptions.aovList", source=True)

        if aiAov_name_list == None:
            return

        del_name_node.append(aiAov_name_list)

        for i in aiAov_name_list:
            filter_node = cmds.listConnections(f"{i}.outputs[0].filter", source=True)
            driver_node = cmds.listConnections(f"{i}.outputs[0].driver", source=True)
            del_name_node.append(filter_node)
            del_name_node.append(driver_node)

        del_name_node = [item for sublist in del_name_node for item in sublist]

        for node_name in del_name_node:
            try:
                if node_name not in nodes_to_keep:
                    cmds.delete(node_name)
            except:
                pass

# 全局aov新创建的选项信息
new_rendering_preset_name = {}

# 渲染预设设置按钮
class rendering_preset_settings_button():

    def __init__(self,menu_name):

        self.import_val = None

        self.lang = language_loading()['ArnoldMagicNode']['RenderPSB']

        self.import_name_win(menu_name)

        self.feedback = FeedbackPrompt() # 错误提示模块
        self.dataM = DataManager() # 数据管理模块



    # 获取默认渲染节点设置
    def get_default_rendering_properties(self):

        defaultRenderGlobals_options = ["animation", "animationRange", "applyFogInPost", "binMembership",
                                        "bitDepth", "blur2DMemoryCap", "blurLength", "blurSharpness", "bottomRegion",
                                        "bufferName", "byFrameStep", "caching", "clipFinalShadedColor",
                                        "colorProfileEnabled", "comFrrt", "composite", "compositeThreshold",
                                        "createIprFile", "currentRenderer", "defaultTraversalSet", "enableDefaultLight",
                                        "enableDepthMaps", "enableStrokeRender", "evenFieldExt", "exrCompression",
                                        "exrPixelType", "extensionPadding", "fieldExtControl", "fogGeometry",
                                        "forceTileSize", "frozen", "gammaCorrection", "geometryVector", "hyperShadeBinList",
                                        "ignoreFilmGate", "imageFilePrefix", "imageFormat", "imfPluginKey",
                                        "inputColorProfile", "interruptFrequency", "iprRenderMotionBlur", "iprRenderShading",
                                        "iprRenderShadowMaps", "iprShadowPass", "isHistoricallyInteresting",
                                        "jitterFinalColor", "keepMotionVector", "leafPrimitives", "leftRegion",
                                        "logRenderPerformance", "macCodec", "macDepth", "macQual",
                                        "matteOpacityUsesTransparency", "maximumMemory", "message", "motionBlur",
                                        "motionBlurByFrame", "motionBlurShutterClose", "motionBlurShutterOpen",
                                        "motionBlurType", "motionBlurUseShutter", "multiCamNamingMode", "nodeState",
                                        "numCpusToUse", "oddFieldExt", "onlyRenderStrokes", "optimizeInstances",
                                        "outFormatControl", "outFormatExt", "outputColorProfile", "oversamplePaintEffects",
                                        "oversamplePfxPostFilter", "periodInExt", "postFogBlur", "postFurRenderMel",
                                        "postMel", "postRenderLayerMel", "postRenderMel", "preFurRenderMel", "preMel",
                                        "preRenderLayerMel", "preRenderMel", "putFrameBeforeExt", "quality", "raysSeeBackground",
                                        "recursionDepth", "renderAll", "renderLayerEnable", "renderVersion", "rendercallback",
                                        "renderedOutput", "renderingColorProfile", "resolution", "reuseTessellations",
                                        "rightRegion", "shadingVector", "shadowPass", "shadowsObeyLightLinking",
                                        "shadowsObeyShadowLinking", "skipExistingFrames", "smoothColor", "smoothValue",
                                        "strokesDepthFile", "subdivisionHashSize", "subdivisionPower", "swatchCamera",
                                        "tiffCompression", "tileHeight", "tileWidth", "topRegion", "useBlur2DMemoryCap",
                                        "useDisplacementBoundingBox", "useFileCache", "useFrameExt", "useMayaFileName",
                                        "useRenderRegion"]
        defaultRenderQuality_options = ["binMembership", "blueThreshold", "caching", "coverageThreshold",
                                        "edgeAntiAliasing", "enableRaytracing", "frozen", "greenThreshold",
                                        "isHistoricallyInteresting", "maxShadingSamples", "maxVisibilitySamples",
                                        "message", "nodeState", "particleSamples", "pixelFilterType", "pixelFilterWidthX",
                                        "pixelFilterWidthY", "plugInFilterWeight", "rayTraceBias", "redThreshold",
                                        "reflections", "refractions", "renderSample", "shadingSamples", "shadows",
                                        "useMultiPixelFilter", "visibilitySamples", "volumeSamples"]
        defaultResolution_options =  ["aspectLock", "binMembership", "caching", "deviceAspectRatio",
                                      "dotsPerInch", "fields", "frozen", "height", "imageSizeUnits",
                                      "isHistoricallyInteresting", "lockDeviceAspectRatio", "message",
                                      "nodeState", "oddFieldFirst", "pixelAspect", "pixelDensityUnits", "width",
                                      "zerothScanline"]

        default_render_options_attribute = {
            'defaultRenderGlobals' : {},
            'defaultRenderQuality' : {},
            'defaultResolution' : {}
        }

        # 获取defaultRenderGlobals的属性
        for i in defaultRenderGlobals_options:
            try:
                default_render_options_attribute['defaultRenderGlobals'][i] = cmds.getAttr("defaultRenderGlobals."+ i)
            except:
                # None值将不会写入到渲染器里
                default_render_options_attribute['defaultRenderGlobals'][i] = None

        # 获取defaultRenderQuality的属性
        for i in defaultRenderQuality_options:
            try:
                default_render_options_attribute['defaultRenderQuality'][i] = cmds.getAttr("defaultRenderQuality."+ i)
            except:
                # None值将不会写入到渲染器里
                default_render_options_attribute['defaultRenderQuality'][i] = None

        # 获取defaultResolution的属性
        for i in defaultResolution_options:
            try:
                default_render_options_attribute['defaultResolution'][i] = cmds.getAttr("defaultResolution."+ i)
            except:
                # None值将不会写入到渲染器里
                default_render_options_attribute['defaultResolution'][i] = None


        return default_render_options_attribute

    # 获取阿诺德渲染设置
    def get_rendering_properties(self):
        defaultArnoldDriver = ["aiTranslator", "aiUserOptions", "alphaHalfPrecision", "alphaTolerance", "append",
                               "autocrop", "binMembership", "caching", "colorManagement", "deepexrTiled",
                               "depthHalfPrecision", "depthTolerance", "dither", "exrCompression", "exrTiled",
                               "frozen", "halfPrecision", "input", "isHistoricallyInteresting", "mergeAOVs",
                               "message", "multipart", "nodeState", "outputMode", "outputPadded", "pngFormat",
                               "pngSkipAlpha", "pngUnpremultAlpha", "prefix", "preserveLayerName", "quality",
                               "renderSession", "skipAlpha", "subpixelMerge", "tiffCompression", "tiffFormat",
                               "tiffTiled", "unpremultAlpha", "useRGBOpacity"]

        defaultArnoldFilter = ["aiFilterWeights", "aiTranslator", "aiUserOptions", "aiWidth", "binMembership", "caching",
                               "domain", "filterWeights", "frozen", "isHistoricallyInteresting", "maximum", "message",
                               "minimum", "nodeState", "scalarMode", "width"]

        defaultArnoldRenderOptions = ["AAAdaptiveThreshold", "AASampleClamp", "AASamples", "AASamplesMax", "AA_seed",
                                      "GIDiffuseDepth", "GIDiffuseSamples", "GISpecularDepth", "GISpecularSamples",
                                      "GISssSamples", "GITotalDepth", "GITransmissionDepth", "GITransmissionSamples",
                                      "GIVolumeDepth", "GIVolumeSamples", "GI_glossy_samples", "GI_refraction_samples",
                                      "IPRRefinementFinished", "IPRRefinementStarted", "IPRStepFinished", "IPRStepStarted",
                                      "PostTranslation", "abortOnError", "abortOnLicenseFail", "absoluteProceduralPaths",
                                      "absoluteTexturePaths", "aiUserOptions", "aovMode", "atmosphere",
                                      "autoTransparencyDepth", "autotile", "autotx", "avpRegionBottom", "avpRegionLeft",
                                      "avpRegionRight", "avpRegionTop", "background", "binMembership", "binaryAss",
                                      "bucketScanning", "bucketSize", "caching", "clear_before_render", "denoiseBeauty",
                                      "dielectricPriorities", "displayAOV", "driver", "enableAdaptiveSampling",
                                      "enableProgressiveRender", "enable_swatch_render", "errorColorBadPixel",
                                      "errorColorBadPixelB", "errorColorBadPixelG", "errorColorBadPixelR",
                                      "errorColorBadTexture", "errorColorBadTextureB", "errorColorBadTextureG",
                                      "errorColorBadTextureR", "expandProcedurals", "exportAllShadingGroups",
                                      "exportDagName", "exportFullPaths", "exportMayaUsd", "exportNamespace",
                                      "exportPrefix", "exportSeparator", "exportShadingEngine", "filter",
                                      "filterType", "forceTranslateShadingEngines", "force_scene_update_before_IPR_refresh",
                                      "force_texture_cache_flush_after_render", "frozen", "globalLightSamplesEnabled",
                                      "gpuDefaultMinMemoryMB", "gpuDefaultNames", "gpu_max_texture_resolution",
                                      "ignoreAtmosphere", "ignoreBump", "ignoreDisplacement", "ignoreDof", "ignoreImagers",
                                      "ignoreLights", "ignoreMotion", "ignoreMotionBlur", "ignoreOperators", "ignoreShaders",
                                      "ignoreShadows", "ignoreSmoothing", "ignoreSss", "ignoreSubdivision", "ignoreTextures",
                                      "ignore_list", "imageFormat", "indirectSampleClamp", "indirectSpecularBlur",
                                      "isHistoricallyInteresting", "kickRenderFlags", "lightLinking", "lightSamples",
                                      "lock_sampling_noise", "log_filename", "log_max_warnings", "log_to_console",
                                      "log_to_file", "log_verbosity", "lowLightThreshold", "manual_gpu_devices",
                                      "maxSubdivisions", "mb_camera_enable", "mb_lights_enable", "mb_object_deform_enable",
                                      "mb_objects_enable", "mb_shader_enable", "message", "motion_blur_enable", "motion_end",
                                      "motion_frames", "motion_start", "motion_steps", "mtoa_translation_info", "nodeState",
                                      "offsetOrigin", "operator", "origin", "outputAssBoundingBox", "outputOverscan",
                                      "outputVarianceAOVs", "output_ass_compressed", "output_ass_filename", "output_ass_mask",
                                      "plugin_searchpath", "plugins_path", "preserve_scene_data", "procedural_searchpath",
                                      "profile_enable", "profile_file", "progressive_initial_level", "progressive_rendering",
                                      "range_type", "referenceTime", "regionMaxX", "regionMaxY", "regionMinX", "regionMinY",
                                      "renderDevice", "renderGlobals", "renderType", "renderUnit", "render_device_fallback",
                                      "sceneScale", "shadowLinking", "skipLicenseCheck", "sssUseAutobump", "standinDrawOverride",
                                      "stats_enable", "stats_file", "stats_mode", "subdivDicingCamera", "subdivFrustumCulling",
                                      "subdivFrustumPadding", "textureAcceptUnmipped", "textureAcceptUntiled", "textureAutoTxPath",
                                      "textureAutotile", "textureConservativeLookups", "textureDiffuseBlur", "textureMaxMemoryMB",
                                      "textureMaxOpenFiles", "textureSpecularBlur", "texture_searchpath", "threads", "threads_autodetect",
                                      "use_existing_tiled_textures", "use_sample_clamp", "use_sample_clamp_AOVs", "version"]

        arnold_render_options_attribute = {
            'defaultArnoldDriver' : {},
            'defaultArnoldFilter' : {},
            'defaultArnoldRenderOptions' : {}
        }

        render_options_attribute = {}

        # 获取defaultArnoldDriver的属性
        for i in defaultArnoldDriver:
            try:
                arnold_render_options_attribute['defaultArnoldDriver'][i] = cmds.getAttr("defaultArnoldDriver."+ i)
            except:
                # None值将不会写入到渲染器里
                arnold_render_options_attribute['defaultArnoldDriver'][i] = None

        # 获取defaultArnoldFilter的属性
        for i in defaultArnoldFilter:
            try:
                arnold_render_options_attribute['defaultArnoldFilter'][i] = cmds.getAttr("defaultArnoldFilter."+ i)
            except:
                # None值将不会写入到渲染器里
                arnold_render_options_attribute['defaultArnoldFilter'][i] = None

        # 获取defaultArnoldRenderOptions的属性
        for i in defaultArnoldRenderOptions:
            try:
                arnold_render_options_attribute['defaultArnoldRenderOptions'][i] = cmds.getAttr("defaultArnoldRenderOptions."+ i)
            except:
                # None值将不会写入到渲染器里
                arnold_render_options_attribute['defaultArnoldRenderOptions'][i] = None

        return arnold_render_options_attribute

    # 获取AOV设置
    def get_AOV_properties(self):
        aiAOV_att_list =  ["binMembership", "caching", "camera", "defaultValue", "denoise", "enabled", "filterType",
                           "frozen", "globalAov", "imageFormat", "isHistoricallyInteresting", "lightGroups",
                           "lightGroupsList", "lightPathExpression", "message", "name", "nodeState", "prefix", "type"]
        # 这是aiAOV中的所有属性
        aiDriver_att_list = ["aiTranslator", "aiUserOptions", "alphaHalfPrecision", "alphaTolerance", "append",
                             "autocrop", "binMembership", "caching", "colorManagement", "deepexrTiled",
                             "depthHalfPrecision", "depthTolerance", "dither", "exrCompression", "exrTiled", "frozen",
                             "halfPrecision", "input", "isHistoricallyInteresting", "mergeAOVs", "message", "multipart",
                             "nodeState", "outputMode", "outputPadded", "pngFormat", "pngSkipAlpha", "pngUnpremultAlpha",
                             "prefix", "preserveLayerName", "quality", "renderSession", "skipAlpha", "subpixelMerge",
                             "tiffCompression", "tiffFormat", "tiffTiled", "unpremultAlpha", "useRGBOpacity"]

        aiFilter_att_list = ["aiFilterWeights", "aiTranslator", "aiUserOptions", "aiWidth", "binMembership", "caching",
                             "domain", "filterWeights", "frozen", "isHistoricallyInteresting", "maximum", "message",
                             "minimum", "nodeState", "scalarMode", "width"]

        if cmds.objExists("defaultArnoldRenderOptions") == False:
            self.feedback.CPW("没检测到阿诺德渲染器节点，无法写入阿诺德的内容请切换渲染器先")
            return None

        aiAov_name_list = cmds.listConnections("defaultArnoldRenderOptions.aovList", source=True)
        # 这是所有aiAOV的名字

        if aiAov_name_list == None:
            self.feedback.CP(f'还没有设置AOV哦～将不会写入AOV')
            return None

        aov_info_dict = {}
        # 这个是数据结构的列表

        for AOV_name in aiAov_name_list:
            # 0，前期获取一些参数
            driver_and_filter_name = self.get_driver_and_filter_nodes(AOV_name)


            # 1，创建对应空的列表---
            aov_info_dict[AOV_name] = []

            # 2，写入节点名字属性---
            aov_info_dict[AOV_name].append({"aov_name":AOV_name})

            # 3, 写入节点属性---
            aov_info_dict[AOV_name].append({"aov_attributes":{}})
            for attribute in aiAOV_att_list:
                try:
                    att_value = cmds.getAttr("{}.{}".format(AOV_name, attribute)) # 获取节点属性
                    aov_info_dict[AOV_name][1]['aov_attributes'][attribute] = att_value # 写入属性列表
                except:
                    aov_info_dict[AOV_name][1]['aov_attributes'][attribute] = None

            # 4，创建driver列表---
            aov_info_dict[AOV_name].append({"driver":{}})

            # 5，写入driver节点名字---
            aov_info_dict[AOV_name][2]['driver']["driver_name"] = driver_and_filter_name[0]

            # 5，写入driver节点属性---
            aov_info_dict[AOV_name][2]['driver']["driver_attribute"] = {}
            for attribute in aiDriver_att_list:
                try:
                    att_value = cmds.getAttr("{}.{}".format(driver_and_filter_name[0], attribute)) # 获取节点属性
                    aov_info_dict[AOV_name][2]['driver']["driver_attribute"][attribute] = att_value
                except:
                    aov_info_dict[AOV_name][2]['driver']["driver_attribute"][attribute] = None

            # 6，创建filter列表---
            aov_info_dict[AOV_name].append({"filter":{}})

            # 7，写入filter节点名字---
            aov_info_dict[AOV_name][3]['filter']["filter_name"] = driver_and_filter_name[1]

            # 8，写入filter节点属性---
            aov_info_dict[AOV_name][3]['filter']["filter_attribute"] = {}
            for attribute in aiFilter_att_list:
                try:
                    att_value = cmds.getAttr("{}.{}".format(driver_and_filter_name[1], attribute)) # 获取节点属性
                    aov_info_dict[AOV_name][3]['filter']["filter_attribute"][attribute] = att_value
                except:
                    aov_info_dict[AOV_name][3]['filter']["filter_attribute"][attribute] = None


        return aov_info_dict

    # 获取driver_and_filter的名字
    def get_driver_and_filter_nodes(self,node_name):

        """
        获取指定节点的 driver 和 filter 节点名称列表。

        Args:
            node_name (str): 要查询的节点名称。

        Returns:
            tuple: 包含两个列表的元组，第一个列表包含所有的 driver 节点名称，第二个列表包含所有的 filter 节点名称。

        Raises:
            None

        Example:
            node_name = 'aiAOV_albedo'
            driver_nodes, filter_nodes = get_driver_and_filter_nodes(node_name)
        """

        driver_node_name = None
        filter_node_name = None

        # 检查节点是否存在
        if not cmds.objExists(node_name):
            self.feedback.CP("节点 {} 不存在".format(node_name))
            return None, None

        # 获取节点的输出连接
        output_connections = cmds.listConnections(node_name + '.outputs', source=True, destination=False)

        # 遍历输出连接，找到 driver 和 filter 节点
        for connection in output_connections:
            # 检查连接的节点类型是否为 driver
            if cmds.nodeType(connection) == 'aiAOVDriver':
                driver_node_name = connection
            # 检查连接的节点类型是否为 filter
            elif cmds.nodeType(connection) == 'aiAOVFilter':
                filter_node_name = connection

        return driver_node_name, filter_node_name

    # _______________________________________________________________________>>> 导入名称窗口函数
    def import_name_win(self, menu_name):
        """
        创建一个窗口用于输入预设名称，并将其添加到指定的菜单中。
        """
        WIN_NAME = "import_name_win"
        # 检查窗口是否存在，如果存在则删除
        if cmds.window(WIN_NAME, exists=True):
            cmds.deleteUI(WIN_NAME)

        # 创建窗口
        cmds.window(WIN_NAME, title =self.lang['import_name_win']['01'], sizeable=False, mbr=True, tlb=False, w=300, h=40) # 输入你的预设名字

        # 创建布局
        layout = cmds.rowLayout(numberOfColumns=50)

        # 创建输入控件
        cmds.text(label=" " * 2)
        text_field = cmds.textField(w=300)

        # 创建按钮布局
        cmds.text(label=" " * 3)
        cmds.button(label=self.lang['import_name_win']['02'], c=lambda *args: determine()) # 确定
        cmds.text(label=" | ")
        cmds.button(label=self.lang['import_name_win']['03'], c=lambda *args: cancellation()) # 取消
        cmds.text(label=" " * 3)

        # 设置父级布局
        cmds.setParent(layout)

        # 显示窗口
        cmds.showWindow(WIN_NAME)

        # _______________________________________________________________________>>> 确认输入的操作函数
        def determine():
            """
            确定按钮的回调函数，保存输入的预设名称和渲染设置。
            """
            global new_rendering_preset_name

            # 01, 获取用户输入的预设名称
            self.import_val = cmds.textField(text_field, query=True, text=True)
            # 获取渲染设置数据
            default_rendering_properties = self.get_default_rendering_properties()
            rendering_properties = self.get_rendering_properties()
            AOV_properties = self.get_AOV_properties()

            # 定义写入数据的路径
            write_data_path = os.path.normpath(os.path.join(datas_path, 'render_presets'))

            # 02, 组织渲染器属性数据
            Render_settings = {
                'default_rendering_properties': default_rendering_properties,
                'rendering_properties': rendering_properties,
                'AOV_properties': AOV_properties
            }

            # 03, 将渲染器属性保存到 JSON 文件中
            if not os.path.exists(os.path.join(write_data_path, self.import_val + ".json")):
                self.dataM.save_json(os.path.join(write_data_path, self.import_val + ".json"), Render_settings)



            # 04, 将新项目添加到菜单中
            edit_menu = menu_name  # 获取菜单的名字或 ID
            existing_items = cmds.menu(edit_menu, query=True, itemArray=True)  # 获取菜单中已有项目

            # 确定新项目插入的位置
            insert_after_item = existing_items[0] if existing_items else None

            # 添加新的菜单项，有效性检查
            if insert_after_item and cmds.menuItem(insert_after_item, exists=True):
                # 插入到指定位置
                new_rendering_preset_name[self.import_val] = cmds.menuItem(
                    self.import_val,
                    parent=edit_menu,
                    insertAfter=insert_after_item,
                    label=self.import_val,
                )
            else:
                # 直接添加到菜单末尾
                new_rendering_preset_name[self.import_val] = cmds.menuItem(
                    self.import_val,
                    parent=edit_menu,
                    label=self.import_val,
                )

            # 如果无法选择就算了，可以选择就选择第二项
            try:
                cmds.optionMenu(edit_menu, edit=True, select=2)
            except:
                pass
            # 关闭窗口
            cmds.deleteUI(WIN_NAME)
            return

        # _______________________________________________________________________>>> 取消操作函数
        def cancellation():
            """
            取消按钮的回调函数，关闭窗口。
            """
            cmds.deleteUI(WIN_NAME)
            return

# 删除渲染预设设置
def delete_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name):
    global new_rendering_preset_name

    for i in rendering_preset_name:
        if sl_name == i:
            cmds.deleteUI(rendering_preset_name[i], menuItem=True)

    for i in new_rendering_preset_name:
        if sl_name == i:
            cmds.deleteUI(new_rendering_preset_name[i], menuItem=True)

    # 2, 删除本地文件
    os.remove(os.path.normpath(os.path.join(
                render_preset_path,  sl_name+ '.json'
            )))

# 修改渲染预设设置
def modify_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name, menu_name):
    rendering_preset_settings_button(menu_name)
    delete_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name)

# 开关AOV函数
def ai_aov_switch_button():

    feedback = FeedbackPrompt()  # 错误提示模块

    # 获取连接到 AovList 端口的所有节点
    if cmds.objExists("defaultArnoldRenderOptions.aovList"):
        connections = cmds.listConnections("defaultArnoldRenderOptions.aovList", source=True)
    else:
        return feedback.CPW("未创建AOV")

    if connections is None:
        return feedback.CPW("未创建AOV")

    for aov in connections:
        # 获取当前属性状态
        enabled = cmds.getAttr(aov + ".enabled")

        # 如果 enabled 属性为 1，则将其设置为 0
        if enabled == 1:
            cmds.setAttr(aov + ".enabled", 0)

        # 否则，将 enabled 属性设置为 1
        else:
            cmds.setAttr(aov + ".enabled", 1)

# 场景名称优化函数
class Scene_Name_optimization:
    def __init__(self):
        pass

    @staticmethod
    def node_rename(old_name, new_name):
        renamed_node = cmds.rename(old_name, new_name)
        return renamed_node

# 路径连接
class Path_Detection_Connection:
    def __init__(self):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor() # 节点处理模块
        ### 初始化配置数据
        # 加载数据
        self.config = self.dataM.load_json(
            os.path.join(settings_path, AMS_Config))


        self.texture_processing_data = self.dataM.load_json(
            os.path.join(settings_path, AMS_Config))

        self.path_detection_data = self.config['path_detection_params']

        self.texture_filter_dict = self.config["texture_filter_params"]  # 过滤贴图的数据

        self.select_node_data = process_sl_data()  # 调用函数获取处理后的节点数据

        self.lang = language_loading()['ArnoldMagicNode']['PDC']

    def main(self):

        # 如果没有返回有效的数据，直接退出
        if self.select_node_data is None:
            return

        # 检查数据中是否包含 'file' 键
        if 'file' not in self.select_node_data:
            return self.feedback.CPW(self.lang['main']['01'])# 请选择贴图节点哦

        modifiers = cmds.getModifiers()
        matching_completed_dict = self.detect_and_calculate_similarity()

        # alt 只会创建贴图
        if (
            is_modifier_pressed(MAYA_ALT_MODIFIER, modifiers)
            or is_modifier_pressed(MAYA_SHIFT_MODIFIER, modifiers)
        ):

            need_connect_node_lists = self.create_nodes_from_list(matching_completed_dict)

            # 判断是否要修改颜色空间
            if self.config['path_detection_params']['set_color_space']:
                for need_connect_node_list in need_connect_node_lists:
                    self.nodeP.AutoSetTexColorSpace(
                        auto_set_color_space_config=self.config['color_space_params']['params'],
                        node_list=need_connect_node_list,
                        filter_data=self.texture_filter_dict)

            # ——————————————————————————————————————————————————————————————————————————> 自动udim
            self.auto_set_file_udim(need_connect_node_lists)

            # shift 会创建材质并连接
            if is_modifier_pressed(MAYA_SHIFT_MODIFIER, modifiers):
                for need_connect_node_list in need_connect_node_lists:

                    # 判断是否要修改材质的名称
                    if self.config['path_detection_params']['set_material_name']:

                        # 材质球名称会用列表的第一个索引的名称
                        file_name = need_connect_node_list[0]

                        processing_mat_name = self.nodeP.clean_material_name(file_name, self.texture_filter_dict)

                        new_mat_name = cmds.shadingNode('aiStandardSurface', asShader=True, name=processing_mat_name)
                    else:
                        new_mat_name = cmds.shadingNode('aiStandardSurface', asShader=True)

                    matching_dict = self.nodeP.AutoNodeConnect(need_connect_node_list,
                                               new_mat_name,
                                               self.texture_filter_dict, # 过滤贴图的数据
                                               self.config['proc_node_config']['params'], # 相应贴图节点的参数
                                               self.config['magic_conn_config']['conn_params'], # 相应贴图是否要连接的参数
                                               self.config['proc_node_config']['conn_params']) # 相应贴图是否要连接相应的节点

                    # 判断是否要修改颜色空间
                    if self.config['path_detection_params']['set_color_space']:
                        self.nodeP.AutoSetTexColorSpace(
                            auto_set_color_space_config= self.config['color_space_params']['params'],
                            matching_channel= matching_dict)

                    # ——————————————————————————————————————————————————————————————————————————> 自动udim 以为这里是创建材质球的，只需有一层列表
                    self.nodeP.auto_set_udim([key for key in matching_dict.keys()])

    def detect_and_calculate_similarity(self):
        # 用来储存匹配完成的数据字典
        matching_completed_dict = {}

        for node_name in self.select_node_data['file']:
            # 1.获取节点路径
            target_object, target_dirname = self.pathD.get_node_path(node_name)

            # 2.寻找子路径下的文件并排除不需要参加匹配的格式
            dir_name_path = self.pathD.detection_path_content(
                target_dirname = target_dirname,
                exclude_list = self.config['path_detection_params']['exclude'],
                exclude_formats = self.config['path_detection_params']['exclude_formats'])

            # 3.获取文件的元属性
            dir_tex_info = self.pathD.get_file_info(dir_name_path)
            target_object_info = self.pathD.get_file_info(target_object)

            # 4.处理匹配名称
            processed_dir_tex_info = self.pathD.process_dict_key_name(dir_tex_info,
                                                                 self.config['path_detection_params']['detection_excluded'],
                                                                 self.texture_filter_dict)

            processed_target_object_info = self.pathD.process_dict_key_name(target_object_info,
                                                                       self.config['path_detection_params']['detection_excluded'],
                                                                       self.texture_filter_dict)


            # 删除原本选择的
            original_name = list(target_object.keys())[0]  # 获取原始名称
            del processed_dir_tex_info[original_name]

            similarity_dict = self.pathD.calculate_similarity(processed_target_object_info,
                                                         processed_dir_tex_info,
                                                         self.path_detection_data,
                                                         self.config['path_detection_params']['creation_day_range_tolerance'])


            # 判断数据匹配数据
            auto_max_val = self.config['path_detection_params']['auto_max_val']
            similarity_max = self.config['path_detection_params']['similarity_max']
            similarity_range = self.config['path_detection_params']['similarity_range']
            matching_list = self.pathD.determine_connection(similarity_dict, auto_max_val, similarity_max, similarity_range)

            if not self.config['path_detection_params']['disable_feedback']:
                # 发出反馈提醒
                self.feedback_prompt(similarity_dict, matching_list, original_name)

            # 储存匹配好的数据
            matching_completed_dict[node_name] = [matching_list, target_dirname]

        return matching_completed_dict

    def feedback_prompt(self, similarity_dict, matching_list, original_name):
        self.feedback.CP(self.lang['feedback_prompt']['01']) #===================================匹配相似度=================================
        for tex_name, similarity in similarity_dict.items():
            formatted_similarity = "{:.5f}".format(similarity)
            self.feedback.CP(f"{self.lang['feedback_prompt']['02']} {original_name},{self.lang['feedback_prompt']['03']}{tex_name},{self.lang['feedback_prompt']['04']}{formatted_similarity}") # 匹配源 匹配目标 # 相似度

        self.feedback.CP(self.lang['feedback_prompt']['05']) # ===================================完成匹配列表================================="
        self.feedback.CP(f"{self.lang['feedback_prompt']['06']}{original_name}") # 匹配的对象
        for target, similarity in matching_list:
            formatted_similarity = "{:.5f}".format(similarity)
            self.feedback.CP(f"{self.lang['feedback_prompt']['07']} {target},{self.lang['feedback_prompt']['08']}{formatted_similarity}") # 完成匹配 # 相似度

    def remove_original_uv(self, node_name):
        originalUvName = cmds.listConnections(node_name, source=True, destination=False)[-1]
        if originalUvName and originalUvName != 'defaultColorMgtGlobals':
            cmds.delete(originalUvName)

    def create_nodes_from_list(self, matching_completed_dict):
        need_connect_node_lists = []

        for node_name, val in matching_completed_dict.items():

            tex_name_list = []
            path = val[1]

            # 获取匹配完的字典中的数据
            for tex_name in val[0]:
                tex_name_list.append(tex_name[0])

            # 创建对应的节点
            new_create_node_list = self.pathD.create_node(tex_name_list, path)

            # 把创建好的节点名称储存下来
            new_create_node_list.append(node_name)
            need_connect_node_lists.append(new_create_node_list)

            # 删除原始uv系欸但
            self.remove_original_uv(node_name)

        # 把uv节点统一起来
        for node_list in need_connect_node_lists:
            self.nodeP.unify_uv_node(node_list)

        return need_connect_node_lists

    def auto_set_file_udim(self, node_lists):
        if self.config['path_detection_params']['set_udim']:
            for node_list in node_lists:
                self.nodeP.auto_set_udim(node_list)
        else:
            return

# 魔法连接
class Magic_Node_Connection:
    def __init__(self):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor()

        ### 初始化配置数据
        # 加载数据
        self.config = self.dataM.load_json(
            os.path.join(settings_path, AMS_Config))

        self.texture_filter_dict = self.config[
            "texture_filter_params"]  # 过滤贴图的数据
        self.processing_node_data = self.config[
            'proc_node_config'][
            'params']  # 相应贴图节点的参数
        self.magic_connection_options = self.config[
            'magic_conn_config'][
            'conn_params']  # 相应贴图是否要连接的参数
        self.auto_node_connection_options = self.config[
            'proc_node_config'][
            'conn_params']  # 相应贴图是否要连接相应的节点

        # 获取选择节点
        self.select_node = process_sl_data()

    def main(self):

        # 如果没有选择节点将会直接退出函数
        if self.select_node is None:
            return

        self.magic_processing_node_connection()

    # 魔法连接处理节点
    def magic_processing_node_connection(self):
        # 检查SlNode字典中是否有file key 如果没有直接退出函数
        if 'file' not in self.select_node:
            return self.feedback.CPW('没有选择纹理节点，请选择纹理节点')

        mat_name = self.detect_and_create_materials()

        # 如果选择了着色节点会连接上
        if 'shadingEngine' in self.select_node:
            shadingEngine = self.select_node['shadingEngine'][0]
        else:
            shadingEngine = None

        self.matching_dict = self.nodeP.AutoNodeConnect(self.select_node['file'],
                                                        mat_name,
                                                        self.texture_filter_dict,
                                                        self.processing_node_data,
                                                        self.magic_connection_options,
                                                        self.auto_node_connection_options,
                                                        shadingEngine)
        # 自动UDIM
        self.auto_set_file_udim()

        # 自动色彩空间
        self.modify_color_space()

        # 如果材质变量是None的话就不需要处理
        if mat_name is None:
            return

        new_mat_name = self.modify_mat_name(original_mat_name=mat_name, file_name=self.select_node['file'][0])

        self.feedback.CP('已完成 {} 材质连接'.format(new_mat_name))

    # 检测并创建材质
    def detect_and_create_materials(self):
        mat_types = ['aiStandardSurface', 'standardSurface', 'aiOpenPBRSurface']
        mat_name = None

        # 检测有没有选择材质球
        for mat_type in mat_types:
            if mat_type in self.select_node:
                mat_name = self.select_node[mat_type][0]
                break  # 找到匹配的材质类型后就退出循环
        else:
            if is_modifier_pressed(MAYA_SHIFT_MODIFIER):
                mat_name = cmds.shadingNode('aiStandardSurface', asShader=True)

        return mat_name

    # 修改材质名称
    def modify_mat_name(self,original_mat_name,  file_name):

        texture_processing_data = self.dataM.load_json(
            os.path.join(settings_path, AMS_Config))

        # 修改材质名称
        if self.config['magic_conn_config']['set_material_name']:
            new_mat_name = self.nodeP.clean_material_name(file_name, self.texture_filter_dict)
        else:
            return original_mat_name

        # 修改材质节点名称
        cmds.rename(original_mat_name, new_mat_name)

        self.feedback.CP('已将 {} 材质名称修改成 {}'.format(original_mat_name, new_mat_name))

        return new_mat_name

    # 修改颜色空间
    def modify_color_space(self):
        if self.config['magic_conn_config']['set_color_space']:
            self.nodeP.AutoSetTexColorSpace(
                auto_set_color_space_config = self.config['color_space_params']['params'],
                matching_channel = self.matching_dict)
        else:
            return

    # 自动udim
    def auto_set_file_udim(self):

        if self.config['magic_conn_config']['set_udim']:
            node_list = [key for key in self.matching_dict.keys()]
            self.nodeP.auto_set_udim(node_list)
        else:
            return

# 转换旧材质到阿诺德
class ConvertOldMaterialsToArnold:
    def __init__(self, select_all = None):
        config_path  = os.path.join(script_path, 'config', 'shader_convert_map.json')

        with open(config_path, 'r') as f:
            self.convert_info = json.load(f)

        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor() # 节点处理模块


        self.materials_node = self.get_materials_node(select_all)

    def get_materials_node(self, select_all=None):
        """
        获取场景中指定类型的材质名列表，排除默认材质 “lambert1”。
        如果没找到任何匹配材质，则返回空字典 {}。
        """
        wanted_types = list(self.convert_info.keys())

        # 取得场景材质原始数据；None / {} / [] 都视为“空”
        scene_nodes = get_scene_all_data() if select_all else process_sl_data()
        if not scene_nodes:  # == {}、[] 或 None 都会进入
            return {}

        result = {}

        for mat_type in wanted_types:
            mat_nodes = scene_nodes.get(mat_type, {})

            # 1) mat_nodes 是 dict ⇒ 直接取 key
            if isinstance(mat_nodes, dict):
                names = list(mat_nodes.keys())

            # 2) mat_nodes 是 list
            elif isinstance(mat_nodes, list):
                if mat_nodes and isinstance(mat_nodes[0], dict):
                    names = [d["name"] for d in mat_nodes if "name" in d]
                else:
                    names = mat_nodes[:]

            # 3) 其它类型 ⇒ 跳过
            else:
                continue

            # 过滤掉默认材质 “lambert1”
            names = [n for n in names if n != "lambert1"]

            if names:
                result[mat_type] = names



        return result

    def get_materials_input_data(self, mat_name):
        """
        收集【输入连接】：
        返回一个字典 {目标端口(dstPlug) : 源端口(srcPlug)}
        ──表示“有哪些上游节点驱动了材质 mat_name 的哪些属性”。

        参数
        -------
        mat_name : str
            需要分析的材质节点名称。

        返回
        -------
        dict
            形如 {'aiStd1.baseColor' : 'file1.outColor', ...}
        """
        # listConnections：s=True,d=False ⇒ 只列出 “上游 → mat_name” 的连线
        # c=True,p=True   ⇒ 结果按 [dstPlug, srcPlug, dstPlug, srcPlug, …] 成对返回
        pairs = cmds.listConnections(mat_name,
                                     s=True, d=False,
                                     c=True, p=True) or []

        conn_dict = {}  # {dstPlug_on_mat : srcPlug_upstream}
        for i in range(0, len(pairs), 2):
            dst, src = pairs[i], pairs[i + 1]  # 0=dst(本节点端口) , 1=src(上游端口)
            conn_dict[dst] = src

        return conn_dict

    def get_materials_output_data(self, mat_name):
        """
        收集【输出连接】：
        返回一个字典 {源端口(srcPlug) : 目标端口(dstPlug)}
        ──表示“材质 mat_name 把哪些属性输出到下游节点”。

        参数
        -------
        mat_name : str
            需要分析的材质节点名称。

        返回
        -------
        dict
            形如 {'aiStd1.outColor' : 'aiStd1SG.surfaceShader', ...}
        """
        # listConnections：s=False,d=True ⇒ 只列出 “mat_name → 下游” 的连线
        # c=True,p=True   ⇒ 结果按 [srcPlug, dstPlug, srcPlug, dstPlug, …] 成对返回
        pairs = cmds.listConnections(mat_name,
                                     s=False, d=True,
                                     c=True, p=True) or []

        conn_dict = {}  # {srcPlug_on_mat : dstPlug_downstream}
        for i in range(0, len(pairs), 2):
            src, dst = pairs[i], pairs[i + 1]  # 0=src(本节点端口) , 1=dst(下游端口)
            conn_dict[src] = dst

        return conn_dict

        for i in range(0, len(pairs), 2):
            dst, src = pairs[i], pairs[i + 1]  # 先 dst 后 src
            conn_dict[dst] = src

        return conn_dict

    def process(self):

        # 如果没有返回有效的数据，直接退出
        for mat_type, mat_names in self.materials_node.items():
            for mat_name in mat_names:

                # 检测材质球是否存在
                if not cmds.objExists(mat_name):
                    continue

                # 获取材质的输入数据
                input_data = self.get_materials_input_data(mat_name)
                materials_out_data = self.get_materials_output_data(mat_name)

                # 创建一个新的材质球
                new_mat_name = cmds.shadingNode(
                    self.convert_info[mat_type]['arnold_shader'], asShader=True, name=mat_name + '_ACArnold')

                # 将输入连接复制到新的材质球
                for dst, src in input_data.items():
                    node_name = src.split('.')[0]
                    node_out_port= src.split('.')[1]
                    mat_iunput_port = dst.split('.')[1]

                    # 将旧材质球的输入连接复制到新材质球
                    cmds.connectAttr(f"{node_name}.{node_out_port}", f"{new_mat_name}.{self.convert_info[mat_type]['attribute_map'][mat_iunput_port]}" , force=True)

                for materials_port_info in materials_out_data:
                    output_node_port = materials_port_info.split('.')[1]
                    try:
                        cmds.connectAttr(f"{new_mat_name}.{output_node_port}", f"{materials_out_data[materials_port_info]}", force=True)
                    except Exception as e:
                        self.feedback.CP(f"连接失败: {e}")

                cmds.delete(mat_name)  # 删除旧材质球

# 智能材质修复
class IntelligentMaterialRepair:
    def __init__(self,  select_all=None):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor() # 节点处理模块
        self.GnodeD = GetNodeData() # 获取节点数据模块

        self.materials_node = self.get_materials_node(select_all)

    # 获取材质节点
    def get_materials_node(self, select_all=None):
        node_types = ['aiStandardSurface', 'standardSurface', 'aiLambert',
                                  'aiStandardHair']

        # 取得场景材质原始数据；None / {} / [] 都视为“空”
        scene_nodes = get_scene_all_data() if select_all else process_sl_data()

        # 如果没有任何数据，返回所有类型对应的空列表
        if not scene_nodes:
            return {nt: [] for nt in node_types}

        # 否则，根据 node_types 提取对应的节点列表，缺失的也补空列表
        return {
            nt: scene_nodes.get(nt, [])
            for nt in node_types
        }

    # 计算相似度
    def detect_and_calculate_similarity(self,  node_path):
        """
        - 使用的配置数据是 AMS_Config 中的 path_detection_params，
        因为这样子方便测试
        """
        # 获取配置数据
        config = self.dataM.load_json(os.path.join(
                                                                    settings_path, AMS_Config))['path_detection_params']

        texture_filter_dict = self.dataM.load_json(os.path.join(
                                                                    settings_path, AMS_Config))['texture_filter_params']



        file_path_dir = os.path.dirname(node_path)
        file_name = os.path.basename(node_path)

        # 2.寻找子路径下的文件并排除不需要参加匹配的格式
        dir_name_path = self.pathD.detection_path_content(
            target_dirname = file_path_dir,
            exclude_list = config['exclude'],
            exclude_formats = config['exclude_formats'])

        # 3.获取文件的元属性
        dir_tex_info = self.pathD.get_file_info(dir_name_path)
        target_object_info = self.pathD.get_file_info(
            {(os.path.basename(os.path.normpath(node_path))): node_path})

        # 4.处理匹配名称
        processed_dir_tex_info = self.pathD.process_dict_key_name(dir_tex_info,
                                                                  config['detection_excluded'],
                                                                  texture_filter_dict)

        processed_target_object_info = self.pathD.process_dict_key_name(target_object_info,
                                                                        config['detection_excluded'],
                                                                        texture_filter_dict)

        # 4, 删除原本选择的
        del processed_dir_tex_info[file_name]

        # 5，计算相似度
        similarity_dict = self.pathD.calculate_similarity(processed_target_object_info,
                                                          processed_dir_tex_info,
                                                          config,
                                                          config['creation_day_range_tolerance'])

        # 6，判断数据匹配数据
        matching_list = self.pathD.determine_connection(
            similarity_dict,
            config['auto_max_val'],
            config['similarity_max'],
            config['similarity_range'])


        return matching_list

    # 通过节点创建节点
    def create_nodes_from_list(self, first_node_name  , dir_path, matching_completed_dict):
        # 遍历 matching_completed_dict，提取所有贴图文件名（每个元组的第一个元素）
        for node_name, val in matching_completed_dict.items():
            filenames = [name for name, _ in val]

        # 根据提取出的文件名列表和目录路径，创建对应的贴图节点
        new_create_node_list = self.pathD.create_node(
            tex_name_list=filenames,
            path=dir_path
        )

        # 将第一个节点名称 first_node_name 添加到新创建的节点列表末尾
        new_create_node_list.append(first_node_name)

        # 对新创建的所有节点执行 UV 统一操作，确保它们使用相同的 UV 设置
        self.nodeP.unify_uv_node(new_create_node_list)

        # 返回包含贴图节点和第一个节点名称的完整列表
        return new_create_node_list

    # 主程序
    def process(self):

        sttings_config = self.dataM.load_json(os.path.join(
                                                                    settings_path, AMS_Config))


        # 遍历材质节点
        for mat_type, mat_names in self.materials_node.items():
            for mat_name in mat_names:
                # 0，初始化一些变量
                matching_completed_dict = {}


                # 1，寻找到材质球的贴图路径
                mat_info = self.GnodeD.get_file_texture_paths(mat_name)

                if mat_info == {}:
                    continue
                else:
                    # 提起其中一个
                    node_name, node_path = next(iter(mat_info.items()))

                # 2，检测并且计算相似度
                similarity_data = self.detect_and_calculate_similarity(node_path)

                # 如果匹配数量异常（比如超过10个），则跳过这个节点处理
                if not similarity_data or len(similarity_data) > 9:
                    self.feedback.CPW(
                        f"[{mat_name}] 的贴图 [{node_name}] 匹配结果异常，数量：{len(similarity_data)}，已跳过修复")
                    continue

                # 3 ，合并参数
                matching_completed_dict[node_name] = similarity_data

                # 4，创建节点
                need_connect_node_lists = self.create_nodes_from_list(
                    first_node_name = node_name,
                    dir_path = os.path.normpath(os.path.dirname(node_path)),
                    matching_completed_dict  = matching_completed_dict)

                # 5，修改颜色空间
                if sttings_config['path_detection_params']['set_color_space']:
                    self.nodeP.AutoSetTexColorSpace(
                        auto_set_color_space_config=sttings_config['color_space_params']['params'],
                        node_list=need_connect_node_lists,
                        filter_data=sttings_config['texture_filter_params'])

                # 6，自动UDIM
                if sttings_config['path_detection_params']['set_udim']:
                    self.nodeP.auto_set_udim(need_connect_node_lists)

                # 7，连接上材质球
                self.nodeP.AutoNodeConnect(need_connect_node_lists,
                                           mat_name,
                                           sttings_config['texture_filter_params'],  # 过滤贴图的数据
                                           sttings_config['proc_node_config']['params'],  # 相应贴图节点的参数
                                           sttings_config['magic_conn_config']['conn_params'],  # 相应贴图是否要连接的参数
                                           sttings_config['proc_node_config']['conn_params'])  # 相应贴图是否要连接相应的节点

# 快速连接节点
class QuickConnectNode:
    def __init__(self):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块

        self.config = self.dataM.load_json(os.path.join(settings_path, AMS_Config))['node_connection_mixer_config']['quick_connect_node_parms']

    def get_select_node(self):
        """
        直接按选中顺序返回节点列表，
        避免 process_sl_data() 分组后的乱序问题
        """
        return cmds.ls(selection=True) or []

    def process(self):
        """
        节点逻辑：
        1. 按选中顺序链式连接：nodes[0]→nodes[1]，nodes[1]→nodes[2]...
        2. 优先使用 priority_order 字典去连接；
        3. 如果优先级连接都失败，再遍历 out_port × input_port 列表连接；
        4. 使用 cmds.connectAttr(..., force=True)，并输出提示或 warning。

        思路：
       节点逻辑优先使用有限级组合去尝试连接，然后在尝试使用输出端口
        和输入端口进行连接。如果是直接使用输出和输入端口就是out_port
        和input_port进行连接，机会使用列表的索引优先级进行测试
        """
        # 1. 获取并校验选中节点
        nodes = self.get_select_node()

        if len(nodes) < 2:
            cmds.warning("至少需要两个节点来建立连接！")
            return

        # 2. 链式：第1→第2，第2→第3，依此类推
        for src_node, dest_node in zip(nodes, nodes[1:]):
            connected = False

            # 3. 优先使用 priority_order
            for out_attr, in_attr in self.config['priority_order'].items():
                if not (cmds.attributeQuery(out_attr, node=src_node, exists=True)
                        and cmds.attributeQuery(in_attr, node=dest_node, exists=True)):
                    continue
                try:
                    cmds.connectAttr(f"{src_node}.{out_attr}",
                                     f"{dest_node}.{in_attr}")
                    print(f"[QuickConnect] {src_node}.{out_attr} → {dest_node}.{in_attr}")
                    connected = True
                    break
                except Exception:
                    continue
            if connected:
                continue

            # 4. 备用 out_port × input_port
            for out_attr in self.config['out_port']:
                if connected:
                    break
                for in_attr in self.config['input_port']:
                    if not (cmds.attributeQuery(out_attr, node=src_node, exists=True)
                            and cmds.attributeQuery(in_attr, node=dest_node, exists=True)):
                        continue
                    try:
                        cmds.connectAttr(f"{src_node}.{out_attr}",
                                         f"{dest_node}.{in_attr}")
                        print(f"[QuickConnect] {src_node}.{out_attr} → {dest_node}.{in_attr}")
                        connected = True
                        break
                    except Exception:
                        continue
                if connected:
                    break

            # 5. 若无任何连接，发 warning
            if not connected:
                cmds.warning(f"{src_node} → {dest_node} 未找到可连接属性，已跳过。")

# 混合节点管理器
class BlendNodeManager:
    def __init__(self):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor()  # 节点处理模块

        # 策略映射：模式名称 -> 处理函数
        self._handlers = {
            'intelligent_mix': self.intelligent_mix_process,
            'mask_mix' : self.mask_mix_process,
        }

        # 类型列表
        self.aiUtilityShader = ['file', 'aiBlackbody', 'aiBump2d', 'aiBump3d',
                                             'aiCameraProjection', 'aiClamp', 'aiColorConvert',
                                             'aiColorCorrect', 'aiColorJitter', 'aiComplexIor', 'aiComposite',
                                             'aiDistance', 'aiFacingRatio',  'aiMotionVector','aiNormalMap',
                                            'aiOslShader', 'aiRampFloat', 'aiRampRgb', 'aiRange','aiRoundCorners',
                                            'aiShuffle', 'aiSpaceTransform', 'aiStateFloat', 'aiStateInt','aiStateVector',
                                            'aiTraceSet', 'aiUvProjection', 'aiUvTransform', 'aiVectorMap']

        self.aiMath = ['aiAbs', 'aiAdd', 'aiAtan', 'aiCompare',
                                   'aiComplement', 'aiCross', 'aiDivide', 'aiDot', 'aiExp',
                                   'aiFraction', 'aiIsFinite', 'aiLength', 'aiLog', 'aiMatrixInterpolate',
                                   'aiMatrixMultiplyVector', 'aiMatrixTransform', 'aiMax', 'aiMin',
                                   'aiModulo', 'aiMultiply', 'aiNegate', 'aiNormalize', 'aiPow', 'aiRandom',
                                   'aiReciprocal', 'aiSign', 'aiSqrt', 'aiSubtract', 'aiTrigo']

        self.aiShader  = ['aiStandardSurface', 'standardSurface', 'aiLambert', 'aiStandardHair', 'aiToon']


        self.aiMix = ['aiLayerFloat', 'aiLayerRgba', 'aiLayerShader']

        # 颜色输出端口
        self.color_output_prot = ['outColor', 'outValue']

        # 灰度输出端口
        self.gray_output_prot = ['outColorR',  'outColorG', 'outColorB', 'outAlpha', 'outValueX', 'outValueY', 'outValueZ']


        self.type_to_category = {}
        for category, types in {
            'aiUtilityShader': self.aiUtilityShader,
            'aiMath': self.aiMath,
            'aiShader': self.aiShader,
            'aiMix': self.aiMix,
        }.items():
            for node_type in types:
                self.type_to_category[node_type] = category




    def intelligent_mix_process(self, select_node = None):

        for node_type, node_names in select_node.items():
            category = self.type_to_category.get(node_type)

            if category in ('aiUtilityShader', 'aiMath'):
                self.handle_utility_shader(node_names)
            elif category == 'aiShader':
                self.handle_shader(node_names)
            elif category == 'aiMix':
                self.handle_mix(node_type, node_names)
            else:
                self.feedback.CPW(f'未知的节点类型：{node_type}')


    # 分别定义不同处理方法
    def handle_utility_shader(self, nodes):
        modifiers = cmds.getModifiers()

        if modifiers == 1:  # shift
            self._handle_shader_mix(nodes)
        elif modifiers == 8:  # ctrl
            self._handle_grays_shader_mix(nodes)
        else:
            self._handle_shader_mix(nodes)

    def _handle_shader_mix(self, nodes):
        # 创建节点
        mix_node_name = cmds.createNode('aiLayerRgba', name='shader_mix')
        # 连接节点
        for index, node_name in enumerate(nodes):
            index += 1
            for output_prot in self.color_output_prot:
                try:
                    cmds.connectAttr(f"{node_name}.{output_prot}", f"{mix_node_name}.input{index}", force=True)
                    continue
                except:
                    pass

    def _handle_grays_shader_mix(self, nodes):
        # 创建节点
        mix_node_name = cmds.createNode('aiLayerFloat', name='grays_shader_mix')
        # 连接节点
        for index, node_name in enumerate(nodes):
            index += 1
            for gray_output in self.gray_output_prot:
                print(gray_output)
                try:
                    cmds.connectAttr(f"{node_name}.{gray_output}", f"{mix_node_name}.input{index}", force=True)
                    continue
                except:
                    pass

    def handle_shader(self, nodes):
        # 创建节点
        shader_mix_name = cmds.createNode('aiLayerShader', name='shader_mix')
        # 连接节点
        for index, node_name in enumerate(nodes):
            index += 1
            cmds.connectAttr(f"{node_name}.outColor", f"{shader_mix_name}.input{index}", force=True)

    def handle_mix(self,node_type,  nodes):

        if node_type == 'aiLayerFloat':

            shader_mix_name = self._create_node('aiLayerFloat', 'LayerFloat')

            for index, node_name in enumerate(nodes):
                index += 1
                cmds.connectAttr(f"{node_name}.outValue", f"{shader_mix_name}.input{index}", force=True)

        elif node_type == 'aiLayerRgba':

            shader_mix_name = self._create_node('aiLayerRgba', 'LayerRgba')
            for index, node_name in enumerate(nodes):
                index += 1
                cmds.connectAttr(f"{node_name}.outColor", f"{shader_mix_name}.input{index}", force=True)

        elif node_type == 'aiLayerShader':
            shader_mix_name = self._create_node('aiLayerShader', 'LayerShader')

            for index, node_name in enumerate(nodes):
                index += 1
                cmds.connectAttr(f"{node_name}.outColor", f"{shader_mix_name}.input{index}", force=True)

    def mask_mix_process(self, select_node = None):
        print('mask_mix_process')


    def _create_node(self, node_type, name):
        """
        创建节点
        """
        node_name = cmds.createNode(node_type, name=name)
        return node_name




    def process(self, mix_mod = None):
        # 1，获取选中的节点
        select_nodes = process_sl_data()

        if not select_nodes:
            return self.feedback.CPW('至少需要两个节点来建立连接！')

        # 扁平化成列表
        nodes = []
        for v in select_nodes.values():
            if isinstance(v, (list, tuple, set)):
                nodes.extend(v)
            else:
                nodes.append(v)

        if len(nodes) < 2:
            return self.feedback.CPW('至少需要两个节点来建立连接！')

        # 2. 根据 mix_mod 调用对应处理器
        handler = self._handlers.get(mix_mod)
        if handler:
            handler(select_nodes)
        else:
            self.feedback.CPW(f'未知的混合模式：{mix_mod}')

# 场景名称优化
class SceneNameOptimization:
    def __init__(self):
        self.dataM = DataManager() # 数据管理模块
        self.feedback = FeedbackPrompt() # 错误提示模块
        self.pathD = PathDetection() # 数据检测模块
        self.nodeP = NodeProcessor() # 节点处理模块

        self.scene_nodes = get_scene_all_data()

        self.config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config)))

    # ______________________________________________________________________________>>> 主函数入口
    def main(self):
        # 从配置中获取节点名称替换参数
        config = self.config['optimized_scene_node_name']['replace_param']

        # 遍历场景节点的所有类型
        for node_type in self.scene_nodes:
            # 遍历当前类型下的所有节点名称
            for node_name in self.scene_nodes[node_type]:
                # 如果节点名称包含'|'，则按'|'拆分为多个部分，否则直接使用节点名称
                node_names_to_process = node_name.split('|') if '|' in node_name else [node_name]
                # 移除分割后产生的空字符串
                node_names_to_process = [part for part in node_names_to_process if part]

                # 逐个处理拆分后的节点名称
                for part_name in node_names_to_process:
                    # 遍历替换配置参数
                    for replace_param in config:
                        # 使用替换工具根据参数替换节点名称
                        self.nodeP.replace_node_name(
                            enabled=replace_param['switch_checkbox'],  # 是否启用替换
                            ignore_case=replace_param['case_sensitive'],  # 是否忽略大小写
                            target=replace_param['target_cont'],  # 替换目标内容
                            replacement=replace_param['replace_cont'],  # 替换为的内容
                            node_name=part_name  # 当前处理的节点名称
                        )

# ----------------------------------------->>>># 实例使用各种类

# 实例使用路径连接
def path_detection_connection_button():
    PDC = Path_Detection_Connection()
    PDC.main()

# 实例使用魔法连接
def magic_connection_button():
    MC = Magic_Node_Connection()
    MC.main()

# 全选转换旧材质到阿诺德
def all_convert_old_materials_to_arnold_button():
    COMTA = ConvertOldMaterialsToArnold(True)
    COMTA.process()

# 选择转换旧材质到阿诺德
def select_convert_old_materials_to_arnold_button():
    COMTA = ConvertOldMaterialsToArnold(False)
    COMTA.process()

# 全选智能材质修复
def all_intelligent_material_repair_button():
    IMR = IntelligentMaterialRepair(True)
    IMR.process()

# 选择智能材质修复
def select_intelligent_material_repair_button():
    IMR = IntelligentMaterialRepair(False)
    IMR.process()

# 快速连接节点
def quick_connect_node_button():
    QCN = QuickConnectNode()
    QCN.process()

# 颜色混合
def intelligent_mix():
    BNM = BlendNodeManager()
    BNM.process(mix_mod='intelligent_mix')

# 遮罩混合
def mask_node_mix():
    BNM = BlendNodeManager()
    BNM.process(mix_mod='mask_mix')

# 主要运行程序
def Main_program():
    from .ui import main_window

    importlib.reload(main_window)
    window_instance = main_window.MainWindow()

