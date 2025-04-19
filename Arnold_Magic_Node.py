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
import concurrent.futures # 并发执行
import difflib # 用于比较文本差异


# 3. PySide 库
# 导入 PySide 库，根据可用版本导入 PySide2 或 PySide6
try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Signal, Slot
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Signal, Slot
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance

from contextlib import contextmanager
# ------------------------------------------
# 获取脚本路径
script_path = os.path.normpath(os.path.join(os.path.dirname(__file__))) # 获取当前脚本的目录路径
# ------------------------------------------

# 9. 自定义库导入与依赖管理
import Arnold_Magic_Node_lib  # 导入自定义的 Arnold 魔法节点库
importlib.reload(Arnold_Magic_Node_lib)  # 在开发阶段，重新加载模块以反映对库的更改
from Arnold_Magic_Node_lib import *  # 从自定义库中导入所有内容

import InitialConfigFile

# 这个是默认窗口的名称记录函数
AMN_UI_WorkSpaceControl = None

##############################################################################################

# --------------------初始变量开始

# _______________________________________________________________>>> 插件状态
SoftwareState = "Release"  # 插件状态
# _______________________________________________________________>>> 插件版本号
SoftwareVersion = "1.1.3" # 插件版本号


pluginHomeURL = r"https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69"
pluginFeedbackURL = r"https://flowus.cn/form/7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69"
pluginUpdateDownloadURL = r'https://flowus.cn/amazingike/share/84422156-5158-4b73-9a5f-c5cadbb6625a?code=LZVF69'
pluginHelpDocumentURL = r'https://flowus.cn/amazingike/share/6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69'

datas_path = os.path.normpath(os.path.join(script_path, "Datas"))  # 定义数据文件夹路径 -> 全局变量

settings_path = os.path.normpath(os.path.join(datas_path, "settings"))  # 定义设置配置文件夹路径 -> 全局变量

icon_path = os.path.normpath(os.path.join(script_path, "icon"))  # 定义图标路径 -> 全局变量

render_preset_path = os.path.normpath(os.path.join(datas_path, "render_presets"))  # 定义渲染预设文件夹路径 -> 全局变量

AMS_Config = "Arnold_Magic_Settings.bin" # Arnold_Magic_Settings

# 定义全局字体大小变量
SMALL_FONT_SIZE = 10
NORMAL_FONT_SIZE = 14
MEDIUM_FONT_SIZE = 16
LARGE_FONT_SIZE = 18
EXTRA_LARGE_FONT_SIZE = 24
# --------------------初始变量结束



# --------------------初始变量结束

# ----------------------------------------------------初始配置变量 开始

TM_FindAndReplace_config_dict = {
    "modify_content_options" : 1 ,
    "modify_scope_options" : 2 ,
    "radio_table_enabled" : False ,
    "search_content" : '' ,
    "replace_content" : '' ,
    "case_sensitive" : True ,
    "use_regex" : False
}

TM_RepathFiles_config_dict = {
    "path_edit" : "",
    "modify_scope_options" : 1 ,
    "search_subfolders_checkbox" : True,
    "forced_path_override_checkbox" : False,
    "multiple_subfolder_search_checkbox" : False,
    "use_cache_checkbox" : True,
    "intelligent_search_mode" : True,
    "normal_search_mode" : True,
}

TM_ImageProcessing_config_dict = {
    "modify_scope_options" : 1 ,
    "format" : "jpg",
    "zoom" : "100",
    "resampling_mode" : 1,
    "JPG_quality" : 90,
    "PNG_quality" : 7,
    "backup_suffix" : '_TM_backup',
    "processed_suffix" : "_TMProc" ,
    "convert_format" : True,
    "scale_texture" : False,
}

TM_texture_pack_config_dict = {
    "path_edit" : "",
    "modify_scope_options" : 1 ,
    "delete_source_files" : False,
    "modify_path" : True,
    "delete_source_tx_files" : False,
    "copy_tx_files" : True,
}

TextureManagerWin_config_dict = {
    'listwidget_data' : 50 ,
}



# ----------------------------------------------------初始配置变量 结束

# 获取Maya主窗口
def MayaMainWindows():
    """获取Maya主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr),QtWidgets.QWidget)

def language_loading():
    dataM = DataManager()

    # 加载语言配置文件并获取 'language_config' 键的值
    language_config = dataM.ascii_load_data(
        os.path.join(script_path, 'Datas', 'settings', 'language_config.json'))['language_config']

    # 动态加载相应语言的JSON文件
    language = dataM.ascii_load_data(
        os.path.join(script_path, 'Datas', 'languages', f'{language_config}.json'))

    return language

#______________________________________________________________________________>>> 插件窗口
class Arnold_Magic_Node_UI(object):
    def __init__(self):
        global AMN_UI_WorkSpaceControl
        # 初始化窗口标题，显示软件状态和版本等信息
        WIN_TITLE = f"Arnold_Magic_Node  {SoftwareState} : {SoftwareVersion}"

        # 检查窗口是否已存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)

        # 创建主窗口
        self.window = cmds.workspaceControl(WIN_TITLE, retain=False, floating=True, w=300, h=300)
        AMN_UI_WorkSpaceControl = self.window

        # 初始化全局配置
        self.initial_global_config()

        # 创建窗口控件
        self.create_widgets()

        # 显示窗口
        cmds.showWindow(self.window)

    def create_widgets(self):
        # 创建行布局
        cmds.rowLayout(numberOfColumns=30)

        # 创建右键菜单
        customMenu = cmds.popupMenu(button=3)
        cmds.menuItem(label=self.language['create_widgets']['ttclgj_menu'], divider=True)  # 贴图处理工具

        # 贴图管理器选项
        cmds.menuItem(
            label=self.language['create_widgets']['ttglq_menu'],
            c=lambda *args: TextureManagerWinInstance(),
            i=icon_path + "\\TXManagerShelf_200.png"
        )

        # 贴图批量导入器选项
        cmds.menuItem(
            label=self.language['create_widgets']['ttpldrq_menu'],
            c=lambda *args: TextureBatchImporterWin(),
            i=icon_path + "\\RenderToTextureShelf_200.png"
        )


        cmds.menuItem(label="AOV管理器", divider=True)  # 渲染预设设置

        # 添加渲染预设选项
        cmds.menuItem(
            label="AOV灯光组管理器",
            c=lambda *args: AOVLightGroupManagerInstance(),
            i=os.path.join(icon_path,"LightManagerShelf_200.png")
        )


        cmds.menuItem(label=self.language['create_widgets']['xryssz_menu'], divider=True)  # 渲染预设设置

        # 添加渲染预设选项
        cmds.menuItem(
            label=self.language['create_widgets']['tjxrys_menu'],
            c=lambda *args: rendering_preset_settings_button(self.rendering_preset)
        )

        # 修改渲染预设选项
        cmds.menuItem(
            label=self.language['create_widgets']['xgxrys_menu'],
            c=lambda *args: modify_rendering_preset_menuItem(
                cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                cmds.optionMenu(self.rendering_preset, query=True, value=True),
                self.rendering_preset_name,
                self.rendering_preset
            )
        )

        # 删除渲染预设选项
        cmds.menuItem(
            label=self.language['create_widgets']['scxrys_menu'],
            c=lambda *args: delete_rendering_preset_menuItem(
                cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                cmds.optionMenu(self.rendering_preset, query=True, value=True),
                self.rendering_preset_name
            )
        )

        # 打开渲染预设文件夹选项
        cmds.menuItem(
            label=self.language['create_widgets']['dkxryswjj_menu'],
            c=lambda *args: os.startfile(render_preset_path)
        )

        cmds.menuItem(divider=True, label='渲染预设输出设置')

        # 输出默认参数选项
        default_rendering_properties_options = cmds.menuItem(
            label=self.language['create_widgets']['default_rendering_properties_options'],
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=['render_preset_params', 'default_rendering_properties_write_options'],
                cont=cmds.menuItem(default_rendering_properties_options, query=True, checkBox=True)
            )
        )

        # 输出阿诺德参数选项
        rendering_properties_options = cmds.menuItem(
            label=self.language['create_widgets']['rendering_properties_options'],
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=['render_preset_params', 'rendering_properties_write_options'],
                cont=cmds.menuItem(rendering_properties_options, query=True, checkBox=True)
            )
        )

        # 输出AOV参数选项
        aov_properties_properties_options = cmds.menuItem(
            label=self.language['create_widgets']['aov_properties_properties_options'],
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=['render_preset_params', 'AOV_properties_properties_write_options'],
                cont=cmds.menuItem(aov_properties_properties_options, query=True, checkBox=True)
            )
        )

        # 设置初始复选框状态
        cmds.menuItem(
            default_rendering_properties_options,
            edit=True,
            checkBox=self.config['render_preset_params']['default_rendering_properties_write_options']
        )
        cmds.menuItem(
            rendering_properties_options,
            edit=True,
            checkBox=self.config['render_preset_params']['rendering_properties_write_options']
        )
        cmds.menuItem(
            aov_properties_properties_options,
            edit=True,
            checkBox=self.config['render_preset_params']['AOV_properties_properties_write_options']
        )

        cmds.menuItem(divider=True, label='其他工具')

        cmds.menuItem(label='优化场景名称',
                      c=lambda *args: self.scene_name_optimization_instance())

        cmds.menuItem(divider=True)
        cmds.menuItem(label='修复选择的FBX材质')
        cmds.menuItem(label='修复所有FBX材质')


        cmds.menuItem(divider=True)

        # 设置面板选项
        cmds.menuItem(
            label=self.language['create_widgets']['sz_menu'],
            c=lambda *args: ArnoldMagicNodeSettingsPanel()
        )

        # 空白文本
        cmds.text(label=" " * 1)

        # 创建各种按钮
        self.magic_connection = cmds.button(
            label=self.language['create_widgets']['magic_connection'],
            c=lambda *args: magic_connection_button()
        )

        self.path_detection_connection = cmds.button(
            label=self.language['create_widgets']['path_detection_connection'],
            c=lambda *args: path_detection_connection_button()
        )

        self.color_mix = cmds.button(
            label=self.language['create_widgets']['color_mix'],
            c=lambda *args: blend_rgba_node()
        )

        self.gray_mix = cmds.button(
            label=self.language['create_widgets']['gray_mix'],
            c=lambda *args: blend_greg_manager()
        )

        # 直连按钮
        self.direct_connection = cmds.button(
            label=self.language['create_widgets']['direct_connection'],
            c=lambda *args: direct_connection_button()
        )

        # 统一UV按钮
        self.unify_uv_node = cmds.button(
            label=self.language['create_widgets']['unify_uv_node'],
            c=lambda *args: unify_uv_node_button()
        )

        cmds.text(label=" " * 2)

        # UV预设选项菜单
        self.uv_preset = cmds.optionMenu(
            mvi=8,
            cc=lambda *args: uv_preset_menu(cmds.optionMenu(self.uv_preset, query=True, value=True))
        )

        # 添加UV模式选项
        uv_mode_list = self.language['create_widgets']['uv_preset']
        for uv_mode_name in uv_mode_list:
            cmds.menuItem(label=uv_mode_name)

        # 色彩空间预设菜单
        self.color_space_preset = cmds.optionMenu(
            mvi=16,
            cc=lambda *args: color_space_preset_menu(
                cmds.optionMenu(self.color_space_preset, query=True, value=True)
            )
        )

        # 循环创建色彩空间菜单选项
        for color_space_name in self.config['color_space_params']['config']:
            cmds.menuItem(label=color_space_name)

        # 自动色彩空间按钮
        cmds.button(
            label=self.language['create_widgets']['zdsckj_button'],
            c=lambda *args: AutoSet_TexColorSpace()
        )

        # 自动UDIM按钮
        cmds.button(
            label=self.language['create_widgets']['zdudim_button'],
            c=lambda *args: auto_set_file_node_udim()
        )

        cmds.text(label=" " * 2)

        # AOV开关按钮
        self.ai_aov_switch = cmds.button(
            label=self.language['create_widgets']['ai_aov_switch'],
            c=lambda *args: ai_aov_switch_button()
        )

        # 渲染预设菜单
        self.rendering_preset_name = {}
        self.rendering_preset = cmds.optionMenu(
            mvi=8,
            cc=lambda *args: rendering_preset_menu(cmds.optionMenu(self.rendering_preset, query=True, value=True))
        )

        # 获取并添加渲染预设文件名
        file_names = os.listdir(render_preset_path)
        file_names_without_json_list = [file_name.replace(".bin", "") for file_name in file_names]

        for renderer_data_mode_name in file_names_without_json_list:
            self.rendering_preset_name[renderer_data_mode_name] = cmds.menuItem(label=renderer_data_mode_name)

        cmds.text(label=" " * 18)

        # 添加图标按钮
        cmds.iconTextButton(
            i=os.path.join(icon_path, 'Autodesk_Arnold_logo.png'),
            h=37.5 / 1.8,
            w=155 / 1.8,
            c=lambda *args: test_program()
        )

        cmds.text(label=" " * 1)
    #______________________________________________________________________________>>> 初始化全局数据
    def initial_global_config(self):
        # 初始化数据管理器和数据处理模块
        self.dataM = DataManager()
        self.dataP = DataProcessor()
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData()  # 获取节点数据模块

        # 加载语言配置
        self.language = language_loading()['ArnoldMagicNode']['AMDUI_WIN']

        # 加载设置配置
        self.config = self.dataM.bin_load_data(os.path.normpath(os.path.join(settings_path, AMS_Config)))

    #______________________________________________________________________________>>> 保存设置内容的函数
    def modify_nested_config(self, key_path, cont):
        """
        修改配置文件的特定键值。

        参数:
        key_path -- 包含要修改的键的路径，以列表形式传递，例如 ["ProcSet_Options", "MagicConnectionSetColorSpace"]
        cont -- 要设置的新值

        功能:
        1. 加载配置数据。
        2. 根据提供的键路径逐层访问并修改对应的值。
        3. 保存修改后的配置数据。
        """
        # 加载当前配置数据
        config = self.dataM.bin_load_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )

        # 遍历键路径，访问到目标键的上一级
        current_level = config
        for key in key_path[:-1]:  # 遍历到倒数第二个键
            current_level = current_level[key]  # 进入下一层级

        # 设置目标键的值为新值
        current_level[key_path[-1]] = cont

        # 保存修改后的配置数据
        self.dataM.bin_save_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config)),
            config
        )

        # 重新加载配置数据以更新当前实例的配置
        self.config = self.dataM.bin_load_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )

    # ______________________________________________________________________________>>> 实例化函数
    def scene_name_optimization_instance(self):
        SNO = SceneNameOptimization()
        SNO.main()

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
        self.config = self.dataM.bin_load_data(
           os.path.normpath(os.path.join(settings_path, AMS_Config)))

        # 加载语言配置
        self.language = language_loading()['ArnoldMagicNode']['AMNSP_WIN']


        self.languages_folder_path = os.path.join(script_path, 'Datas', 'languages')  # 语言文件夹路径

    def initialize_window_config(self):

        WINDOWS_NAME = f"{self.language['initialize_window_config']['WINDOWS_NAME']}  {SoftwareState} : {SoftwareVersion}"  # Win名称

        delete_window_if_existe('ArnoldMagicNodeSettingsPanel')

        self.setObjectName('ArnoldMagicNodeSettingsPanel')
        self.setWindowTitle(WINDOWS_NAME)


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
                                                          InitialConfigFile.Main_program()))


        self.settings_menu.addAction(self.reset_data_action)
        # 创建“语言设置”动作

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

    def create_widgets(self):
        # 创建选项卡部件
        self.tab_widget = QtWidgets.QTabWidget()

        # 创建各个选项卡页面
        self.create_magic_connection_tab()
        self.create_color_space_tab()
        self.create_node_connection_tab()
        self.create_path_matching_tab()
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
        path_detection_config = self.dataM.bin_load_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config)))['path_detection_params']

        # 创建节点路径匹配选项卡
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        path_matching_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(path_matching_widget)

        # [1] 连接时相关设置
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

    # ______________________________________________________________________________>>> 优化场景节点名称页面
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

    # _______________________________>>> 创建界面与布局设置页面
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
        lang_config = self.dataM.ascii_load_data(lang_config_path)

        # 检查配置并设置语言菜单默认值
        for file_name in os.listdir(self.languages_folder_path):
            if lang_config['language_config'] == file_name.replace('.json', ''):
                lang = self.dataM.ascii_load_data(os.path.join(self.languages_folder_path, file_name))
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

        config = self.dataM.bin_load_data(
            os.path.join(settings_path, file_name))

        config[key] = cont

        self.dataM.bin_save_data(
            os.path.join(settings_path, file_name), config)

        ### 初始化配置数据
        self.config = self.dataM.bin_load_data(
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

        # 加载二进制配置数据
        config = self.dataM.bin_load_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )

        # 根据给定的键路径逐层访问数据
        current_level = config
        for key in key_path[:-1]:  # 遍历到倒数第二个键
            current_level = current_level[key]  # 进入下一层级

        # 设置最终键的值为新值
        current_level[key_path[-1]] = cont

        # 保存修改后的配置数据
        self.dataM.bin_save_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config)),
            config
        )

        ### 初始化配置数据
        self.config = self.dataM.bin_load_data(
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
        if keyboard.is_pressed('alt'):
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

            lang = self.dataM.ascii_load_data(os.path.join(folder_path, file_name))
            languages_list.append(lang['language_type'])

        return languages_list

    # 更改语言配置文件
    def change_language(self, language_folder):

        # 获取当前选择的语言
        selected_lang = self.language_combo_box.currentText()

        # 语言配置路径
        lang_config_path = os.path.join(script_path, 'Datas', 'settings', 'language_config.json')

        # 加载语言配置文件
        lang_config = self.dataM.ascii_load_data(lang_config_path)

        # 遍历文件夹中的所有JSON文件
        for file_name in os.listdir(language_folder):
            lang = self.dataM.ascii_load_data(os.path.join(language_folder, file_name))
            if selected_lang == lang['language_type']:
                # 修改语言文件
                lang_config['language_config'] = file_name.replace('.json', '')

                self.feedback.CP(f'语言已修改成:{lang["language_type"]}')

        # 保存修改过后的语言文件
        self.dataM.ascii_save_data(lang_config_path, lang_config)

#______________________________________________________________________________>>>贴图管理器 使用QT库写的窗口！！！
class TextureManagerWin(QtWidgets.QDialog):

    def __init__(self,parent = MayaMainWindows()):
        super(TextureManagerWin, self).__init__(parent)

        # 初始操作
        # 创建实例类
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData() # 提取数据模块
        self.dataM = DataManager() # 储存模块
        self.dataP = DataProcessor() # 数据处理模块

        self.TextureManager_texture_table_data_temp_path = os.path.join(script_path, 'Temp', 'TM_texture_table.bin')
        self.TextureManager_config_path = os.path.join(script_path, 'Datas', 'texture_manager', 'TM_config.bin')

        # 加载语言配置
        self.language =  language_loading()['ArnoldMagicNode']['TM_WIN']

        # 如果有这个TM_texture_table_data文件删除并新创建一个空数据文件
        if os.path.exists(self.TextureManager_texture_table_data_temp_path):
            os.remove(self.TextureManager_texture_table_data_temp_path)
            self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, [])
        else:
            self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, [])

        # 如果没有TM_config_data文件创建一个TM_config_data的配置文件
        if not os.path.exists(self.TextureManager_config_path):
            self.dataM.bin_save_data(self.TextureManager_config_path, TextureManagerWin_config_dict)

        # 初始化获取材质节点的所有信息
        self.MterialNodeAllInfoDict = self.getnodedata.GetMterialNodeAllInfo()

        # 初始化数据<<<<
        self.refresh_scene_node_info()



        # 创建各种的暂存数据变量
        self.temp_cache_material_sl = None
        self.temp_cache_texture_sl = None



        #...窗口名字

        self.WINDOWS_NAME = f"{self.language['__init__']['WINDOWS_NAME']}  {SoftwareState} : {SoftwareVersion}"

        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('TextureManagerWin')



        self.setObjectName('TextureManagerWin')
        self.setWindowTitle(self.WINDOWS_NAME)
        self.setWindowIcon(QtGui.QIcon(icon_path + "\\TXManagerShelf_200.png"))
        #...窗口长宽
        self.setMinimumHeight(700)
        self.setMinimumWidth(1500)









        # 添加隐藏 放大/缩小 几个按钮
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.create_widgets()

        self.create_menu()

        self.create_layouts()
        # 设置全局的 QToolTip 样式
        self.setStyleSheet("""
            QToolTip {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f0f0f0, stop:1 #a9a9a9);
                color: black;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 100);
            }
        """)

    #______________________________________________________________________________>>> 表格的函数
    class DataTableView(QtWidgets.QTableView):
        def __init__(self, outer_instance, parent=None):
            super().__init__(parent)
            self.outer_instance = outer_instance  # 存储对外部类实例的引用

            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(lambda position: self.show_context_menu(position))

        def show_context_menu(self, position):

            menu = QtWidgets.QMenu(self)


            action1 = menu.addAction("测试按钮")
            action1.triggered.connect(lambda *args: self.outer_instance.test())

            menu.addSection("快捷操作") # 添加分组1

            open_file = menu.addAction("打开文件")
            open_file.triggered.connect(lambda *args: self.open_file())

            open_folder = menu.addAction("打开文件夹")
            open_folder.triggered.connect(lambda *args: self.open_folder())

            menu.addSection("图片处理快捷操作")  # 添加分组2
            modified_files  = menu.addAction("源文件切换")
            modified_files.triggered.connect(lambda *args: self.switch_source_tex_files())

            updated_and_deleted_files = menu.addAction("删除处理过文件")
            updated_and_deleted_files.triggered.connect(lambda *args: self.delete_processed_files())

            menu.exec_(self.viewport().mapToGlobal(position))

        # 测试按钮
        def test_button(self):
            self.outer_instance.feedback.CPW(':)')

        # 打开文件
        def open_file(self):

            folder_path = self.outer_instance.get_selected_row_data()[0][7] # 获取选中行的第7列数据（文件路径）

            if not os.path.exists(folder_path):
                self.outer_instance.feedback.CPW('文件路径不存在') # 文件夹不存在
                return # 如果文件夹不存在则直接返回

            # 使用系统默认的文件管理器打开文件夹
            os.startfile(os.path.normpath(folder_path))

        # 打开文件夹
        def open_folder(self):

            folder_path = self.outer_instance.get_selected_row_data()[0][7] # 获取选中行的第7列数据（文件路径）

            if not os.path.exists(folder_path):
                self.outer_instance.feedback.CPW('文件夹路径不存在') # 文件夹不存在
                return # 如果文件夹不存在则直接返回

            # 使用系统默认的文件管理器打开文件夹
            os.startfile(os.path.dirname(os.path.normpath(folder_path)))

        def add_suffix_to_filename(self, file_path, suffix):
            # 分离文件路径和文件名
            dir_name, file_name = os.path.split(file_path)

            # 分离文件名和扩展名
            name, ext = os.path.splitext(file_name)

            # 添加后缀
            new_file_name = f"{name}{suffix}{ext}"

            # 合并回完整路径
            new_file_path = os.path.join(dir_name, new_file_name)

            return new_file_path

        # 修改节点路径
        def modify_node_path(self, node_name, new_path):
            try:
                cmds.setAttr(f"{node_name}.fileTextureName", new_path, type="string")
            except:
                self.feedback.CPW(f'无法重命名只读节点: {node_name}')

        # 刷新表格
        def refresh_table(self, modify_row):
            """
            刷新表格数据并更新UI

            modify_row: list, 需要修改的行数据，每一行的数据包含文件路径和其他信息
            """
            # 用于存储需要更新的数据字典
            update_dict = {}

            # 获取旧的材质节点数据字典
            old_MterialNodeAllInfoDict = self.outer_instance.MterialNodeAllInfoDict

            # 遍历需要修改的行数据，更新路径信息
            for row in modify_row:
                old_MterialNodeAllInfoDict[row[1]][row[0]]['Path'] = row[7]  # 更新每行的路径
                update_dict[row[0]] = row[1]  # 记录更新的节点信息

            # 调用外部方法更新节点状态
            new_MterialNodeAllInfoDict = self.outer_instance.getnodedata.TM_StickerUpdateStatusDict(update_dict,
                                                                                                    old_MterialNodeAllInfoDict)

            # 获取临时存储的表格数据
            temp_TextureManager_texture_table_data = self.outer_instance.dataM.bin_load_data(
                self.outer_instance.TextureManager_texture_table_data_temp_path)

            # 筛选出表格中存在的贴图数据，并将其以字典形式保存
            select_texture_dict = {
                temp_TextureManager_texture_table_data[index][0]: temp_TextureManager_texture_table_data[index][1]
                for index in range(len(temp_TextureManager_texture_table_data))}

            # 更新新的材质节点信息并刷新UI
            self.outer_instance.replace_path_data_and_refresh_ui(new_MterialNodeAllInfoDict, select_texture_dict)

        def switch_source_tex_files(self):
            # 获取当前选中的行数据
            selected_row = self.outer_instance.get_selected_row_data()
            if not selected_row:
                self.outer_instance.feedback.CPW('未选择任何行')
                return
            # 定义可能的扩展名列表，可根据需要调整
            IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.bmp']
            for row in selected_row:
                path = row[7]
                dir_name = os.path.dirname(path)
                file_name = os.path.basename(path)
                base, ext = os.path.splitext(file_name)

                # 预处理文件名（移除可能的版本后缀）
                base_parts = base.split('.')
                version_suffix = ''
                # 检测版本号模式（如 .0001）
                if len(base_parts) > 1 and re.match(r'^\d+$', base_parts[-1]):
                    version_suffix = '.' + base_parts.pop()
                main_base = '.'.join(base_parts)

                if "_TMProc" in main_base:
                    # 删除_TMProc模式
                    new_base = main_base.replace("_TMProc", "") + version_suffix
                    search_pattern = new_base + '*'  # 匹配任意扩展名

                    # 构建可能的候选路径
                    candidate_paths = [
                        os.path.join(dir_name, new_base + ext) for ext in IMAGE_EXTS
                    ]

                    # 添加原始扩展名到首位
                    candidate_paths.insert(0, os.path.join(dir_name, new_base + ext))
                else:
                    # 添加_TMProc模式
                    new_base = main_base + "_TMProc" + version_suffix
                    search_pattern = new_base + '*'  # 匹配任意扩展名

                    # 构建可能的候选路径
                    candidate_paths = [
                        os.path.join(dir_name, new_base + ext) for ext in IMAGE_EXTS
                    ]
                    # 添加原始扩展名到首位
                    candidate_paths.insert(0, os.path.join(dir_name, new_base + ext))

                # 查找存在的文件
                source_path = None
                for candidate in candidate_paths:
                    if os.path.exists(candidate):
                        source_path = candidate
                        break

                if source_path:
                    row[7] = os.path.normpath(source_path)
                    self.modify_node_path(row[0], source_path)
                else:
                    self.outer_instance.feedback.CPW(f'未找到对应文件：{search_pattern}')
            self.refresh_table(selected_row)

        def _parse_udim_filename(self, filename):
            """
            UDIM文件名解析函数
            格式规范：文件名.<UDIM编号>.<扩展名>
            UDIM要求：4位数字，范围1001-9999（Maya官方规范）

            :param filename: 完整文件名(需包含扩展名)
            :return: 解析结果字典
            """
            # 分离基础名称和扩展名
            base_name, file_ext = os.path.splitext(filename)
            parts = base_name.split('.')

            # UDIM正则检测（严格模式）
            udim_pattern = r'^(1\d{3}|[2-9]\d{3})$'  # 1001-9999

            # 反向遍历寻找UDIM编号
            for i in reversed(range(len(parts))):
                if re.match(udim_pattern, parts[i]):
                    # 分离名称部分和UDIM编号
                    udim_id = parts[i]
                    name_part = '.'.join(parts[:i])
                    return {
                        'is_udim': True,
                        'file_name': name_part,
                        'udim_id': udim_id,
                        'extension': file_ext.lower().lstrip('.')
                    }

            # 未找到符合UDIM编号的情况
            return {
                'is_udim': False,
                'file_name': base_name,
                'extension': file_ext.lower().lstrip('.')
            }

        def _find_udim_textures(self, filepath):
            """
            根据给定的贴图文件路径，查找同一目录下所有同名且带有 UDIM 编号的文件。
            参数:
                filepath (str): 带有 UDIM 编号的贴图文件路径，例如 "C:\\path\\to\\texture.1001.jpeg"
            返回:
                list: 同一目录下所有匹配的 UDIM 贴图文件名列表，例如 ["texture.1002.jpeg", "texture.1003.jpeg"]
            """
            directory = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            # 使用正则表达式解析文件名，提取基名、UDIM 编号和扩展名
            # 例如，"Helmet_emissive.1001.jpeg" 中 base="Helmet_emissive", udim="1001", ext="jpeg"
            udim_pattern = re.compile(r'^(?P<base>.+)\.(?P<udim>\d{4})\.(?P<ext>[^.]+)$')
            match = udim_pattern.match(filename)

            if not match:
                print(f"输入文件名 '{filename}' 不符合 UDIM 命名约定。")
                return []
            base = match.group('base')
            ext = match.group('ext')
            # 构建用于匹配的正则表达式
            search_pattern = re.compile(rf'^{re.escape(base)}\.(\d{{4}})\.{re.escape(ext)}$')
            # 列出目录中所有文件
            try:
                all_files = os.listdir(directory)
            except FileNotFoundError:
                print(f"目录 '{directory}' 不存在。")
                return []
            except PermissionError:
                print(f"没有权限访问目录 '{directory}'。")
                return []
            # 筛选出匹配的 UDIM 文件（除了输入文件本身）
            udim_files = [
                f for f in all_files
                if search_pattern.match(f) and os.path.isfile(os.path.join(directory, f)) and f != filename
            ]
            return udim_files

        def delete_processed_files(self):

            # 获取当前选中的行数据
            selected_row = self.outer_instance.get_selected_row_data()

            # 如果没有选择任何行，显示提示并返回
            if not selected_row:
                self.outer_instance.feedback.CPW('未选择任何行')
                return

            # 收集所有需要删除的文件路径
            all_files_to_delete = set()

            for row in selected_row:
                path = row[7]
                if not os.path.exists(path):
                    self.outer_instance.feedback.CPW(f'文件不存在: {path}')
                    continue

                filename = os.path.basename(path)
                udim_info = self._parse_udim_filename(filename)
                is_udim = udim_info['is_udim']

                if is_udim:
                    # 提取原基名（去除可能存在的_TMProc后缀）
                    original_base = udim_info['file_name'].split('_TMProc')[0]
                    # 构建处理过的基名
                    processed_base = original_base + '_TMProc'
                    # 构建虚拟处理过的文件名用于查找UDIM文件
                    processed_filename = f"{processed_base}.{udim_info['udim_id']}.{udim_info['extension']}"
                    virtual_processed_path = os.path.join(os.path.dirname(path), processed_filename)

                    # 查找所有处理过的UDIM文件
                    processed_udim_files = self._find_udim_textures(virtual_processed_path)
                    directory = os.path.dirname(virtual_processed_path)
                    for f in processed_udim_files:
                        full_path = os.path.join(directory, f)
                        all_files_to_delete.add(full_path)

                    # 添加当前文件到删除列表（如果是处理过的文件）
                    if '_TMProc' in filename:
                        all_files_to_delete.add(path)
                else:
                    # 处理非UDIM文件
                    if '_TMProc' in filename:
                        all_files_to_delete.add(path)

            # 删除所有收集到的文件并处理源文件恢复
            for file_path in all_files_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        # 构造源文件路径并检查是否需要恢复
                        source_path = file_path.replace('_TMProc', '')
                        # 更新选中行中对应的路径
                        for row in selected_row:
                            if row[7] == file_path and os.path.exists(source_path):
                                row[7] = source_path
                                self.modify_node_path(row[0], source_path)
                except Exception as e:
                    self.outer_instance.feedback.CPW(f'无法删除文件: {file_path}')

            # 刷新表格数据
            self.refresh_table(selected_row)

    def create_widgets(self):
        lang = self.language['create_widgets']

        # MaterialListSearch 搜索框
        self.MaterialListSearch = QtWidgets.QLineEdit()
        self.MaterialListSearch.textChanged.connect(lambda *args: self.material_list_search())
        self.MaterialListSearch.setFixedWidth(350)
        self.MaterialListSearch.setFixedHeight(40)
        self.MaterialListSearch.setPlaceholderText(lang['MaterialListSearch_placeholder']) # 输入要搜索的材质球名称
        # MaterialListSearch 搜索框一些控件

        # 材质列表刷新
        self.MaterialList_Refresh_Button = QtWidgets.QPushButton()
        self.MaterialList_Refresh_Button.setIcon(QtGui.QIcon(icon_path + "\\ResetMode_200.png"))
        self.MaterialList_Refresh_Button.clicked.connect(lambda *args:  (self.refresh_scene_node_info(),
                                                                        self.refresh_material_list()))
        self.MaterialList_Refresh_Button.setFixedWidth(40)
        self.MaterialList_Refresh_Button.setFixedHeight(40)
        self.MaterialList_Refresh_Button.setIconSize(QtCore.QSize(32, 32))

        # 材质列表
        self.MaterialList = QtWidgets.QListWidget()
        self.MaterialList.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.MaterialList.currentItemChanged.connect(lambda *args: self.material_list_clicked())
        self.MaterialList.itemChanged.connect(lambda *args: self.material_list_material_rename())
        self.MaterialList.setFixedWidth(400)
        self.MaterialList.setIconSize(QtCore.QSize(32, 32))
        self.refresh_material_list()  # 初始化刷新材质列表

        # 材质列表的一些控制器
        self.MaterialList_Display_Slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.MaterialList_Display_Slider.setFixedWidth(400)

        # 获取默认大小
        MaterialList_Slider_default_font = self.MaterialList.font().pixelSize()
        # 计算出默认值的的最小一倍和最大一倍
        self.MaterialList_Display_Slider.setMinimum(1)
        self.MaterialList_Display_Slider.setMaximum(MaterialList_Slider_default_font + MaterialList_Slider_default_font)
        # 并设置成材质列表的默认大小到滑杆上
        self.MaterialList_Display_Slider.setValue(MaterialList_Slider_default_font - 8)
        # 滑杆绑定函数
        self.MaterialList_Display_Slider.valueChanged.connect(lambda *args:  self.updateMaterialListSlider())

        # TexturelListSearch 搜索框
        self.TexturelListSearch = QtWidgets.QLineEdit()
        self.TexturelListSearch.textChanged.connect(lambda *args: self.texture_list_search())
        self.TexturelListSearch.setFixedHeight(40)
        self.TexturelListSearch.setPlaceholderText(lang['TexturelListSearch_placeholder']) # 输入要搜索的贴图球名称
        # TexturelListSearch 搜索框一些控件

        # 贴图列表的刷新
        self.TexturelList_Refresh_Button = QtWidgets.QPushButton()
        self.TexturelList_Refresh_Button.setIcon(QtGui.QIcon(icon_path + "\\ResetMode_200.png"))
        self.TexturelList_Refresh_Button.setFixedWidth(40)
        self.TexturelList_Refresh_Button.setFixedHeight(40)
        self.TexturelList_Refresh_Button.setIconSize(QtCore.QSize(32, 32))
        self.TexturelList_Refresh_Button.clicked.connect(lambda *args:  self.refresh_texture_table())
        self.TexturelList_Refresh_Button.setToolTip(lang['TexturelList_Refresh_Button_ToolTip']) # 根据缓存进行重新刷新

        # 全选材质节点
        self.MaterialList_SelectAll_Button = QtWidgets.QPushButton(lang['MaterialList_SelectAll_Button'])
        # self.MaterialList_SelectAll_Button.setIcon(QtGui.QIcon(icon_path + "\\select_all_icon.png"))
        # self.MaterialList_SelectAll_Button.setFixedWidth(40)
        self.MaterialList_SelectAll_Button.setFixedHeight(40)
        self.MaterialList_SelectAll_Button.clicked.connect(lambda *args:  self.all_selected_materials())
        self.MaterialList_SelectAll_Button.setIconSize(QtCore.QSize(38, 38))

        # 取消所有选择
        self.TexturelList_Unselect_All_Button = QtWidgets.QPushButton(lang['TexturelList_Unselect_All_Button']) # 取消全选 lang['TexturelList_Unselect_All_Button']
        self.TexturelList_Unselect_All_Button.clicked.connect(lambda *args:  (
            self.MaterialList.clearSelection(),
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())
        ))
        self.TexturelList_Unselect_All_Button.setFixedHeight(40)
        #self.TexturelList_Unselect_All_Button.setFixedWidth(40)
        # self.TexturelList_Unselect_All_Button.setIcon(QtGui.QIcon(
        #     os.path.join(icon_path , 'deselect_all_icon.png')))
        self.TexturelList_Unselect_All_Button.setIconSize(QtCore.QSize(38, 38))

        # 反选
        self.TexturelList_reverse_selection = QtWidgets.QPushButton(lang['TexturelList_reverse_selection']) # 反选 lang['TexturelList_reverse_selection']
        self.TexturelList_reverse_selection.setFixedHeight(40)
       # self.TexturelList_reverse_selection.setFixedWidth(40)
        self.TexturelList_reverse_selection.setIconSize(QtCore.QSize(42, 42))
        self.TexturelList_reverse_selection.clicked.connect(lambda *args:  self.texture_list_reverse_selection())
        # self.TexturelList_reverse_selection.setIcon(QtGui.QIcon(
        #     os.path.join(icon_path , 'invert_selection_icon.png')
        # ))

        # 一键选出所有缺失贴图
        self.TexturelList_Find_Missing_Textures_Button = QtWidgets.QPushButton(lang['TexturelList_Find_Missing_Textures_Button']) # 选出缺失 lang['TexturelList_Find_Missing_Textures_Button']
        self.TexturelList_Find_Missing_Textures_Button.clicked.connect(
            lambda *args:  self.texture_list_find_missing_textures())
        self.TexturelList_Find_Missing_Textures_Button.setFixedHeight(40)
        #self.TexturelList_Find_Missing_Textures_Button.setFixedWidth(40)
        self.TexturelList_Find_Missing_Textures_Button.setIconSize(QtCore.QSize(38, 38))
        # self.TexturelList_Find_Missing_Textures_Button.setIcon(QtGui.QIcon(
        #     os.path.join(icon_path , 'select_missing_icon.png')
        # ))

        # 选出最大贴图的按钮
        self.TexturelList_Intelligent_Find_Max_Size_Button = QtWidgets.QPushButton(lang['TexturelList_Intelligent_Find_Max_Size_Button']) # 选出大贴图 lang['TexturelList_Intelligent_Find_Max_Size_Button']
        self.TexturelList_Intelligent_Find_Max_Size_Button.clicked.connect(lambda *args:  self.texture_list_intelligent_find_max_size(self.dataM.bin_load_data(self.TextureManager_config_path)['listwidget_data']))
        self.TexturelList_Intelligent_Find_Max_Size_Button.setFixedHeight(40)
       # self.TexturelList_Intelligent_Find_Max_Size_Button.setFixedWidth(40)
        self.TexturelList_Intelligent_Find_Max_Size_Button.setIconSize(QtCore.QSize(38, 38))
        # self.TexturelList_Intelligent_Find_Max_Size_Button.setIcon(QtGui.QIcon(
        #     os.path.join(icon_path , 'select_large_textures_icon.png')
        # ))

        # 选出最大贴图的容错率值
        self.tolerance_doubleSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.tolerance_doubleSpinBox.setMinimum(0.0)  # 设置最小值
        self.tolerance_doubleSpinBox.setMaximum(10000.0)  # 设置最大值
        self.tolerance_doubleSpinBox.setValue(50.0)  # 设置默认值
        self.tolerance_doubleSpinBox.setSingleStep(0.1)  # 设置步长
        self.tolerance_doubleSpinBox.setDecimals(2)  # 设置小数点后的位数
        self.tolerance_doubleSpinBox.setFixedHeight(40)
        self.tolerance_doubleSpinBox.valueChanged.connect(
            lambda *args:  self.TM_modify_config('listwidget_data', self.tolerance_doubleSpinBox.value()))

        # 替换名称
        self.TexturelList_Search_And_Replace_Date_Button = QtWidgets.QPushButton(
            lang['TexturelList_Search_And_Replace_Date_Button'])
        self.TexturelList_Search_And_Replace_Date_Button.setFixedHeight(40)
        self.TexturelList_Search_And_Replace_Date_Button.clicked.connect(lambda *args:  self.batch_replace_data_Win())

        # 找回所有缺失路径
        self.TexturelList_Replace_Data_Button = QtWidgets.QPushButton(lang['TexturelList_Replace_Data_Button']) # 找回路径
        self.TexturelList_Replace_Data_Button.setFixedHeight(40)
        self.TexturelList_Replace_Data_Button.clicked.connect(lambda *args:  self.find_path_re_Win())

        # 压缩贴图
        self.TexturelList_Processed_Image_Button = QtWidgets.QPushButton(lang['TexturelList_Processed_Image_Button']) # 处理图像
        self.TexturelList_Processed_Image_Button.setFixedHeight(40)
        self.TexturelList_Processed_Image_Button.clicked.connect(lambda *args:  self.image_processing_Win())


        self.TexturelList_Texture_Pack_Button = QtWidgets.QPushButton('贴图打包')
        self.TexturelList_Texture_Pack_Button.setFixedHeight(40)
        self.TexturelList_Texture_Pack_Button.clicked.connect(lambda *args: self.texture_pack_Win())

        # ______________________________________________________________________________>>> 表格控件
        self.TexturelList = self.DataTableView(self)

        # 设置表格的样式
        TexturelList_Headers = lang['TexturelList_Headers'] # "贴图节点名称", "材质球", "大小", "像素大小", "格式", "引用次数", "状态", "路径"

        # 设置表格上下文菜单
        # self.TexturelList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.TexturelList.customContextMenuRequested.connect(lambda position: self.table_show_context_menu(position))

        # 创建自定义的模型，设置第2到6列不可编辑
        self.TEXTURELIST_MODEL = NonEditableColumnsModel(0, 8, non_editable_columns=[2, 3, 4, 5, 6])
        self.TEXTURELIST_MODEL.setHorizontalHeaderLabels(TexturelList_Headers)

        # 设置表格的模型
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)
        self.TexturelList.setColumnWidth(0, 445)
        self.TexturelList.setColumnWidth(1, 200)
        self.TexturelList.setColumnWidth(2, 70)
        self.TexturelList.setColumnWidth(3, 110)
        self.TexturelList.setColumnWidth(4, 60)
        self.TexturelList.setColumnWidth(5, 80)
        self.TexturelList.setColumnWidth(6, 80)
        self.TexturelList.setColumnWidth(7, 1000)

        # 让第7列根据窗口大小自动伸缩
        self.TexturelList.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)

        self.TexturelList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # 更改成多选模式
        self.TexturelList.clicked.connect(lambda *args:  self.selection_texture_sl_node_delay_selection_signal())

        # 启用自动换行
        self.TexturelList.setWordWrap(True)
        # 启用排序功能
        self.TexturelList.setSortingEnabled(True)

        # 让TexturelList表格中的数据居中
        delegate = CenterDelegate(self.TexturelList)
        self.TexturelList.setItemDelegate(delegate)

        # 单独设置第七列左对齐代理（列索引为6）
        left_align_delegate = LeftAlignDelegate(self.TexturelList)
        self.TexturelList.setItemDelegateForColumn(7, left_align_delegate)

        # 编辑表格中的数据
        self.TEXTURELIST_MODEL.dataChanged.connect(lambda top_left, bottom_right, roles: self.texture_list_texture_update(top_left, bottom_right, roles))

        # 设置初始化值
        self.initial_settings()
        # ----------------------------列表 结束

    def create_menu(self):
        # 创建主菜单栏
        self.main_menu_bar = QtWidgets.QMenuBar(self)

        # 创建选择菜单
        self.select_menu = self.main_menu_bar.addMenu('选择')

        # 创建全选动作
        self.select_all_action = QAction('全选', self)
        self.select_all_action.triggered.connect(lambda *args:  self.all_selected_materials())

        # 创建选择缺失动作
        self.select_missing_action = QAction('选择缺失', self)
        self.select_missing_action.triggered.connect(lambda *args:  self.texture_list_find_missing_textures())

        # 创建取消全选动作
        self.deselect_all_action = QAction('取消全选', self)
        self.deselect_all_action.triggered.connect(lambda *args:  (
            self.MaterialList.clearSelection(),
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())))

        # 创建反选动作
        self.invert_selection_action = QAction('反选', self)
        self.invert_selection_action.triggered.connect(lambda *args:  self.texture_list_reverse_selection())

        # 创建选出大贴图动作
        self.select_large_textures_action = QAction('选出大贴图', self)
        self.select_large_textures_action.triggered.connect(lambda *args:  self.texture_list_intelligent_find_max_size(self.dataM.bin_load_data(self.TextureManager_config_path)['listwidget_data']))

        self.select_processed_textures_action = QAction('选择处理过的贴图', self)
        self.select_processed_textures_action.triggered.connect(lambda *args: self.texture_list_find_processed_textures())

        # 将动作添加到选择菜单
        self.select_menu.addAction(self.select_all_action)
        self.select_menu.addAction(self.deselect_all_action)
        self.select_menu.addAction(self.invert_selection_action)
        self.select_menu.addAction(self.select_missing_action)
        self.select_menu.addAction(self.select_large_textures_action)
        self.select_menu.addAction(self.select_processed_textures_action)

        # 关于菜单及其动作
        self.about_menu = self.main_menu_bar.addMenu('关于') # 关于

        # 创建 插件主页菜单
        self.plugin_home = QAction('插件主页') # 插件主页
        self.plugin_home.triggered.connect(
            lambda *args:  QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginHomeURL)))

        # 创建 帮助/反馈菜单
        self.contact_feedback_action = QAction('联系/反馈', self) # 联系/反馈
        self.contact_feedback_action.triggered.connect(
            lambda *args:  QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginFeedbackURL)))

        # 创建“帮助文档”动作并连接到打开帮助文档的槽函数
        self.help_document_action = QAction('帮助文档', self) # 帮助文档
        self.help_document_action.triggered.connect(
            lambda *args: QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginHelpDocumentURL)))

        self.plugin_update_download_action = QAction('插件更新下载', self) # 插件更新下载
        self.plugin_update_download_action.triggered.connect(
            lambda *args: QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginUpdateDownloadURL)))

        # 将动作添加到关于菜单
        self.about_menu.addAction(self.plugin_home)
        self.about_menu.addAction(self.contact_feedback_action)
        self.about_menu.addAction(self.plugin_update_download_action)
        self.about_menu.addAction(self.help_document_action)

    def create_layouts(self):

        # [0][0][0][1][0]材质搜索区域Layout
        Material_Search_Layout = QtWidgets.QHBoxLayout()
        # 材质和贴图搜索区域的按钮和搜索框

        Material_Search_Layout.addWidget(self.MaterialList_Refresh_Button)
        Material_Search_Layout.addWidget(self.MaterialListSearch)

        # [0][0][0][1][1]贴图搜索区域Layout
        Texture_Search_Layout = QtWidgets.QHBoxLayout()

        # 贴图搜索区域的按钮和搜索框
        Texture_Search_Layout.addWidget(self.TexturelList_Refresh_Button)
        Texture_Search_Layout.addWidget(self.TexturelListSearch)
        Texture_Search_Layout.addWidget(self.tolerance_doubleSpinBox)
        Texture_Search_Layout.addWidget(self.TexturelList_Search_And_Replace_Date_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Replace_Data_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Processed_Image_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Texture_Pack_Button)


        # [0][0][0][1] 材质和贴图搜索区域
        Material_And_Texture_Search_Layout = QtWidgets.QHBoxLayout()
        Material_And_Texture_Search_Layout.addLayout(Material_Search_Layout)
        Material_And_Texture_Search_Layout.addLayout(Texture_Search_Layout)
        Material_And_Texture_Search_Layout.setAlignment(QtCore.Qt.AlignLeft)  # 往左对齐

        # [0][0][0][2][0] 材质列表区域
        Material_List_Layout = QtWidgets.QVBoxLayout()
        Material_List_Layout.addWidget(self.MaterialList_Display_Slider)
        Material_List_Layout.addWidget(self.MaterialList)


        # [0][0][0][2][1] 贴图列表区域
        Texture_List_Layout = QtWidgets.QHBoxLayout()
        Texture_List_Layout.addWidget(self.TexturelList)

        # [0][0][0][2] 材质和贴图列表区域
        Material_And_Texture_List_Layout = QtWidgets.QHBoxLayout()
        Material_And_Texture_List_Layout.addLayout(Material_List_Layout)
        Material_And_Texture_List_Layout.addLayout(Texture_List_Layout)
        Material_And_Texture_List_Layout.setAlignment(QtCore.Qt.AlignLeft)  # 往左对齐

        # [0][0][0] 选择区域 (Selection Area)
        Target_Area_Layout = QtWidgets.QVBoxLayout()

        # 把这几个区域添加到选择区域中
        Target_Area_Layout.addLayout(Material_And_Texture_Search_Layout)
        Target_Area_Layout.addLayout(Material_And_Texture_List_Layout)

        # [0][0][1] 修改区域 (Modification Area)
        Edit_Area_Layout = QtWidgets.QHBoxLayout()

        # 选择区域和修改区域 [0]
        Target_And_Edit_Area_Layout = QtWidgets.QHBoxLayout()
        Target_And_Edit_Area_Layout.addLayout(Target_Area_Layout)
        Target_And_Edit_Area_Layout.addLayout(Edit_Area_Layout)

        # 主窗口
        Main_Layout = QtWidgets.QVBoxLayout(self)
        Main_Layout.setMenuBar(self.main_menu_bar)
        Main_Layout.addLayout(Target_And_Edit_Area_Layout)

    def initial_settings(self):
        self.tolerance_doubleSpinBox.setValue(self.dataM.bin_load_data(self.TextureManager_config_path)['listwidget_data'])
    # material_list的功能++++++++++++++++++++++++++++++++++开始

    # material list 点击后激活
    def material_list_clicked(self):
        # 使用 QTimer 延迟处理选择

        # 刷新到贴图表格
        QtCore.QTimer.singleShot(0, lambda *args: self.refresh_to_texture_table())

        # 选择选中的材质球
        QtCore.QTimer.singleShot(0, lambda *args:  self.select_nodes([item.text() for item in self.MaterialList.selectedItems()]))

    # 刷新material_list列表控件
    def refresh_material_list(self):
        # 刷新列表前先把列表清除干净
        self.MaterialList.clear()

        for mat_node_name in self.MterialNodeAllInfoDict:
            item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\render_aiImage.png"), mat_node_name)

            try:
                # 场景中存在的对象都可以获取到材质的类型
                node_type = cmds.nodeType(mat_node_name)
            except:
                # 如果获取不到就是缺失的贴图列表
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\render_aiImage.png"), mat_node_name)
                self.MaterialList.addItem(item)
                break

            if node_type == 'lambert':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\lambert.svg"), mat_node_name)

            elif node_type == 'standardSurface':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\standardSurface.svg"), mat_node_name)

            elif node_type == 'aiStandardSurface':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\render_aiStandardSurface.png"),
                                                 mat_node_name)

            elif node_type == 'aiStandardVolume':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\render_aiVolumeCollector.png"),
                                                 mat_node_name)

            elif node_type == 'aiStandardHair':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\render_aiHair.png"), mat_node_name)

            elif node_type == 'blinn':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\blinn.svg"), mat_node_name)

            elif node_type == 'phongE':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\phongE.svg"), mat_node_name)

            elif node_type == 'phong':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(icon_path + "\\phong.svg"), mat_node_name)

            # 设置为可编辑
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

            # 将item添加到listWidget中
            self.MaterialList.addItem(item)

    # 修改材质列表中的名称，更具相同索引的列表 -如果没有输入值的话就会使用MterialNodeAllInfoDict的材质名称作为列表刷新
    def modify_material_list(self, listwidget_data = None):
        # 提取 self.MaterialList 中的所有数据
        material_list_data = [self.MaterialList.item(i).text() for i in range(self.MaterialList.count())]

        if listwidget_data == None:
            listwidget_data = []
            for matName in self.MterialNodeAllInfoDict:
                listwidget_data.append(matName)

        # 遍历两个列表并进行比较
        for i in range(min(len(material_list_data), len(listwidget_data))):
            if material_list_data[i] != listwidget_data[i]:
                # 如果不相等，则更新 self.MaterialList 中的对应项目
                self.MaterialList.item(i).setText(listwidget_data[i])

        # 处理长度不一致的情况
        if len(listwidget_data) > len(material_list_data):
            # listwidget_data 比 MaterialList 数据多，添加新的项目
            for i in range(len(material_list_data), len(listwidget_data)):
                self.MaterialList.addItem(listwidget_data[i])

        elif len(listwidget_data) < len(material_list_data):
            # MaterialList 数据比 listwidget_data 多，删除多余的项目
            for i in range(len(material_list_data) - 1, len(listwidget_data) - 1, -1):
                self.MaterialList.takeItem(i)

    # material_list_search 搜索框函数
    def material_list_search(self):


        # 获取搜索内容
        search_content = self.MaterialListSearch.text()

        # 获取 QListWidget 中的项数
        item_count = self.MaterialList.count()

        # 如果搜索内容为空，显示所有项
        if search_content == '':
            # 遍历所有项，将其显示
            for i in range(item_count):
                item = self.MaterialList.item(i)
                item.setHidden(False)  # 显示所有项
            return  # 直接返回，不进行后续的过滤

        # 遍历 QListWidget 中的所有项
        for i in range(item_count):
            # 获取每个 QListWidgetItem
            item = self.MaterialList.item(i)

            # 获取项的名称（文本内容）
            matNodeName = item.text()

            # 使用正则表达式进行匹配
            if not re.search(search_content, matNodeName, re.IGNORECASE):
                # 如果不匹配，隐藏该项
                item.setHidden(True)
            else:
                # 如果匹配，显示该项
                item.setHidden(False)



        # # 使用正则表达式搜索，如果找到匹配的内容，就将对应的项添加到列表中
        # for matNodeName in self.MterialNodeAllInfoDict:
        #   if re.search(search_content, matNodeName, re.IGNORECASE):
        #       item = QtWidgets.QListWidgetItem(QtGui.QIcon (icon_path + "\\render_aiStandardSurface.png"), matNodeName)
        #       # 将item添加到listWidget中
        #       self.MaterialList.addItem(item)

    # 点击后把选择的节点刷新到纹理列表
    def refresh_to_texture_table(self):


        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        # 获取所有选中的项
        selected_node_list = self.MaterialList.selectedItems()

        # 提取每个选中项的文本
        selected_mat_node_list = [item.text() for item in selected_node_list]

        # >>>>选中的同时也会产生一个零时选择数据
        if selected_mat_node_list:
            self.temp_cache_material_sl = selected_mat_node_list[0]


        select_texture_dict = {}

        # 选出需要输出的贴图
        for matName in selected_mat_node_list:
            for texName in self.MterialNodeAllInfoDict[matName]:
                select_texture_dict[texName] = matName

        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict)

        self.TexturelList.setModel(self.TEXTURELIST_MODEL)



        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 滑杆刷新材质列表显示大小
    def updateMaterialListSlider(self):
        current_value = self.MaterialList_Display_Slider.value()
        font = QtGui.QFont()
        font.setPointSize(current_value)
        self.MaterialList.setFont(font)

    # 全选材质列表中的选项
    def all_selected_materials(self):

        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        # 选择材质列表的所有选项
        for index in range(self.MaterialList.count()):
            item = self.MaterialList.item(index)
            item.setSelected(True)

        select_texture_dict = {}

        # 转为表格数据
        for matName in self.MterialNodeAllInfoDict:
            for texName in self.MterialNodeAllInfoDict[matName]:
                select_texture_dict[texName] = matName


        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict)
        # 设置模型
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)


        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 修改材质名称
    def material_list_material_rename(self):
        # 在加载选择对应的行之前先清除之前的表格数据
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        # 获取所有选中的项
        selected_node_list = self.MaterialList.selectedItems()

        # 提取每个选中项的文本
        selected_mat_node_list = [item.text() for item in selected_node_list]

        try:
            matNewName = cmds.rename(self.temp_cache_material_sl, selected_mat_node_list)
        except:
            return

        new_dict = {}
        # 迭代原字典，构建新的字典
        for key, value in self.MterialNodeAllInfoDict.items():
            if key == self.temp_cache_material_sl :
                # 替换键名
                new_dict[matNewName] = value
            else:
                # 保持原键值
                new_dict[key] = value

        # 改旧的场景贴图数据节点
        self.MterialNodeAllInfoDict = new_dict



        TextureManager_texture_table_data = self.dataM.bin_load_data(self.TextureManager_texture_table_data_temp_path)

        for index, key in enumerate(TextureManager_texture_table_data):
            if TextureManager_texture_table_data[index][1] == self.temp_cache_material_sl:
                TextureManager_texture_table_data[index][1] = matNewName

        self.add_multiple_rows(self.TEXTURELIST_MODEL, TextureManager_texture_table_data , True)

        # 加载过修改过材质名称的列表模型
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)


        # ---------------------------重新写出零时数据

        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, TextureManager_texture_table_data)

        # 如果改名成功刷新选择内容   >防止再次改名无法找到正确名称
        self.temp_cache_material_sl = matNewName

    # material_list的功能++++++++++++++++++++++++++++++++++结束

    # TexturelList的功能++++++++++++++++++++++++++++++++++开始

    # 纹理列表搜索框
    def texture_list_search(self):

        _texture_data_list = self.dataM.bin_load_data(self.TextureManager_texture_table_data_temp_path)

        # 如果临时储存的文件是空的话就不执行该函数
        if _texture_data_list == "":
            return

        # 获取搜索内容
        search_content = self.TexturelListSearch.text()

        # 如果搜索内容为空，就使用回原始列表
        if search_content == '':
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())
            self.add_multiple_rows(self.TEXTURELIST_MODEL, _texture_data_list, True)
            self.TexturelList.setModel(self.TEXTURELIST_MODEL)
            return

        _search_texture_data_list = []
        # 使用正则表达式搜索，如果找到匹配的内容，就将对应的项添加到列表中
        for table_list in _texture_data_list:
            if re.search(search_content, table_list[0], re.IGNORECASE):
                _search_texture_data_list.append(table_list)

        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())
        self.add_multiple_rows(self.TEXTURELIST_MODEL, _search_texture_data_list, True)

        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

    # 选择的延迟处理
    def selection_texture_sl_node_delay_selection_signal(self):
        # 使用 QTimer 延迟处理选择
        QtCore.QTimer.singleShot(0,lambda *args:  self.selection_texture_sl_node())

    # 选择当前表格选择的节点
    def selection_texture_sl_node(self):

        # 获取当前选中的索引列表
        selected_indexes = self.TexturelList.selectionModel().selectedIndexes()

        # 初始化一个空列表，用于存储选中的数据
        selected_data = []

        # 遍历所有选中的索引
        for index in selected_indexes:
            # 根据索引从模型中获取对应的数据
            data = self.TexturelList.model().data(index)

            # 将获取到的数据添加到 selected_data 列表中
            selected_data.append(data)

        # >>>>选中的同时也会产生一个零时选择数据
        if selected_data:
            self.temp_cache_texture_sl = selected_data[0]

        # 选择选到的贴图节点
        QtCore.QTimer.singleShot(0,lambda *args:  self.select_nodes(selected_data))

    # 列表反选
    def texture_list_reverse_selection(self):
        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        # 从临时文件中加载已保存的贴图数据
        temp_TextureManager_texture_table_data = self.dataM.bin_load_data(
            self.TextureManager_texture_table_data_temp_path)

        # 加载表格数据中的所有贴图名称
        texture_list_from_table = {val[0] for val in temp_TextureManager_texture_table_data}

        # 加载主字典中的所有贴图名称
        texture_list_from_main_dict = {texName for matName in self.MterialNodeAllInfoDict for texName in
                                       self.MterialNodeAllInfoDict[matName]}

        # 计算反选的贴图列表
        reverse_selected_texture_list = list(texture_list_from_main_dict - texture_list_from_table)

        # 获取反选的材质和贴图字典
        reverse_selected_texture_dict = self.dataP.filter_material_textures(reverse_selected_texture_list,
                                                                            self.MterialNodeAllInfoDict)

        # 构建需要添加到表格的数据
        add_multiple_rows_dict = {}
        reverse_selected_mat_list = []

        for matName, texNames in reverse_selected_texture_dict.items():
            reverse_selected_mat_list.append(matName)
            for texName in texNames:
                add_multiple_rows_dict[texName] = matName

        # 将反选的贴图数据添加到表格模型中
        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, add_multiple_rows_dict)

        # 更新模型
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 清除材质列表中所有项目的选中状态
        self.MaterialList.clearSelection()

        # 选择材质列表中的对应项目
        for i in range(self.MaterialList.count()):
            item = self.MaterialList.item(i)
            if item.text() in reverse_selected_mat_list:
                item.setSelected(True)

        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 选择缺失贴图
    def texture_list_find_missing_textures(self):
        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        select_texture_dict = {}

        # 遍历所有材质节点信息，提取未加载的贴图
        for matName, texDict in self.MterialNodeAllInfoDict.items():
            for texName, texInfo in texDict.items():
                if not texInfo['isLoaded']:  # 判断贴图是否未加载
                    select_texture_dict[texName] = matName

        # 先取消MaterialList中所有项目的选中状态
        self.MaterialList.clearSelection()

        # 选择出选中的材质
        for i in range(self.MaterialList.count()):
            item = self.MaterialList.item(i)
            if item.text() in select_texture_dict.values():  # 直接判断材质是否在字典中
                item.setSelected(True)

        # 添加选中的贴图数据到模型
        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict)

        # 更新模型
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 只有在数据变化时才保存临时文件
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 智能获取最大值
    def texture_list_intelligent_find_max_size(self, tolerance_mb=50):

        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        select_matName_list = [] # 选择到材质的空列表

        # 初始化最大Size和最大纹理列表
        max_size = 0
        max_textures = {}
        data_dict = self.MterialNodeAllInfoDict
        # 遍历字典找到最大的纹理Size
        for material, textures in data_dict.items():
            for texture_name, texture_info in textures.items():
                texture_size = texture_info.get('Size', 0)
                if texture_size > max_size:
                    max_size = texture_size

        # 计算容错范围
        tolerance_size = max_size - tolerance_mb

        large_textures_dict = {}

        for matName in data_dict:
            for texName in data_dict[matName]:
                if data_dict[matName][texName]['Size'] >= tolerance_size:
                    select_matName_list.append(matName)
                    large_textures_dict[texName] = matName

        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, large_textures_dict)

        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 先取消MaterialList中所有项目的选中状态
        self.MaterialList.clearSelection()

        # 选择出选中的材质
        for i in range(self.MaterialList.count()):
            item = self.MaterialList.item(i)
            # 如果项目的文本在select_texture_list中，就选择它
            if item.text() in select_matName_list:
                item.setSelected(True)


        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 选择出处理过的贴图
    def texture_list_find_processed_textures(self):
        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        select_texture_dict = {}

        # 遍历所有材质节点信息，提取已处理的贴图
        for matName, texDict in self.MterialNodeAllInfoDict.items():
            for texName, texInfo in texDict.items():
                if "_TMProc" in os.path.basename(texInfo['Path']):  # 判断贴图是否已处理
                    select_texture_dict[texName] = matName


        # 先取消MaterialList中所有项目的选中状态
        self.MaterialList.clearSelection()

        # 选择出选中的材质
        for i in range(self.MaterialList.count()):
            item = self.MaterialList.item(i)
            if item.text() in select_texture_dict.values():  # 直接判断材质是否在字典中
                item.setSelected(True)

        # 添加选中的贴图数据到模型
        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict)

        # 更新模型
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 只有在数据变化时才保存临时文件
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 更改贴图列表中的贴图节点名称还有路径
    def texture_list_texture_update(self, top_left, bottom_right, roles):


        # 获取当前选中的索引列表
        selected_indexes = self.TexturelList.selectionModel().selectedIndexes()

        # 初始化一个空列表，用于存储选中的数据
        selected_data = []

        # 遍历所有选中的索引
        for index in selected_indexes:
            # 根据索引从模型中获取对应的数据
            data = self.TexturelList.model().data(index)

            # 将获取到的数据添加到 selected_data 列表中
            selected_data.append(data)

        # 获取编辑的行号
        row = top_left.row()

        texNodeName = self.TEXTURELIST_MODEL.item(row, 0).text()
        matNodeName = self.TEXTURELIST_MODEL.item(row, 1).text()
        texNodePath = self.TEXTURELIST_MODEL.item(row, 7).text()



        # 如果数据是空的就不执行下面的
        if self.temp_cache_texture_sl is None or selected_data is []:
            return



        if top_left.column() == 0 and bottom_right.column() == 0:
            # 修改贴图节点名称
            texNewName = cmds.rename(self.temp_cache_texture_sl, texNodeName)

            # 创建一个新的字典用于存储更新后的材质节点信息
            new_tex_info_dict = {}

            # 遍历所有的材质节点信息字典
            for matName in self.MterialNodeAllInfoDict:
                # 为当前材质节点创建一个新的字典
                new_tex_info_dict[matName] = {}
                # 遍历当前材质节点下的所有贴图信息
                for texName, value in self.MterialNodeAllInfoDict[matName].items():
                    # 如果当前贴图名称等于临时缓存的贴图名称，则更新为新地贴图名称
                    if texName == self.temp_cache_texture_sl:
                        new_tex_info_dict[matName][texNewName] = value
                    else:
                        # 否则保持原来地贴图名称和对应的值
                        new_tex_info_dict[matName][texName] = value

            # 更新材质节点的全部信息字典为修改后的字典
            self.MterialNodeAllInfoDict = new_tex_info_dict

            # 加载贴图管理器的贴图表数据
            TextureManager_texture_table_data = self.dataM.bin_load_data(self.TextureManager_texture_table_data_temp_path)

            # 遍历贴图表数据，根据索引查找并替换旧的贴图名称为新的贴图名称
            for index, key in enumerate(TextureManager_texture_table_data):
                if TextureManager_texture_table_data[index][0] == self.temp_cache_texture_sl:
                    TextureManager_texture_table_data[index][0] = texNewName


            # 如果改名成功刷新选择内容   >防止再次改名无法找到正确名称
            self.temp_cache_texture_sl = texNewName

            # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
            self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, TextureManager_texture_table_data)

        elif top_left.column() == 7 and bottom_right.column() == 7:
            # 在加载选择对应的行之前先清除之前的表格数据
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

            # 修改节点的路径
            cmds.setAttr(f"{texNodeName}.fileTextureName", texNodePath , type="string")

            if not self.MterialNodeAllInfoDict[matNodeName][texNodeName]['Path'] == texNodePath:
                self.MterialNodeAllInfoDict[matNodeName][texNodeName]['Path'] = texNodePath
            else:
                return

            # 加载贴图管理器的贴图表数据
            TextureManager_texture_table_temp_data = self.dataM.bin_load_data(self.TextureManager_texture_table_data_temp_path)



            update_dict = {}
            update_dict[texNodeName] = matNodeName


            # 根据新的路径更新字典中的信息
            new_MterialNodeAllInfoDict = self.getnodedata.TM_StickerUpdateStatusDict(update_dict, self.MterialNodeAllInfoDict)

            # 把总信息更新
            self.MterialNodeAllInfoDict = new_MterialNodeAllInfoDict

            # 获取当前表格中都有那些贴图
            table_tex_list = []
            for index, key in enumerate(TextureManager_texture_table_temp_data):
                table_tex_list.append(TextureManager_texture_table_temp_data[index][0])

            # 把表格中有的贴图做成的列表在总信息中筛选出来
            select_texture_dict = {}
            for index, table_list in enumerate(TextureManager_texture_table_temp_data):
                select_texture_dict[TextureManager_texture_table_temp_data[index][0]] = TextureManager_texture_table_temp_data[index][1]

            # 更新表格
            TextureManager_texture_table_data = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict)

            # 设置模型
            self.TexturelList.setModel(self.TEXTURELIST_MODEL)

            # 如果改名成功刷新选择内容   >防止再次改名无法找到正确名称
            self.temp_cache_texture_sl = texNodePath

            # 把贴图表格的数据写到临时文件里
            self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, TextureManager_texture_table_data)

    # 从缓存中刷新纹理表格
    def refresh_texture_table(self, use_cache = True):
        """
        功能是刷新纹理表格

        如果use_cache是true的话就是使用缓存去进行重置表格
        如果是False就是使用字典去重新刷新表格


        """

        if use_cache == True:
            # 从缓存中获取表格数据

            temp_TextureManager_texture_table_data = self.dataM.bin_load_data(self.TextureManager_texture_table_data_temp_path)

            # 在加载选择对应的行之前先清除之前的
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

            # 把缓存表格数据加载到模型中
            self.add_multiple_rows(self.TEXTURELIST_MODEL, temp_TextureManager_texture_table_data, True)

        else:
            self.add_multiple_rows(self.TEXTURELIST_MODEL, self.MterialNodeAllInfoDict)

        # 把模型加载到表格
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 返回缓存数据

        return temp_TextureManager_texture_table_data

    # TexturelList的功能++++++++++++++++++++++++++++++++++结束

    # 其他窗口-----------------------------------------开始

    def batch_replace_data_Win(self):
        # 实例化数据替换窗口
        tm_FindAndReplaceWin = TM_FindAndReplace(self.WINDOWS_NAME, parent=self)
        tm_FindAndReplaceWin.show()

        # 连接信号和槽
        tm_FindAndReplaceWin.base_data_signal.connect(lambda new_MterialNodeAllInfoDict: self.replace_base_data_and_refresh_ui(new_MterialNodeAllInfoDict))
        tm_FindAndReplaceWin.base_data_bundle_signal.connect(lambda new_MterialNodeAllInfoDict, select_texture_dict:
                                                             self.replace_path_data_and_refresh_ui(new_MterialNodeAllInfoDict, select_texture_dict))

    def find_path_re_Win(self):
        tm_RepathFiles = TM_RepathFiles(self.WINDOWS_NAME, parent=self)
        tm_RepathFiles.show()

        tm_RepathFiles.new_MterialNodeAllInfoDict_signal.connect(lambda new_MterialNodeAllInfoDict, select_texture_dict:
                                                                 self.replace_path_data_and_refresh_ui(new_MterialNodeAllInfoDict, select_texture_dict))

    def image_processing_Win(self):
        tm_ImageProcessing = TM_ImageProcessing(self.WINDOWS_NAME, parent=self)
        tm_ImageProcessing.show()

        tm_ImageProcessing.new_MterialNodeAllInfoDict_signal.connect(lambda new_MterialNodeAllInfoDict, select_texture_dict:
                                                                     self.replace_path_data_and_refresh_ui(new_MterialNodeAllInfoDict, select_texture_dict))

    def texture_pack_Win(self):
        tm_TexturePack = TM_TexturePack(self.WINDOWS_NAME, parent=self)
        tm_TexturePack.show()

        tm_TexturePack.new_MterialNodeAllInfoDict_signal.connect(lambda new_MterialNodeAllInfoDict, select_texture_dict:
                                                                 self.replace_path_data_and_refresh_ui(new_MterialNodeAllInfoDict, select_texture_dict))

    # 其他窗口-----------------------------------------结束


    # 选择表格内容返回数据函数 -----------------------------------------开始

    # 获取表格中的所有数据
    def get_all_table_data(self):
        """
        获取表格中的所有数据

        model: 表格的数据模型 (例如 QAbstractTableModel 或其子类)
        """

        model = self.TEXTURELIST_MODEL

        all_rows_data = []  # 用于存储所有行的数据

        # 获取表格的总行数
        row_count = model.rowCount()

        # 获取表格的总列数
        column_count = model.columnCount()

        # 遍历所有行和列，提取数据
        for row in range(row_count):
            row_data = [model.data(model.index(row, column)) for column in range(column_count)]
            all_rows_data.append(row_data)

        return all_rows_data

    # 获取选中行的数据
    def get_selected_row_data(self):
        """
        获取选中行的数据

        model: 表格的数据模型 (例如 QAbstractTableModel 或其子类)
        table_variables: 表格视图的变量 (例如 QTableView)
        """
        model = self.TEXTURELIST_MODEL
        table_variables = self.TexturelList
        # 获取当前选择模型
        selection_model = table_variables.selectionModel()

        # 获取选中的索引
        selected_indexes = selection_model.selectedIndexes()

        # 如果没有选中任何单元格
        if not selected_indexes:
            return None

        # 用于存储选中的行数据
        selected_rows_data = []

        # 遍历所有选中的单元格
        for index in selected_indexes:
            row = index.row()  # 获取当前单元格所在的行
            # 获取该行所有列的数据
            row_data = [model.data(model.index(row, column)) for column in range(model.columnCount())]

            # 将该行的数据添加到选中的行数据列表中
            if row_data not in selected_rows_data:
                selected_rows_data.append(row_data)

        return selected_rows_data

    # 将列表转换为字典，使用列表的第0个元素作为键查找字典中的数据
    def convert_list_to_dict(self, data_dict, target_list):
        """
        将列表转换为字典，使用列表的第0个元素作为键查找字典中的数据
        并重建一个新的字典。

        参数：
        data_dict: dict, 主要的数据字典，其中键为材质名称，值为一个字典，
                   该字典包含纹理名称及其对应的纹理数据。
        target_list: list, 目标列表，列表中的每个元素的第0个值将作为纹理名称来查找。

        返回：
        new_dict: dict, 新的字典，按材质名称组织，包含匹配的纹理数据。
        """
        print("target_list", target_list)
        print("data_dict", data_dict)

        new_dict = {}  # 用于存储最终结果的字典


        if target_list is None:
            self.feedback.CPW('没有选中任何行')
            return {}

        # 将目标列表中的第0个元素提取为集合，用于加速后续的查找操作
        target_nodes = set(item[0] for item in target_list)

        # 遍历输入的data_dict字典
        for material_name, value in data_dict.items():
            # 对每个材质的纹理进行遍历
            for texture_name, texture_data in value.items():
                # 只有当纹理名称texture_name在目标节点集合target_nodes中时才处理
                if texture_name in target_nodes:
                    # 如果材质名称还没有加入new_dict，则初始化一个空字典
                    if material_name not in new_dict:
                        new_dict[material_name] = {}
                    # 将匹配的纹理数据加入到new_dict中
                    new_dict[material_name][texture_name] = texture_data

        return new_dict

    # 根据修改范围选择对应的数据
    def get_selected_table_data(self, modify_scope):
        """根据修改范围选择对应的数据"""
        if modify_scope == 1:
            return self.MterialNodeAllInfoDict
        elif modify_scope == 2:
            selected_table_data = self.get_all_table_data()
            return self.convert_list_to_dict(self.MterialNodeAllInfoDict, selected_table_data)
        elif modify_scope == 3:
            selected_table_data = self.get_selected_row_data()
            return self.convert_list_to_dict(self.MterialNodeAllInfoDict, selected_table_data)



        return {}  # 默认返回空字典

    # 选择表格内容返回数据函数 -----------------------------------------结束

    # 一些快捷操作函数 -----------------------------------------开始

    # 刷新主窗口的数据
    def refresh_main_window_texture_data(self):
        # 获取主窗口的表格数据
        old_table_data = self.TextureManagerWin.MterialNodeAllInfoDict

        # 获取零时的表格列表数据
        temp_TextureManager_texture_table_data = self.dataM.bin_load_data(
            self.TextureManagerWin.TextureManager_texture_table_data_temp_path)





    # 一些快捷操作函数 -----------------------------------------结束
    def state_set_background_colors(self, model):
        # 遍历模型中的每一行
        for row in range(model.rowCount()):
            # 获取第六列（索引为5）的值
            table_texture_name_item = model.item(row, 0)
            table_texture_name = table_texture_name_item.text()
            table_material_name_item = model.item(row, 1)
            table_material_name = table_material_name_item.text()


            if self.MterialNodeAllInfoDict[table_material_name][table_texture_name]['isLoaded']: # 正常
                # 更细致的绿色 (RGB: 34, 177, 76) 和 50% 透明度
                color = QtGui.QColor(34, 177, 76, 128)  # RGB + Alpha
            else: # 缺失
                # 更细致的红色 (RGB: 237, 28, 36) 和 50% 透明度
                color = QtGui.QColor(237, 28, 36, 128)  # RGB + Alpha


            # 设置第六行的背景颜色
            item = model.item(row, 6)

            item.setData(color, QtCore.Qt.BackgroundRole)
        #
        # for row in range(model.rowCount()):
        #     # 获取第六列（索引为5）的值
        #     table_texture_name_item = model.item(row, 0)
        #     table_texture_name = table_texture_name_item.text()
        #     table_material_name_item = model.item(row, 1)
        #     table_material_name = table_material_name_item.text()
        #     path =  self.MterialNodeAllInfoDict[table_material_name][table_texture_name]['Path']
        #
        #     # 检查纹理名称是否包含 '_TMProc' 后缀
        #     if  "_TMProc" in os.path.basename(path):
        #         # 设置为黄色背景 (RGB: 255, 255, 0) 和 50% 透明度
        #         color1 = QtGui.QColor(255, 255, 64, 64)  # RGB + Alpha
        #     else:
        #         continue
        #
        #     # 设置第一列的背景颜色
        #     first_item = model.item(row,0)
        #     if first_item:
        #         first_item.setData(color1, QtCore.Qt.BackgroundRole)


    # 刷新获取场景的数据
    def refresh_scene_node_info(self):

        starttime = time.time()
        # 初始化获取材质节点的所有信息
        self.MterialNodeAllInfoDict = self.getnodedata.GetMterialNodeAllInfo()

        MterialNodeAllInfoDict_TexList = []
        for matName in self.MterialNodeAllInfoDict:
            for texName in self.MterialNodeAllInfoDict[matName]:
                MterialNodeAllInfoDict_TexList.append(texName)

        unlisted_textures = self.getnodedata.FindUnlistedTextures(MterialNodeAllInfoDict_TexList)
        unlisted_textures_info_dict = self.getnodedata.GetTexturesNodeAllInfo(unlisted_textures)
        self.MterialNodeAllInfoDict.update(unlisted_textures_info_dict)

        # 删除重复的Key（删除重复的纹理节点，因为获取是通过材质球去获取的，如果节点有多个引用就会导致有多个相同的数据）
        self.MterialNodeAllInfoDict = self.dataP.remove_duplicate_keys(self.MterialNodeAllInfoDict)

        endtime = time.time()
        self.feedback.CP("刷新获取数据使用的时间:" + str(format((endtime - starttime), ".3f")) + "秒")

    # 将数据以row格式添加到表格
    def add_multiple_rows(self, model, select_texture_dict, Use_data = False, MterialNodeAllInfoDict = None):
        """
        add_multiple_rows 函数用于将纹理相关的信息以行的形式添加到一个表格模型中。这个函数的主要功能是根据提供的纹理数据，
        将信息如纹理名称、材质名称、尺寸、格式、引用次数、加载状态和路径等格式化，并逐行添加到指定的模型中。该模型通常用于在用
        户界面（如图形化应用程序）中展示这些信息。

        函数支持两种不同的工作模式：

        动态生成模式：从 select_texture_dict 字典中提取纹理信息，并动态生成需要的数据列表。
        直接使用模式：直接使用传入的 select_texture_dict 作为数据源，而不进行动态生成。

        最终，函数会将整理好的数据行添加到表格模型中，并根据需要调整每行的背景颜色，以实现视觉区分或状态提示。

        """

        if MterialNodeAllInfoDict == None:
            MterialNodeAllInfoDict = self.MterialNodeAllInfoDict

        # 如果 Use_data 为 False，则手动从 select_texture_dict 构建 _texture_data_list
        if Use_data == False:
            _texture_data_list = []  # 初始化存储纹理数据的列表

            # 遍历选中的贴图字典
            for texName in select_texture_dict:
                matName = select_texture_dict[texName]  # 获取材质名称

                Size = MterialNodeAllInfoDict[matName][texName]['Size']  # 获取贴图大小

                # 格式化大小为小数点后一位的字符串形式，注意捕获异常以防格式化失败
                try:
                    Size = format(Size, '.1f')
                except:
                    pass  # 如果格式化失败，保持原始的大小值

                Dimensions = f"{MterialNodeAllInfoDict[matName][texName]['Dimensions'][0]}x{MterialNodeAllInfoDict[matName][texName]['Dimensions'][1]}" # 格式化像素尺寸为 "宽x高" 的字符串
                Format = MterialNodeAllInfoDict[matName][texName]['Format']  # 获取贴图的格式 (如png, jpg)
                usageCount = str(MterialNodeAllInfoDict[matName][texName]['usageCount'])  # 获取贴图的引用次数并转为字符串
                # 根据是否加载设置状态文本 ('正常' 或 '缺失')
                if MterialNodeAllInfoDict[matName][texName]['isLoaded'] == True:
                    isLoaded = self.language['state']['normal'] # 正常
                else:
                    isLoaded = self.language['state']['lack'] # 缺失

                Path = MterialNodeAllInfoDict[matName][texName]['Path']  # 获取贴图路径

                # 构建一行数据，注意列表中数据的顺序
                row = [
                    texName,  # 纹理名称
                    matName,  # 材质名称
                    Size,  # 贴图大小
                    Dimensions,  # 像素大小 (宽x高)
                    Format,  # 贴图格式
                    usageCount,  # 引用次数
                    isLoaded,  # 贴图状态 (正常或缺失)
                    Path  # 贴图路径
                ]

                # 将构建的行数据添加到 _texture_data_list 列表中
                _texture_data_list.append(row)
        else:
            # 如果 Use_data 为 True，则直接使用传入的 select_texture_dict 作为数据列表
            _texture_data_list = select_texture_dict

        # 遍历 _texture_data_list，将每一行数据作为 QStandardItem 添加到模型中
        for row_data in _texture_data_list:
            row_items = [QtGui.QStandardItem(item) for item in row_data]
            model.appendRow(row_items)

        self.state_set_background_colors(model)  # 设置背景颜色（具体实现不在此代码片段中）

        return _texture_data_list  # 返回生成的 _texture_data_list 以供后续使用

    # 选择节点
    def select_nodes(self, node_list, exclusion_list = None):

        if exclusion_list == None:
            exclusion_list = ['Unlisted Textures']

        # 遍历 node_list 的副本，检查每个节点是否在排除列表中
        # 如果节点在排除列表中，则从 node_list 中删除该节点
        for node in node_list[:]: # 使用 node_list[:] 来避免在遍历时修改原始列表
            if node in exclusion_list:
                node_list.remove(node)
        try:
            cmds.select(node_list)
        except Exception as e:
            pass
            #self.feedback.CP('请选择正确的内容')

    # 储存配置文件
    def TM_modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.TextureManager_config_path)

        config[key] = cont

        self.dataM.bin_save_data(self.TextureManager_config_path, config)

    @Slot(dict)
    def replace_base_data_and_refresh_ui(self, new_MterialNodeAllInfoDict):
        # 处理从子窗口传来的数据
        self.MterialNodeAllInfoDict = new_MterialNodeAllInfoDict

        # 刷新材质列表
        self.modify_material_list()

        # 刷新表格
        self.refresh_texture_table()

    @Slot(dict, dict)
    def replace_path_data_and_refresh_ui(self, new_MterialNodeAllInfoDict, select_texture_dict):

        TextureManager_texture_table_data = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict, MterialNodeAllInfoDict=new_MterialNodeAllInfoDict)

        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # # 把刷新的贴图数据存入缓存中
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, TextureManager_texture_table_data)

        # # 刷新表格
        self.refresh_texture_table()

#______________________________________________________________________________>>>贴图管理器的搜索与替换界面
class TM_FindAndReplace(QtWidgets.QDialog):
    # 定义一个信号，传递多个变量
    base_data_signal = Signal(dict)
    base_data_bundle_signal = Signal(dict, dict)

    def __init__(self, WinName = '', parent = None):
        super(TM_FindAndReplace, self).__init__(parent)
        self.TextureManagerWin = parent  # 保存主窗口的引用

        # 创建初始实例与变量
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.dataM = DataManager()
        self.dataP = DataProcessor()
        self.getnodedata = GetNodeData()

        self.config_path = os.path.join(script_path, 'Datas', 'texture_manager', 'TM_find_and_replace_config.bin') # 历史写入路径

        # 加载语言配置
        self.language =  language_loading()['ArnoldMagicNode']['TM_FAR_WIN']

        # 命名常量命名
        WINDOWS_NAME =  self.language['__init__']['WINDOWS_NAME'] + WinName #Win名称

        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('TM_FindAndReplace_Win')

        self.setObjectName('TM_FindAndReplace_Win')
        self.setWindowTitle(WINDOWS_NAME)
        #...窗口长宽
        self.setMinimumHeight(400)
        self.setMinimumWidth(630)

        # 初始化配置内容
        self.initial_config()

        self.create_widgets()
        self.create_layouts()

        # 初始化设置内容
        self.initial_settings()

    def create_widgets(self):
        lang = self.language['create_widgets']  # 获取当前语言的数据

        # 设置字体大小
        font_20x = QtGui.QFont()
        font_20x.setPointSize(20)  # 设置字体大小为20

        font_15x = QtGui.QFont()
        font_15x.setPointSize(15)  # 设置字体大小为15

        font_10x = QtGui.QFont()
        font_10x.setPointSize(10)  # 设置字体大小为10

        # 第一行 两个文字内容
        self.label_data_to_edit_options = QtWidgets.QLabel(lang['label_data_to_edit_options'])  # 修改内容
        self.label_data_to_edit_options.setFont(font_20x)
        self.label_data_to_edit_options.setAlignment(QtCore.Qt.AlignCenter)  # 居中文字
        self.label_data_to_edit_options.setStyleSheet("letter-spacing: 5px;")

        self.label_data_to_edit_options_02 = QtWidgets.QLabel(lang['label_data_to_edit_options_02'])  # 你需要根据你要修改的内容选择
        self.label_data_to_edit_options_02.setAlignment(QtCore.Qt.AlignCenter)  # 居中文字
        self.label_data_to_edit_options_02.setStyleSheet("""
                                                            letter-spacing: 8px;
                                                            color: rgb(128, 128, 128);
                                                        """)
        # 选择修改内容的选项
        self.select_group = QtWidgets.QButtonGroup(self)
        self.sl_material = QtWidgets.QRadioButton(lang['sl_material'])  # 材质
        self.sl_texture = QtWidgets.QRadioButton(lang['sl_texture'])  # 贴图
        self.sl_texture_path = QtWidgets.QRadioButton(lang['sl_texture_path'])  # 贴图路径
        self.select_group.addButton(self.sl_material, 1)
        self.select_group.addButton(self.sl_texture, 2)
        self.select_group.addButton(self.sl_texture_path, 3)
        self.select_group.buttonClicked.connect(lambda button: (
            self.modify_config('modify_content_options', self.select_group.id(button))
        ))

        # 创建目标内容和替换内容交换的按钮
        self.button_target_to_replace = QtWidgets.QPushButton('↓')  # 目标内容 → 替换内容
        self.button_target_to_replace.setFixedWidth(50)
        self.button_target_to_replace.clicked.connect(self.target_to_replace)
        self.button_replace_to_target = QtWidgets.QPushButton('↑')  # 替换内容 → 目标内容
        self.button_replace_to_target.setFixedWidth(50)
        self.button_replace_to_target.clicked.connect(self.replace_to_target)
        self.button_swap = QtWidgets.QPushButton('↑↓')  # 互相切换
        self.button_swap.setFixedWidth(50)
        self.button_swap.clicked.connect(self.swap_content)
        self.button_clear = QtWidgets.QPushButton('✖')  # 清除按钮
        self.button_clear.setFixedWidth(50)
        self.button_clear.clicked.connect(self.clear_content)



        self.label_modify_options = QtWidgets.QLabel(lang['label_modify_options'])  # 修改内容的范围
        self.label_modify_options.setAlignment(QtCore.Qt.AlignCenter)  # 居中文字
        self.label_modify_options.setStyleSheet("""
                                                    letter-spacing: 8px;
                                                    color: rgb(128, 128, 128);
                                                """)
        # 选择修改范围的选项
        self.modify_group = QtWidgets.QButtonGroup(self)
        self.radio_all = QtWidgets.QRadioButton(lang['radio_all'])  # 全部
        self.radio_table = QtWidgets.QRadioButton(lang['radio_table'])  # 表格内
        self.radio_selection = QtWidgets.QRadioButton(lang['radio_selection'])  # 选择中
        self.modify_group.addButton(self.radio_all, 1)
        self.modify_group.addButton(self.radio_table, 2)
        self.modify_group.addButton(self.radio_selection, 3)
        self.modify_group.buttonClicked.connect(
            lambda button: self.modify_config('modify_scope_options', self.modify_group.id(button)))

        # 创建第二行的控件（标签和输入框）
        self.label_find = QtWidgets.QLabel(lang['label_find'])  # 查找内容
        self.label_find.setFont(font_10x)
        self.label_find.setAlignment(QtCore.Qt.AlignCenter)  # 居中文字

        self.line_edit_find = QtWidgets.QLineEdit()
        self.line_edit_find.setFixedHeight(40)
        self.line_edit_find.setPlaceholderText(lang['line_edit_find_placeholder'])  # 请输入查找内容...
        self.line_edit_find.textChanged.connect(
            lambda *args:  self.modify_config('search_content', self.line_edit_find.text()))

        self.label_replace = QtWidgets.QLabel(lang['label_replace'])  # ↓ ↓ ↓ ↓ ↓ ↓
        self.label_replace.setFont(font_10x)
        self.label_replace.setAlignment(QtCore.Qt.AlignCenter)  # 居中文字

        self.line_edit_replace = QtWidgets.QLineEdit()
        self.line_edit_replace.setFixedHeight(40)
        self.line_edit_replace.setPlaceholderText(lang['line_edit_replace_placeholder'])  # 请输入替换内容...
        self.line_edit_replace.textChanged.connect(
            lambda *args:  self.modify_config('replace_content', self.line_edit_replace.text()))

        # 创建第三行的控件（复选框）
        self.checkbox_case_sensitive = QtWidgets.QCheckBox(lang['checkbox_case_sensitive'])  # 大小写忽略
        self.checkbox_case_sensitive.stateChanged.connect(
            lambda *args:  self.modify_config('case_sensitive', self.checkbox_case_sensitive.isChecked()))

        self.checkbox_regex = QtWidgets.QCheckBox(lang['checkbox_regex'])  # 使用正则表达式
        self.checkbox_regex.stateChanged.connect(
            lambda *args:  self.modify_config('use_regex', self.checkbox_regex.isChecked()))

        # 创建第四行的控件（替换按钮）
        self.button_replace = QtWidgets.QPushButton(lang['button_replace'])  # 替换
        self.button_replace.clicked.connect(lambda *args:  self.replace_button())

    def create_layouts(self):
        # 创建主垂直布局
        main_layout = QtWidgets.QVBoxLayout(self)

        label_data_to_edit_layout = QtWidgets.QVBoxLayout()
        # 设置布局中控件之间的间距为 0

        #label_data_to_edit_layout.setContentsMargins(0, 0, 0, 0)
        # label_data_to_edit_layout.addWidget(self.label_data_to_edit_options)
        label_data_to_edit_layout.addWidget(self.label_data_to_edit_options_02)

        # 往上对齐Layout
        label_data_to_edit_layout.setAlignment(self.label_data_to_edit_options_02, QtCore.Qt.AlignTop)

        # 选择修改的内容Layout的选项
        data_to_edit_options_layou = QtWidgets.QHBoxLayout()
        data_to_edit_options_layou.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        data_to_edit_options_layou.addWidget(self.sl_material)
        data_to_edit_options_layou.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        data_to_edit_options_layou.addWidget(self.sl_texture)
        data_to_edit_options_layou.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        data_to_edit_options_layou.addWidget(self.sl_texture_path)
        data_to_edit_options_layou.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 修改内容的范围标题
        modify_options_label_layout = QtWidgets.QVBoxLayout()
        modify_options_label_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        modify_options_label_layout.addWidget(self.label_modify_options)
        modify_options_label_layout.setAlignment(self.label_modify_options, QtCore.Qt.AlignTop)

        # 修改内容的范围的选项
        modify_options_layout = QtWidgets.QHBoxLayout()
        modify_options_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        modify_options_layout.addWidget(self.radio_all)
        modify_options_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        modify_options_layout.addWidget(self.radio_table)
        modify_options_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        modify_options_layout.addWidget(self.radio_selection)
        modify_options_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))



        # 第二行：竖向布局，包含标签和输入框
        # 在原有的 modify_content_layout 部分修改如下
        modify_content_layout = QtWidgets.QVBoxLayout()
        modify_content_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 目标内容列
        target_layout = QtWidgets.QVBoxLayout()
        target_layout.addWidget(self.label_find)
        target_layout.addWidget(self.line_edit_find)

        # 按钮列
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button_target_to_replace)
        button_layout.addWidget(self.button_replace_to_target)
        button_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        button_layout.addWidget(self.label_replace)
        button_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        button_layout.addWidget(self.button_swap)
        button_layout.addWidget(self.button_clear)

        button_layout.addStretch()

        # 替换内容列
        replace_layout = QtWidgets.QVBoxLayout()

        replace_layout.addWidget(self.line_edit_replace)

        modify_content_layout.addLayout(target_layout)
        modify_content_layout.addLayout(button_layout)
        modify_content_layout.addLayout(replace_layout)
        modify_content_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 第三行：横向布局，包含复选框
        search_settings_layout = QtWidgets.QHBoxLayout()
        search_settings_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        search_settings_layout.addWidget(self.checkbox_case_sensitive)
        search_settings_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        search_settings_layout.addWidget(self.checkbox_regex)
        search_settings_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        #search_settings_layout.addStretch()  # 使用伸缩项，使复选框分布开来

        # 第四行：横向布局，包含替换按钮
        finish_button_layout = QtWidgets.QHBoxLayout()
        finish_button_layout.addStretch()  # 使用伸缩项，使按钮居中
        finish_button_layout.addWidget(self.button_replace)
        finish_button_layout.addStretch()  # 使用伸缩项，使按钮居中

        # 将所有行布局添加到主布局中
        main_layout.addLayout(label_data_to_edit_layout)
        main_layout.addLayout(data_to_edit_options_layou)
        main_layout.addLayout(modify_options_label_layout)
        main_layout.addLayout(modify_options_layout)
        # main_layout.addLayout(hotword_button_layout)
        main_layout.addLayout(modify_content_layout)
        main_layout.addLayout(search_settings_layout)
        main_layout.addLayout(finish_button_layout)

        # 设置对话框的布局
        self.setLayout(main_layout)

    def target_to_replace(self):
        # 将目标内容复制到替换内容
        self.line_edit_replace.setText(self.line_edit_find.text())
        self.modify_config('replace_content', self.line_edit_find.text())

    def replace_to_target(self):
        # 将替换内容复制到目标内容
        self.line_edit_find.setText(self.line_edit_replace.text())
        self.modify_config('search_content', self.line_edit_replace.text())

    def swap_content(self):
        # 交换目标内容和替换内容
        temp = self.line_edit_find.text()
        self.line_edit_find.setText(self.line_edit_replace.text())
        self.line_edit_replace.setText(temp)

        # 更新配置
        self.modify_config('search_content', self.line_edit_find.text())
        self.modify_config('replace_content', self.line_edit_replace.text())

    def clear_content(self):
        # 清除目标内容和替换内容
        self.line_edit_find.clear()
        self.line_edit_replace.clear()

        # 更新配置
        self.modify_config('search_content', '')
        self.modify_config('replace_content', '')

    def initial_config(self):

        # 如果没有默认配置文件会创建一个新的默认配置文件
        if not os.path.exists(self.config_path):
            self.dataM.bin_save_data(self.config_path, TM_FindAndReplace_config_dict)

    def initial_settings(self):
        # 设置 select_group 的默认选中按钮（通过 ID）
        select_group_button = self.select_group.button(self.dataM.bin_load_data(self.config_path)['modify_content_options'])
        if select_group_button:
            select_group_button.setChecked(True)  # 设置该按钮为选中状态

        # 设置 select_group 的默认选中按钮（通过 ID）
        modify_group_button = self.modify_group.button(self.dataM.bin_load_data(self.config_path)['modify_scope_options'])
        if modify_group_button:
            modify_group_button.setChecked(True)  # 设置该按钮为选中状态


        self.line_edit_find.setText(self.dataM.bin_load_data(self.config_path)['search_content'])
        self.line_edit_replace.setText(self.dataM.bin_load_data(self.config_path)['replace_content'])

        self.checkbox_case_sensitive.setChecked(self.dataM.bin_load_data(self.config_path)['case_sensitive'])
        self.checkbox_regex.setChecked(self.dataM.bin_load_data(self.config_path)['use_regex'])




    class ReplaceContent:
        def __init__(self, outer_instance):

            self.outer_instance = outer_instance # 存储对外部类实例的引用

            self.dataM = DataManager() # 数据管理
            self.dataP = DataProcessor() # 数据处理
            self.feedback = FeedbackPrompt()  # 错误提示模块
            self.getnodedata = GetNodeData() # 获取节点数据模块

            # 初始化默认变量
            self.config = self.dataM.bin_load_data(self.outer_instance.config_path)

            # 访问继承TextureManagerWin里面最新的MterialNodeAllInfoDict
            self.old_material_node_all_info_dict = self.outer_instance.TextureManagerWin.MterialNodeAllInfoDict

            # 获取零时数据
            self.temp_TextureManager_texture_table_data = self.dataM.bin_load_data(
                self.outer_instance.TextureManagerWin.TextureManager_texture_table_data_temp_path)

        def save_temp_data(self, temp_TextureManager_texture_table_data):

            # 保存修改后的数据到临时文件
            self.dataM.bin_save_data(self.outer_instance.TextureManagerWin.TextureManager_texture_table_data_temp_path,
                                     temp_TextureManager_texture_table_data)

        # 修改材质名称
        def change_material_name (self, select_data):
            # 创建初始变量
            temp_TextureManager_texture_table_data = self.temp_TextureManager_texture_table_data
            new_material_node_all_info_dict = self.old_material_node_all_info_dict

            # 遍历选中的数据
            for material_name, value in list(select_data.items()):
                old_material_name = material_name

                # 修改材质的名称
                new_material_name = self.dataP.SimpleSearchAndReplaceData(
                                                                   old_material_name,
                                                                   self.config['search_content'],
                                                                   self.config['replace_content'],
                                                                   self.config['case_sensitive'],
                                                                   self.config['use_regex'])

                # 重命名材质
                if old_material_name == new_material_name:
                    continue
                else:
                    try:
                        cmds.rename(old_material_name, new_material_name)
                    except Exception as e:
                        self.feedback.CPW(e)
                        continue

                # 在修改字典键时保持原有顺序
                if old_material_name in new_material_node_all_info_dict:
                    # 将字典内容转为有序的键值对列表
                    items = list(new_material_node_all_info_dict.items())
                    # 替换旧键为新键
                    new_items = [(new_material_name if k == old_material_name else k, v) for k, v in items]
                    # 清空原字典以保持引用不变
                    new_material_node_all_info_dict.clear()
                    # 按顺序重新插入所有键值对
                    for k, v in new_items:
                        new_material_node_all_info_dict[k] = v

                # 修改零时缓存数据
                for index, value in enumerate(temp_TextureManager_texture_table_data):
                    if temp_TextureManager_texture_table_data[index][1] == old_material_name:
                        temp_TextureManager_texture_table_data[index][1] = new_material_name

                self.save_temp_data(temp_TextureManager_texture_table_data)

                # 激活一次讯号到主窗口，并把修改好的字典传递回去
                self.outer_instance.base_data_signal.emit(new_material_node_all_info_dict)

        # 修改贴图名称
        def change_texture_name (self, select_data):
            # 创建初始变量
            temp_TextureManager_texture_table_data = self.temp_TextureManager_texture_table_data
            new_material_node_all_info_dict = self.old_material_node_all_info_dict

            for material_name, value in list(select_data.items()):
                for texture_name, texture_data in list(value.items()):

                        old_texture_name = texture_name

                        # 修贴图名称
                        new_texture_name = self.dataP.SimpleSearchAndReplaceData(
                            old_texture_name,
                            self.config['search_content'],
                            self.config['replace_content'],
                            self.config['case_sensitive'],
                            self.config['use_regex'])

                        # 如果贴图名称没有变化就使用原来的名称
                        if old_texture_name == new_texture_name:
                            continue
                        else:
                            try:
                                cmds.rename(old_texture_name, new_texture_name)
                            except Exception as e:
                                self.feedback.CPW(e)
                                continue

                        # 修改数据内容的键
                        if old_texture_name in new_material_node_all_info_dict[material_name]:
                            # 获取旧键对应的值
                            material_info =  new_material_node_all_info_dict[material_name].pop(old_texture_name)
                            # 使用新键创建新的字典项
                            new_material_node_all_info_dict[material_name][new_texture_name] = material_info

                        # 修改零时缓存数据
                        for index, value in enumerate(temp_TextureManager_texture_table_data):
                            if temp_TextureManager_texture_table_data[index][0] == old_texture_name:
                                temp_TextureManager_texture_table_data[index][0] = new_texture_name

                        self.save_temp_data(temp_TextureManager_texture_table_data)

                        # 激活一次讯号到主窗口，并把修改好的字典传递回去
                        self.outer_instance.base_data_signal.emit(new_material_node_all_info_dict)

        # 修改贴图路径
        def change_texture_path(self, select_data):
            # 获取临时纹理管理器表格数据和材质节点信息字典
            temp_TextureManager_texture_table_data = self.temp_TextureManager_texture_table_data
            new_material_node_all_info_dict = self.old_material_node_all_info_dict

            # 初始化需要更新的节点字典
            update_dict = {}
            # 遍历选中的数据
            for material_name, value in list(select_data.items()):
                for texture_name, texture_data in list(value.items()):
                    # 获取旧的纹理路径
                    old_path = texture_data['Path']
                    # 使用搜索替换方法获取新的纹理路径
                    new_path = self.dataP.SimpleSearchAndReplaceData(
                        old_path,
                        self.config['search_content'],
                        self.config['replace_content'],
                        self.config['case_sensitive'],
                        self.config['use_regex'])
                    # 如果路径没有变化，跳过当前循环
                    if old_path == new_path:
                        continue
                    else:
                        try:
                            # 尝试更新Maya文件纹理节点的路径
                            cmds.setAttr(f"{texture_name}.fileTextureName", new_path, type="string")
                        except Exception as e:
                            # 如果更新失败，打印错误信息并继续下一个循环
                            self.feedback.CPW(e)
                            continue
                    # 更新材质节点信息字典中的路径
                    new_material_node_all_info_dict[material_name][texture_name]['Path'] = new_path
                    # 记录需要更新状态的节点
                    update_dict[texture_name] = material_name
                    # 更新临时缓存数据中的纹理路径
                    for index, value in enumerate(temp_TextureManager_texture_table_data):
                        if temp_TextureManager_texture_table_data[index][7] == old_path:
                            temp_TextureManager_texture_table_data[index][7] = new_path
                    # 保存更新后的临时数据
                    self.save_temp_data(temp_TextureManager_texture_table_data)
            # 更新材质节点的状态
            new_material_node_all_info_dict = self.getnodedata.TM_StickerUpdateStatusDict(
                update_dict,
                new_material_node_all_info_dict
            )
            # 创建选中纹理的字典
            select_texture_dict = {
                table_list[0]: table_list[1]
                for table_list in temp_TextureManager_texture_table_data
            }
            # 发送更新后的材质节点信息和选中纹理字典到主窗口
            self.outer_instance.base_data_bundle_signal.emit(
                new_material_node_all_info_dict,
                select_texture_dict
            )



        def process(self):

            select_data = self.outer_instance.TextureManagerWin.get_selected_table_data(self.config['modify_scope_options'])


            # 1，修改材质名称
            if self.config['modify_content_options'] == 1:
                self.change_material_name(select_data)

            # 2，修改贴图名称
            elif self.config['modify_content_options'] == 2:
                self.change_texture_name(select_data)

            # 3，修改贴图路径
            elif self.config['modify_content_options'] == 3:
                self.change_texture_path(select_data)

    def replace_button(self):
        replace_content = self.ReplaceContent(self)
        replace_content.process()


    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.config_path)

        config[key] = cont

        self.dataM.bin_save_data(self.config_path, config)
    # --------------------保存设置内容的函数

#______________________________________________________________________________>>>贴图管理器的寻找路径修复界面
class TM_RepathFiles(QtWidgets.QDialog):
    # 定义一个信号，传递多个变量
    new_MterialNodeAllInfoDict_signal = Signal(dict, dict)

    def __init__(self, WinName = '', parent = None):
        super(TM_RepathFiles, self).__init__(parent)

        self.TextureManagerWin = parent  # 保存主窗口的引用

        # 0. 初始化全局配置
        self.initial_global_config()

        # 1. 初始化窗口配置
        self.initialize_window_config(WinName)

        # 2. 创建控件
        self.create_widgets()

        # 3. 创建菜单
        self.menu_widgets()

        # 4. 创建布局
        self.create_layouts()

        # 5. 初始化控件
        self.initial_widgets_settings()

    # 初始化窗口配置
    def initialize_window_config(self, WinName):

        # 命名常量命名
        WINDOWS_NAME =  self.language['initialize_window_config']['WINDOWS_NAME'] + WinName #Win名称

        delete_window_if_existe('TM_RepathFiles_Win')

        self.setObjectName('TM_RepathFiles_Win')
        self.setWindowTitle(WINDOWS_NAME)

        #...窗口长宽
        #self.setMinimumHeight(400)
        self.setMinimumWidth(650)

    # 初始化全局设置
    def initial_global_config(self):
        # 实例数据管理器
        self.dataM = DataManager() # 数据管理
        self.dataP = DataProcessor() # 数据处理
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData() # 获取节点数据模块



        # 加载语言配置
        self.language =  language_loading()['ArnoldMagicNode']['TM_RF_WIN']


        self.TM_repath_files_config_FilePath = os.path.join(script_path, "Datas", "texture_manager", "TM_repath_files_config.bin")

        # 如果TM_repath_files_config配置文件不存在会重新创建一次
        if not os.path.exists(self.TM_repath_files_config_FilePath):
            self.dataM.bin_save_data(self.TM_repath_files_config_FilePath, TM_RepathFiles_config_dict)

        self.tm_repath_file_cache_filepath = os.path.join(script_path, "Datas", "texture_manager",
                                                            "TM_repath_files_cache.bin")

        # 缓存空字典创建
        tm_repath_file_cache_dict = {}

        # 如果TM_repath_files_cache缓存文件不存在会重新创建一次
        if not os.path.exists(self.tm_repath_file_cache_filepath):
            self.dataM.bin_save_data(self.tm_repath_file_cache_filepath, tm_repath_file_cache_dict)

    # 创建控件
    def create_widgets(self):
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setFixedHeight(40)
        self.path_edit.textChanged.connect(lambda text: self.modify_config('path_edit', text))

        self.select_folder_button = QtWidgets.QPushButton('. . .')
        self.select_folder_button.setFixedHeight(38)
        self.select_folder_button.setFixedWidth(35)
        self.select_folder_button.clicked.connect(lambda *args: self.select_folder())


        self.modify_group = QtWidgets.QButtonGroup(self)
        self.radio_all = QtWidgets.QRadioButton('全部')  # '全部'选项
        self.radio_table = QtWidgets.QRadioButton('表格内')  # '表格内'选项
        self.radio_selection = QtWidgets.QRadioButton('选择中')  # '选择中'选项
        self.modify_group.addButton(self.radio_all, 1)  # 将按钮加入组
        self.modify_group.addButton(self.radio_table, 2)
        self.modify_group.addButton(self.radio_selection, 3)

        # 当选择变化时，更新配置文件中的选项
        self.modify_group.buttonClicked.connect(
            lambda button: self.modify_config('modify_scope_options', self.modify_group.id(button)))

        self.use_cache_checkbox = QtWidgets.QCheckBox('缓存搜索模式') # 使用缓存搜索
        self.use_cache_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('use_cache_checkbox', self.use_cache_checkbox.isChecked()))

        self.intelligent_search_mode_checkbox = QtWidgets.QCheckBox(
            self.language['create_widgets']['memory_search_mode_checkbox'])  # 智能搜索
        self.intelligent_search_mode_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('intelligent_search_mode', self.intelligent_search_mode_checkbox.isChecked()))

        self.normal_search_mode_checkbox  = QtWidgets.QCheckBox('普通搜索模式')  # 使用缓存
        self.normal_search_mode_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('normal_search_mode', self.normal_search_mode_checkbox.isChecked()))

        self.search_subfolders_checkbox = QtWidgets.QCheckBox(self.language['create_widgets']['search_subfolders_checkbox']) # 搜索子文件夹
        self.search_subfolders_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('search_subfolders_checkbox', self.search_subfolders_checkbox.isChecked()))


        self.multiple_subfolder_search_checkbox = QtWidgets.QCheckBox(self.language['create_widgets']['multiple_subfolder_search_checkbox']) # 多个子文件夹搜索
        self.multiple_subfolder_search_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('multiple_subfolder_search_checkbox', self.multiple_subfolder_search_checkbox.isChecked()))

        self.forced_path_override_checkbox  = QtWidgets.QCheckBox('强制搜索')  # 使用缓存
        self.forced_path_override_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('forced_path_override_checkbox', self.forced_path_override_checkbox.isChecked()))



        self.fix_path_button = QtWidgets.QPushButton(self.language['create_widgets']['fix_path_button'])
        self.fix_path_button.clicked.connect(lambda *args:  self.fix_path())

    # 创建菜单
    def menu_widgets(self):

        # 创建菜单栏
        self.menu_bar = QtWidgets.QMenuBar(self)

        # 创建“编辑”菜单，并传递菜单名称
        self.edit_menu = self.menu_bar.addMenu("编辑")  # 编辑

        # 重置设置
        self.reset_settings = QAction('重置设置', self)  # 重置设置
        self.reset_settings.triggered.connect(lambda *args: os.remove(self.TM_repath_files_config_FilePath))

        # 创建“清除路径缓存”动作
        self.clear_cache = QAction('清除正确路径的缓存', self)  # 清除缓存 ！谨慎删除！
        self.clear_cache.triggered.connect(lambda *args: os.remove(self.tm_repath_file_cache_filepath))  # 绑定清除缓存函数

        self.edit_menu.addAction(self.reset_settings)
        self.edit_menu.addAction(self.clear_cache)

        self.help_menu = self.menu_bar.addMenu("帮助") # 帮助

        self.instructions_action = QAction("使用说明", self) # 使用说明
        self.help_menu.addAction(self.instructions_action)

    # 创建布局
    def create_layouts(self):
        # 路径输入的窗口文件夹
        path_list_layout = QtWidgets.QHBoxLayout()
        path_list_layout.addWidget(self.path_edit)
        path_list_layout.addWidget(self.select_folder_button)

        # 选择修改范围的选项
        selection_layout = QtWidgets.QHBoxLayout()
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_all)
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_table)
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_selection)
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 配置选项输入
        config_checkbox_01 = QtWidgets.QHBoxLayout()
        config_checkbox_01.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        config_checkbox_01.addWidget(self.use_cache_checkbox)
        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        config_checkbox_01.addWidget(self.intelligent_search_mode_checkbox)
        config_checkbox_01.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        config_checkbox_01.addWidget(self.normal_search_mode_checkbox)
        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        config_checkbox_01.addWidget(self.search_subfolders_checkbox)
        config_checkbox_01.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        config_checkbox_01.addWidget(self.multiple_subfolder_search_checkbox)
        config_checkbox_01.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        config_checkbox_01.addWidget(self.forced_path_override_checkbox)
        config_checkbox_01.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        # 按钮
        button_01 = QtWidgets.QHBoxLayout()
        button_01.addWidget(self.fix_path_button)

        # 主布局
        MainLayout = QtWidgets.QVBoxLayout(self)
        MainLayout.setMenuBar(self.menu_bar)
        MainLayout.addLayout(path_list_layout)
        MainLayout.addItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        MainLayout.addLayout(selection_layout)
        MainLayout.addItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        MainLayout.addLayout(config_checkbox_01)
        MainLayout.addItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        MainLayout.addLayout(button_01)

    # 初始化控件设置
    def initial_widgets_settings(self):
        self.path_edit.setText(self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['path_edit'])

        # 设置 select_group 的默认选中按钮（通过 ID）
        modify_group_button = self.modify_group.button(self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['modify_scope_options'])
        if modify_group_button:
            modify_group_button.setChecked(True)  # 设置该按钮为选中状态

        self.intelligent_search_mode_checkbox.setChecked(
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['intelligent_search_mode'])
        self.search_subfolders_checkbox.setChecked(
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['search_subfolders_checkbox'])
        self.multiple_subfolder_search_checkbox.setChecked(
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['multiple_subfolder_search_checkbox'])
        self.forced_path_override_checkbox.setChecked(
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['forced_path_override_checkbox'])
        self.use_cache_checkbox.setChecked(
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['use_cache_checkbox'])
        self.normal_search_mode_checkbox.setChecked(
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['normal_search_mode'])

    # 选择文件夹
    def select_folder(self):

        default_url = self.path_edit.text()

        if os.path.exists(default_url):

            folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择文件夹", default_url)
        else:
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择文件夹", '')

        # 判断是防止没有选择并执行了写入到控件的命令。如果空内容写入会导致使用不适
        if not folder_path == '':
            self.path_edit.setText(folder_path)

    class FixPath:
        def __init__(self, outer_instance, exclude_extensions):
            super().__init__()


            self.same_path_dict = {} # 需要搜索的贴图字典
            self.need_search_texture_dict = {} # 相同路径的字典

            self.outer_instance = outer_instance # 存储对外部类实例的引用

            self.dataM = DataManager() # 数据管理
            self.dataP = DataProcessor() # 数据处理
            self.feedback = FeedbackPrompt()  # 错误提示模块
            self.getnodedata = GetNodeData() # 获取节点数据模块

            # 获取路径
            self.enter_path = self.dataM.bin_load_data(outer_instance.TM_repath_files_config_FilePath)['path_edit']

            # 从主窗口获取的材质所有数据
            self.old_MterialNodeAllInfoDict = outer_instance.TextureManagerWin.MterialNodeAllInfoDict

            # 排除的格式列表
            self.exclude_extensions = exclude_extensions

            # 定义缓存文件路径
            self.cache_file_path = outer_instance.tm_repath_file_cache_filepath

        # 获取表格中的所有数据
        def get_all_table_data(self, model):
            """
            获取表格中的所有数据

            model: 表格的数据模型 (例如 QAbstractTableModel 或其子类)
            """
            all_rows_data = []  # 用于存储所有行的数据

            # 获取表格的总行数
            row_count = model.rowCount()

            # 获取表格的总列数
            column_count = model.columnCount()

            # 遍历所有行和列，提取数据
            for row in range(row_count):
                row_data = [model.data(model.index(row, column)) for column in range(column_count)]
                all_rows_data.append(row_data)

            return all_rows_data

        # 获取选中行的数据
        def get_selected_row_data(self, model, table_variables):
            """
            获取选中行的数据

            model: 表格的数据模型 (例如 QAbstractTableModel 或其子类)
            table_variables: 表格视图的变量 (例如 QTableView)
            """
            # 获取当前选择模型
            selection_model = table_variables.selectionModel()

            # 获取选中的索引
            selected_indexes = selection_model.selectedIndexes()

            # 如果没有选中任何单元格
            if not selected_indexes:
                return None

            # 用于存储选中的行数据
            selected_rows_data = []

            # 遍历所有选中的单元格
            for index in selected_indexes:
                row = index.row()  # 获取当前单元格所在的行
                # 获取该行所有列的数据
                row_data = [model.data(model.index(row, column)) for column in range(model.columnCount())]

                # 将该行的数据添加到选中的行数据列表中
                if row_data not in selected_rows_data:
                    selected_rows_data.append(row_data)

            return selected_rows_data

        # 将列表转换为字典，使用列表的第0个元素作为键查找字典中的数据
        def convert_list_to_dict(self, data_dict, target_list):
            """
            将列表转换为字典，使用列表的第0个元素作为键查找字典中的数据
            并重建一个新的字典。

            参数：
            data_dict: dict, 主要的数据字典，其中键为材质名称，值为一个字典，
                       该字典包含纹理名称及其对应的纹理数据。
            target_list: list, 目标列表，列表中的每个元素的第0个值将作为纹理名称来查找。

            返回：
            new_dict: dict, 新的字典，按材质名称组织，包含匹配的纹理数据。
            """
            new_dict = {}  # 用于存储最终结果的字典

            if target_list is None:
                self.feedback.CPW('没有选中任何行')
                return {}

            # 将目标列表中的第0个元素提取为集合，用于加速后续的查找操作
            target_nodes = set(item[0] for item in target_list)

            # 遍历输入的data_dict字典
            for material_name, value in data_dict.items():
                # 对每个材质的纹理进行遍历
                for texture_name, texture_data in value.items():
                    # 只有当纹理名称texture_name在目标节点集合target_nodes中时才处理
                    if texture_name in target_nodes:
                        # 如果材质名称还没有加入new_dict，则初始化一个空字典
                        if material_name not in new_dict:
                            new_dict[material_name] = {}
                        # 将匹配的纹理数据加入到new_dict中
                        new_dict[material_name][texture_name] = texture_data

            return new_dict

        # 根据修改范围选择对应的数据
        def get_selected_table_data(self, modify_scope):
            """根据修改范围选择对应的数据"""
            if modify_scope == 1:
                return self.old_MterialNodeAllInfoDict
            elif modify_scope == 2:
                selected_table_data = self.get_all_table_data(
                    model=self.outer_instance.TextureManagerWin.TEXTURELIST_MODEL)
                return self.convert_list_to_dict(self.old_MterialNodeAllInfoDict, selected_table_data)
            elif modify_scope == 3:
                selected_table_data = self.get_selected_row_data(
                    model=self.outer_instance.TextureManagerWin.TEXTURELIST_MODEL,
                    table_variables=self.outer_instance.TextureManagerWin.TexturelList
                )
                return self.convert_list_to_dict(self.old_MterialNodeAllInfoDict, selected_table_data)
            return {}  # 默认返回空字典

        # 初始化搜索数据
        def init_search_data(self):
            # 获取配置文件中的修改范围选项
            config_data = self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)
            modify_scope = config_data['modify_scope_options']
            forced_path_override_checkbox = config_data['forced_path_override_checkbox']  # 缓存配置文件数据

            selected_table_dict = self.get_selected_table_data(modify_scope)  # 提取成单独函数

            # 判断是否有数据
            if not selected_table_dict:
                return False

            # 查找未加载的贴图
            for MatName, textures in selected_table_dict.items():
                for TexName, Contents in textures.items():
                    tex_file_name = os.path.basename(Contents['Path'])

                    if forced_path_override_checkbox or not Contents['isLoaded']:
                        # 记录重复的贴图文件名
                        if tex_file_name in self.need_search_texture_dict:
                            self.same_path_dict.setdefault(tex_file_name, []).append([TexName, MatName])
                        else:
                            # 添加新的未加载贴图
                            self.need_search_texture_dict[tex_file_name] = [TexName, MatName, Contents['Path']]

            return True # 返回 True 表示初始化成功

        # 寻找文件夹内的所有文件
        def get_directory_contents(self):
            """
            寻找文件夹内的所有文件
            """

            path_contenes = self.getnodedata.GetDirectoryContentsWithOptions(
                self.enter_path,
                self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['search_subfolders_checkbox'],
                self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['multiple_subfolder_search_checkbox'],
                self.exclude_extensions
            )


            return path_contenes

        # 普通搜索模式
        def normal_search_mode(self, path, exclude_extensions):

            # 计算获取时间
            start_time = time.time()

            # 获取路径下内容
            path_contenes = self.getnodedata.GetDirectoryContentsWithOptions(
                path,
                self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['search_subfolders_checkbox'],
                self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['multiple_subfolder_search_checkbox'],
                exclude_extensions
            )

            # 计算获取路径内容需要多少时间
            get_path_contenes_time = time.time() - start_time
            self.feedback.CPW(f'获取路径内容时间: {get_path_contenes_time:.4f} 秒')

            # 构建 Aho-Corasick 树
            corasick_tree = self.dataP.build_ahocorapy_tree(self.need_search_texture_dict)

            # 使用 Aho-Corasick 算法搜索匹配的贴图
            matched_dict = self.dataP.search_keys_in_dict_using_ahocorapy(self.need_search_texture_dict,
                                                                          path_contenes,
                                                                          corasick_tree)

            # 查询对比的时间
            find_time = time.time() - start_time - get_path_contenes_time
            self.feedback.CPW(f'查找对比时间: {find_time:.4f} 秒')

            return matched_dict

        # 使用缓存搜索模式
        def cache_search_mode(self):
            """
            使用缓存搜索模式
            """
            # 用于存储匹配的贴图
            path_contenes = {}

            # 加载缓存数据
            path_cache_contents = self.dataM.bin_load_data(self.cache_file_path)

            # 构建 Aho-Corasick 树
            corasick_tree = self.dataP.build_ahocorapy_tree(self.need_search_texture_dict)

            # 组建搜索数据
            for tex_name in path_cache_contents:
                path_contenes[tex_name] = path_cache_contents[tex_name][2]


            # 使用 Aho-Corasick 算法搜索匹配的贴图
            matched_dict = self.dataP.search_keys_in_dict_using_ahocorapy(self.need_search_texture_dict,
                                                                          path_contenes,
                                                                          corasick_tree)

            return matched_dict

        # -----------------------------------------------智能搜索模式开始

        # 获取电脑有效盘符
        def get_drives(self):
            # 存储有效的盘符
            valid_drives = []

            # 检查从 'C:' 到 'Z:' 的所有盘符
            for letter in range(65, 91):  # 'A' 的ASCII值是65, 'Z'是90
                drive = f"{chr(letter)}:"
                # 检查该盘符是否存在
                if os.path.exists(drive):
                    valid_drives.append(drive)

            return valid_drives

        # 贪心搜索算法
        def greedy_search(self, old_path, drive_letters):
            """
            使用贪心算法生成所有可能的路径
            old_path: 原始路径
            drive_letters: 有效盘符列表
            """
            all_possibility_path = []

            # 提取文件夹路径，不包括文件名
            base_path = os.path.dirname(old_path)

            # 遍历所有可能的盘符，生成相应的基础路径
            for drive in drive_letters:
                new_base_path = drive + base_path[2:]  # 拼接新的盘符和目录路径
                new_base_path = os.path.normpath(new_base_path)  # 规范化路径
                all_possibility_path.append(new_base_path)  # 将生成的路径加入所有可能路径列表

            # 使用模糊匹配来搜索目标文件
            target_file_name = os.path.basename(old_path)  # 获取目标文件名

            possible_paths_with_scores = []

            # 遍历所有可能路径，递归地搜索目标文件
            for path in all_possibility_path:
                if os.path.exists(path):  # 如果目录存在
                    for root, dirs, files in os.walk(path):  # 使用os.walk递归遍历目录
                        # 使用difflib进行模糊匹配，找到与目标文件名最相似的文件
                        matches = difflib.get_close_matches(target_file_name, files, n=3, cutoff=0.7)
                        if matches:
                            for match in matches:
                                matched_file_path = os.path.join(root, match)  # 计算每个匹配文件的完整路径
                                score = 1  # 模拟评分，可以根据需要进行调整
                                possible_paths_with_scores.append((matched_file_path, score))

            # 根据得分排序，从高到低筛选最有可能的路径
            possible_paths_with_scores.sort(key=lambda x: x[1], reverse=True)

            # 返回得分最高的路径（最有可能的路径）
            return [path for path, score in possible_paths_with_scores]

        # 并行优化的贪心搜索方法
        def greedy_search_parallel(self, old_path, drive_letters, file_name):
            """并行优化的贪心搜索方法"""
            possible_paths = self.greedy_search(old_path, drive_letters)
            for path in possible_paths:
                if os.path.exists(path) and os.path.basename(path) == file_name:
                    return path
            return None

        # 智能搜索模式
        def intelligent_search_mode(self):
            """
            智能搜索模式
            """

            path_contenes = {}
            drive_letters = self.get_drives()

            # 使用线程池并行处理每个文件的搜索任务
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
                futures = []
                for file_name, cont in self.need_search_texture_dict.items():
                    # 提交任务到线程池
                    futures.append(
                        executor.submit(
                            self.greedy_search_parallel,  # 修改后的并行化贪心搜索方法
                            cont[2],
                            drive_letters,
                            file_name
                        )
                    )

                # 收集结果
                for future in concurrent.futures.as_completed(futures):
                    matched_path = future.result()
                    if matched_path:
                        file_name = os.path.basename(matched_path)
                        path_contenes[file_name] = matched_path

            # 构建Aho-Corasick树并搜索
            corasick_tree = self.dataP.build_ahocorapy_tree(self.need_search_texture_dict)
            matched_dict = self.dataP.search_keys_in_dict_using_ahocorapy(
                self.need_search_texture_dict,
                path_contenes,
                corasick_tree
            )

            return matched_dict

        # -----------------------------------------------智能搜索模式结束


        # 刷新正确路径的缓存
        def refresh_correct_path_cache(self, successful_matched_dict):
            """
            刷新正确路径的缓存

            correct_path_dict: dict, 匹配的正确路径字典
            """
            # 加载缓存数据
            cache_dict = self.dataM.bin_load_data(self.outer_instance.tm_repath_file_cache_filepath)

            # 更新缓存数据
            for textrue_name , cont in successful_matched_dict.items():
                cache_dict[textrue_name] = cont

            # 保存更新后的缓存数据
            self.dataM.bin_save_data(self.outer_instance.tm_repath_file_cache_filepath, cache_dict)

        # 修改匹配正确的节点路径
        def modify_correct_path(self, successful_matched_dict, same_path_dict):
            """
            修改匹配正确的节点路径

            successful_matched_dict: dict, 匹配的正确路径字典
            same_path_dict: dict, 具有相同路径的节点字典
            """

            # 执行路径修改操作
            def modify_texture_path(tex_name, correct_path):
                try:
                    cmds.setAttr(f"{tex_name}.fileTextureName", correct_path, type="string")
                except:
                    self.feedback.CPW(f'无法重命名只读节点: {tex_name}')

            # 处理匹配成功的路径字典
            for tex_name, cont in successful_matched_dict.items():
                tex_name = cont[0]
                correct_path = cont[2]
                modify_texture_path(tex_name, correct_path)

            # 处理相同路径的字典
            for tex_name, cont in same_path_dict.items():
                for tex_cont in cont:
                    tex_name = tex_cont[0]
                    correct_path = tex_cont[2]
                    modify_texture_path(tex_name, correct_path)


        # 刷新主窗口的贴图数据
        def refresh_main_window_texture_data(self, successful_matched_dict, same_path_dict):
            """
            刷新主窗口的贴图数据

            successful_matched_dict: dict, 匹配成功的贴图数据字典
            same_path_dict: dict, 具有相同路径的贴图数据字典
            """
            # 获取主窗口的表格数据
            old_table_data = self.outer_instance.TextureManagerWin.MterialNodeAllInfoDict

            # update_dict字典是为了储存接下来需要更新主数据
            update_dict = {}

            # 修改旧表格数据
            for tex_name, tex_cont in successful_matched_dict.items():
                old_table_data[tex_cont[1]][tex_cont[0]]['Path'] = tex_cont[2]  # 更新主窗口的表格数据路径
                update_dict[tex_cont[0]] = tex_cont[1]  # 记录需要更新的节点

            # 同样处理相同路径的字典
            for tex_name, tex_cont in same_path_dict.items():
                for tex_info in tex_cont:
                    old_table_data[tex_info[1]][tex_info[0]]['Path'] = tex_info[2]  # 更新主窗口的表格数据路径
                    update_dict[tex_info[0]] = tex_info[1]  # 记录需要更新的节点

            # 更新主窗口的表格数据
            new_MterialNodeAllInfoDict = self.getnodedata.TM_StickerUpdateStatusDict(update_dict,
                                                                                     old_table_data)

            # 获取零时的表格列表数据
            temp_TextureManager_texture_table_data = self.dataM.bin_load_data(
                self.outer_instance.TextureManagerWin.TextureManager_texture_table_data_temp_path)


            # 把表格中有的贴图做成的列表在总信息中筛选出来
            select_texture_dict = {
                temp_TextureManager_texture_table_data[index][0]: temp_TextureManager_texture_table_data[index][1]
                for index in range(len(temp_TextureManager_texture_table_data))}

            # 把新的MterialNodeAllInfoDict字典传递回主窗口并刷新窗口
            self.outer_instance.new_MterialNodeAllInfoDict_signal.emit(new_MterialNodeAllInfoDict, select_texture_dict)

        # 从待搜索字典中移除已搜索正确的项
        def remove_searched_correct_path(self, successful_matched_dict):
            """
            从待搜索字典中删除已成功匹配的项

            successful_matched_dict: dict，成功匹配的字典，键为已匹配的项
            """
            # 初始化新的待搜索字典
            new_need_search_texture_dict = {}

            # 遍历原待搜索字典
            for tex_file_name, tex_info in self.need_search_texture_dict.items():
                # 若当前项未匹配成功
                if tex_file_name not in successful_matched_dict:
                    # 加入新的待搜索字典
                    new_need_search_texture_dict[tex_file_name] = tex_info

            # 更新待搜索字典
            self.need_search_texture_dict = new_need_search_texture_dict

        # 把匹配好内容更新到相同路径的字典并返回新的字典
        def update_same_path_dict(self, successful_matched_dict):
            """
            把匹配好内容更新到相同路径的字典并返回新的字典

            successful_matched_dict: dict, 匹配成功的字典
            """

            # 遍历原相同路径字典
            for tex_file_name, tex_info in self.same_path_dict.items():
                path = successful_matched_dict[tex_file_name][2]
                for index, tex_info_entry  in enumerate(tex_info):
                    self.same_path_dict[tex_file_name][index].append(path)

            return self.same_path_dict

        # 主要逻辑函数
        def process(self):
            # 用于存储匹配成功的贴图
            successful_matched_dict = {}



            # 1, 初始化搜索数据
            if not self.init_search_data():
                return

            # 2, 判断有没有搜索模式
            # 获取几种模式
            use_cache_checkbox = self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['use_cache_checkbox']
            intelligent_search_mode = self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['intelligent_search_mode']
            normal_search_mode = self.dataM.bin_load_data(self.outer_instance.TM_repath_files_config_FilePath)['normal_search_mode']

            if not use_cache_checkbox and not intelligent_search_mode and not normal_search_mode:
                self.feedback.CPW('没有选择搜索模式')
                return

            # 3, 判断运行模式
            if use_cache_checkbox:
                print('缓存搜索模式')
                # 缓存搜索模式
                cache_successful_matched_dict = self.cache_search_mode()

                self.remove_searched_correct_path(cache_successful_matched_dict)

                # 把搜索正确的内容添加进正确内容更新字典
                successful_matched_dict.update(cache_successful_matched_dict)

            if intelligent_search_mode:
                # 智能搜索模式
                print('智能搜索模式')

                intelligent_successful_matched_dict =  self.intelligent_search_mode()

                # 把搜索正确的内容添加进正确内容更新字典
                successful_matched_dict.update(intelligent_successful_matched_dict)



            if normal_search_mode:
                # 判断路径是否有问题
                if not os.path.exists(self.enter_path):
                    self.feedback.CPW('输入的路径不存在')
                    return

                # 普通搜索模式
                print('普通搜索模式')

                # 寻找文件夹内的所有文件
                normal_successful_matched_dict = self.normal_search_mode(self.enter_path, self.exclude_extensions)

                # 把搜索正确的内容添加进正确内容更新字典
                successful_matched_dict.update(normal_successful_matched_dict)

            same_path_dict = self.update_same_path_dict(successful_matched_dict)

            # 刷新正确路径的缓存
            self.refresh_correct_path_cache(successful_matched_dict)

            # 修改匹配正确的节点路径
            self.modify_correct_path(successful_matched_dict, same_path_dict)

            # 刷新主窗口的贴图数据
            self.refresh_main_window_texture_data(successful_matched_dict, same_path_dict)

    # 寻找文件夹并修复确实文件夹主要逻辑函数
    def fix_path(self):

        # 排除的格式列表（用来筛选特定文件）
        exclude_extensions = ['.jpg', '.jpeg', '.png', '.bmp',
                              '.tiff', '.tif','.raw','.tga',
                              '.exr' ,'.hdr']


        fix_path_processor = self.FixPath(self, exclude_extensions)
        fix_path_processor.process()


    # 测试函数
    def test(self):
        pass



    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)

        config[key] = cont

        self.dataM.bin_save_data(self.TM_repath_files_config_FilePath, config)
    # --------------------保存设置内容的函数

#______________________________________________________________________________>>>贴图管理器的图像处理界面 支持转换格式和压缩图像
class TM_ImageProcessing(QtWidgets.QDialog):

    new_MterialNodeAllInfoDict_signal = Signal(dict, dict)

    def __init__(self, WinName = '', parent=None):
        super(TM_ImageProcessing, self).__init__(parent)

        self.TextureManagerWin = parent  # 保存主窗口的引用

        # 0. 初始化全局配置
        self.initial_global_config()

        # 1. 初始化窗口配置
        self.initialize_window_config(WinName)

        # 2. 创建菜单
        self.menu_widgets()

        # 3. 创建控件
        self.create_widgets()

        # 4. 创建布局
        self.create_layouts()

        # 5. 初始化控件
        self.initial_widgets_settings()

    # 初始化窗口配置
    def initialize_window_config(self, WinName):
        # 命名常量命名
        WINDOWS_NAME =  self.lang['initialize_window_config']['WINDOWS_NAME'] + WinName #Win名称

        delete_window_if_existe('TM_ImageProcessing_Win')

        self.setObjectName('TM_ImageProcessing_Win')
        self.setWindowTitle(WINDOWS_NAME)

        #...窗口长宽
        self.setMinimumHeight(200)
        self.setMinimumWidth(650)

    def initial_global_config(self):

        # 实例数据管理器
        self.dataM = DataManager() # 数据管理
        self.dataP = DataProcessor() # 数据处理
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData() # 获取节点数据模块
        self.imageP = ImageProcessor() # 处理图像

        # 基础缓存数据变量空字典
        image_processing_cache_dict = {}


        # TM_ImageProcessing配置文件路径
        self.TM_image_processing_config_FilePath = os.path.join(script_path, "Datas", "texture_manager",
                                                            "TM_image_processing_config.bin")

        # 如果TM_image_processing_config配置文件不存在会重新创建一次
        if not os.path.exists(self.TM_image_processing_config_FilePath):
            self.dataM.bin_save_data(self.TM_image_processing_config_FilePath, TM_ImageProcessing_config_dict)



        # TM_ImageProcessing的缓存文件路径
        self.TM_image_processing_cache_FilePath = os.path.join(script_path, "Datas", "texture_manager",
                                                            "TM_image_processing_cache.bin")

        # 如果TM_image_processing_cache缓存文件不存在会重新创建一次
        if not os.path.exists(self.TM_image_processing_cache_FilePath):
            self.dataM.bin_save_data(self.TM_image_processing_cache_FilePath, image_processing_cache_dict)

        self.lang = language_loading()['ArnoldMagicNode']['TM_IP_WIN']

    def menu_widgets(self):
        # 获取到相应函数的语言
        menu_lang = self.lang['menu_widgets']

        # 创建菜单栏
        self.menu_bar = QtWidgets.QMenuBar(self)

        # 创建“编辑”菜单
        self.edit_menu = self.menu_bar.addMenu(menu_lang['edit_menu']) # 编辑

        self.clear_cache = QAction(menu_lang['clear_cache'], self) # 清除缓存  ！谨慎删除！
        self.clear_cache.triggered.connect(lambda *args: os.remove(self.TM_image_processing_cache_FilePath))

        self.redo_action = QAction(menu_lang['redo_action'], self) # 还原图像

        self.edit_menu.addAction(self.clear_cache)
        self.edit_menu.addAction(self.redo_action)



        self.help_menu = self.menu_bar.addMenu(menu_lang['help_menu']) # 帮助

        self.instructions_action = QAction(menu_lang['instructions_action'], self) # 使用说明
        self.help_menu.addAction(self.instructions_action)

    def create_widgets(self):

        # 获取到相应函数的语言
        widgets_lang = self.lang['create_widgets']

        common_font = QtGui.QFont()
        common_font.setPointSize(SMALL_FONT_SIZE)




        self.format_combo_box_label = QtWidgets.QLabel(widgets_lang['format_combo_box_label']) # 格式

        format_list = ['jpg', 'png', 'tif', 'bmp']
        self.format_combo_box = QtWidgets.QComboBox()
        self.format_combo_box.addItems(format_list)  # 添加选项
        self.format_combo_box.currentTextChanged.connect(lambda *args: (
            self.modify_config('format', self.format_combo_box.currentText()), # 存入数据
            self.update_quality_controls_visibility()))


        # 创建一个显示输入结果的 QLabel
        self.zoom_ratios_combo_box_label = QtWidgets.QLabel(widgets_lang['zoom_ratios_combo_box_label']) # 缩放

        # 创建可编辑的 QComboBox
        self.zoom_ratios_combo_box = QtWidgets.QComboBox()
        self.zoom_ratios_combo_box.setEditable(True)  # 设置为可编辑状态
        self.zoom_ratios_combo_box.addItems(["10%", "25%", "33%", "50%", "75%", "85%", "100%"])  # 添加选项

        # 设置 zoom_ratios_combo_box 的参数
        self.zoom_ratios_combo_box.setFixedWidth(100)

        # 绑定 currentTextChanged 信号到自定义的函数
        self.zoom_ratios_combo_box.currentTextChanged.connect(lambda *args: (
            self.modify_config('zoom', self.zoom_ratios_combo_box.currentText().replace('%', ''))))

        # 获取 QComboBox 内部的 QLineEdit
        self.zoom_ratios_line_edit = self.zoom_ratios_combo_box.lineEdit()

        # 当编辑结束时，连接信号到槽函数
        self.zoom_ratios_line_edit.editingFinished.connect(lambda *args: self.update_zoom_ratios_string())

        # 创建一个显示输入结果的 QLabel
        self.resampling_mode_combo_box_label = QtWidgets.QLabel(widgets_lang['resampling_mode_combo_box_label']) # 重新取样

        # 重采样的模式
        resampling_mode_list = widgets_lang['resampling_mode_list'] # '最近邻插值', '双线性插值', '三次插值', 'Lanczos 插值', '区域插值', '填充插值外点', '逆映射插值'
        self.resampling_combo_box = QtWidgets.QComboBox()
        self.resampling_combo_box.addItems(resampling_mode_list)  # 添加选项
        self.resampling_combo_box.currentTextChanged.connect(lambda *args: self.modify_config(
            'resampling_mode', self.resampling_combo_box.currentIndex()))

        self.jpg_label = QtWidgets.QLabel(widgets_lang['jpg_label']) # JPG的品质

        # jpg的参数设置面板
        self.jpg_quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        # jpg_quality_slider控件的设置
        # 设置最小值为0，最大值为100，步长为5
        self.jpg_quality_slider.setMinimum(0)
        self.jpg_quality_slider.setMaximum(100)
        self.jpg_quality_slider.setTickInterval(5)  # 设置刻度间隔为5
        self.jpg_quality_slider.setSingleStep(5)  # 设置滑动步长为5
        self.jpg_quality_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)  # 设置刻度显示在滑杆下方
        self.jpg_quality_slider.setFixedHeight(25)
        self.jpg_quality_slider.setFixedWidth(400)

        self.jpg_quality_slider.valueChanged.connect(lambda *args:  (
            self.update_quality_display_label(),
            self.modify_config('JPG_quality', self.jpg_quality_slider.value())))

        self.jpg_quality_display_label = QtWidgets.QLabel()


        self.png_label = QtWidgets.QLabel(widgets_lang['png_label']) # PNG的品质

        # jpg的参数设置面板
        self.png_quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        # png_quality_slider控件的设置
        # 设置最小值为0，最大值为100，步长为5
        self.png_quality_slider.setMinimum(0)
        self.png_quality_slider.setMaximum(9)
        self.png_quality_slider.setTickInterval(1)  # 设置刻度间隔为5
        self.png_quality_slider.setSingleStep(1)  # 设置滑动步长为5
        self.png_quality_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)  # 设置刻度显示在滑杆下方
        self.png_quality_slider.setFixedHeight(25)
        self.png_quality_slider.setFixedWidth(400)

        self.png_quality_slider.valueChanged.connect(lambda *args: (
            self.update_quality_display_label(),
            self.modify_config('PNG_quality', self.png_quality_slider.value())))

        self.png_quality_display_label = QtWidgets.QLabel()

        self.modify_group = QtWidgets.QButtonGroup(self)
        self.radio_all = QtWidgets.QRadioButton('全部')  # '全部'选项
        self.radio_table = QtWidgets.QRadioButton('表格内')  # '表格内'选项
        self.radio_selection = QtWidgets.QRadioButton('选择中')  # '选择中'选项
        self.modify_group.addButton(self.radio_all, 1)  # 将按钮加入组
        self.modify_group.addButton(self.radio_table, 2)
        self.modify_group.addButton(self.radio_selection, 3)

        # 当选择变化时，更新配置文件中的选项
        self.modify_group.buttonClicked.connect(
            lambda button: self.modify_config('modify_scope_options', self.modify_group.id(button)))

        self.convert_format_check_box = QtWidgets.QCheckBox(widgets_lang['convert_format_check_box']) # 转换格式
        self.convert_format_check_box.clicked.connect(
            lambda *args: self.modify_config('convert_format', self.convert_format_check_box.isChecked()))

        self.scale_texture_check_box = QtWidgets.QCheckBox(widgets_lang['scale_texture_check_box']) # 缩放贴图
        self.scale_texture_check_box.clicked.connect(
            lambda *args:  self.modify_config('scale_texture', self.scale_texture_check_box.isChecked()))



        self.conversion_button = QtWidgets.QPushButton(widgets_lang['conversion_button']) # 开始转换
        self.conversion_button.clicked.connect(lambda *args: self.image_conversion())

    def create_layouts(self):
        # 第一层的多选格式的控件布局
        combo_layout = QtWidgets.QHBoxLayout()

        # 添加标签和控件，无需过多的 Spacer
        combo_layout.addStretch()  # 在开头加入可伸缩的空白
        combo_layout.addWidget(self.format_combo_box_label)
        combo_layout.addWidget(self.format_combo_box)
        combo_layout.addStretch()  # 控制空白区域
        combo_layout.addWidget(self.zoom_ratios_combo_box_label)
        combo_layout.addWidget(self.zoom_ratios_combo_box)
        combo_layout.addStretch()  # 控制空白区域
        combo_layout.addWidget(self.resampling_mode_combo_box_label)
        combo_layout.addWidget(self.resampling_combo_box)
        combo_layout.addStretch()  # 在末尾加入可伸缩的空白

        # JPG配置布局
        jpg_config_layout = QtWidgets.QHBoxLayout()
        jpg_config_layout.addStretch()  # 控制空白区域
        jpg_config_layout.addWidget(self.jpg_label)
        jpg_config_layout.addStretch()  # 控制空白区域
        jpg_config_layout.addWidget(self.jpg_quality_slider)
        jpg_config_layout.addStretch()  # 控制空白区域
        jpg_config_layout.addWidget(self.jpg_quality_display_label)
        jpg_config_layout.addStretch()  # 控制空白区域

        # PNG配置布局
        png_config_layout = QtWidgets.QHBoxLayout()
        png_config_layout.addStretch()  # 控制空白区域
        png_config_layout.addWidget(self.png_label)
        png_config_layout.addStretch()  # 控制空白区域
        png_config_layout.addWidget(self.png_quality_slider)
        png_config_layout.addStretch()  # 控制空白区域
        png_config_layout.addWidget(self.png_quality_display_label)
        png_config_layout.addStretch()  # 控制空白区域

        selection_layout = QtWidgets.QHBoxLayout()
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_all)
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_table)
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_selection)
        selection_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))


        radio_button = QtWidgets.QHBoxLayout()
        radio_button.addStretch()
        radio_button.addWidget(self.convert_format_check_box)
        radio_button.addStretch()
        radio_button.addWidget(self.scale_texture_check_box)
        radio_button.addStretch()

        conversion_layout = QtWidgets.QHBoxLayout()
        conversion_layout.addWidget(self.conversion_button)

        Main_Layout = QtWidgets.QVBoxLayout()
        Main_Layout.setMenuBar(self.menu_bar)
        Main_Layout.addLayout(combo_layout)
        Main_Layout.addStretch()  # 控制空白区域
        Main_Layout.addLayout(jpg_config_layout)
        Main_Layout.addLayout(png_config_layout)
        Main_Layout.addStretch()
        Main_Layout.addLayout(selection_layout)
        Main_Layout.addLayout(radio_button)
        Main_Layout.addLayout(conversion_layout)


        # 设置窗口的主布局
        self.setLayout(Main_Layout)

    def initial_widgets_settings(self):
        initial_config = self.dataM.bin_load_data(self.TM_image_processing_config_FilePath)

        # 设置 select_group 的默认选中按钮（通过 ID）
        modify_group_button = self.modify_group.button(initial_config['modify_scope_options'])
        if modify_group_button:
            modify_group_button.setChecked(True)  # 设置该按钮为选中状态

        # 设置质量标签的初始值
        self.jpg_quality_display_label.setText(str(initial_config['JPG_quality']))
        self.png_quality_display_label.setText(str(initial_config['PNG_quality']))
        # 设置控件的初始值
        self.format_combo_box.setCurrentText(initial_config['format'])
        self.zoom_ratios_combo_box.setCurrentText(self.ensure_single_percent(initial_config['zoom']))
        self.resampling_combo_box.setCurrentIndex(initial_config['resampling_mode'])
        self.jpg_quality_slider.setValue(initial_config['JPG_quality'])
        self.png_quality_slider.setValue(initial_config['PNG_quality'])
        self.convert_format_check_box.setChecked(initial_config['convert_format'])
        self.scale_texture_check_box.setChecked(initial_config['scale_texture'])

        self.update_quality_controls_visibility()
        self.update_quality_display_label()

    # 更新jpg和png之间切换的控件显示模式
    def update_quality_controls_visibility(self):
        """
        根据初始配置隐藏不需要的品质设置控件。

        - 如果格式为 'jpg'，则隐藏 PNG 的品质设置控件。
        - 如果格式为 'png'，则隐藏 JPG 的品质设置控件。
        - 如果是其他格式，则隐藏所有与品质相关的控件。
        """

        def hide_jpg_controls(hide=True):
            """设置 JPG 相关控件的可见性"""
            self.jpg_label.setVisible(not hide)
            self.jpg_quality_slider.setVisible(not hide)
            self.jpg_quality_display_label.setVisible(not hide)

        def hide_png_controls(hide=True):
            """设置 PNG 相关控件的可见性"""
            self.png_label.setVisible(not hide)
            self.png_quality_slider.setVisible(not hide)
            self.png_quality_display_label.setVisible(not hide)

        initial_config = self.dataM.bin_load_data(self.TM_image_processing_config_FilePath)
        current_format = initial_config.get('format', '')

        # 根据当前格式隐藏或显示相关的控件
        if current_format == 'jpg':
            hide_jpg_controls(False)  # 显示 JPG 相关控件
            hide_png_controls(True)  # 隐藏 PNG 相关控件
        elif current_format == 'png':
            hide_jpg_controls(True)  # 隐藏 JPG 相关控件
            hide_png_controls(False)  # 显示 PNG 相关控件
        else:
            hide_jpg_controls(True)  # 隐藏所有品质相关控件
            hide_png_controls(True)

    # 更新质量显示的标签
    def update_quality_display_label(self):
        self.jpg_quality_display_label.setText(
            str(self.jpg_quality_slider.value()) + '%'
        )
        self.png_quality_display_label.setText(
            str(self.png_quality_slider.value()) + ' 级'
        )

    # 更新zoom_ratios的字符串，具体是强制加入%
    def update_zoom_ratios_string(self):
        new_text = (self.ensure_single_percent(self.zoom_ratios_combo_box.currentText()))
        self.zoom_ratios_combo_box.setCurrentText(new_text)

    # 处理字符串%号
    def ensure_single_percent(self, s):
        # 去掉字符串两端的空格
        s = s.strip()

        # 检查字符串中是否包含 %
        if '%' in s:
            # 如果有多个 %，将连续的 % 替换为一个 %
            s = '%'.join(part for part in s.split('%') if part) + '%'
        else:
            # 如果没有 %，在字符串末尾加上 %
            s += '%'

        return s

    # 获取表格中选中的行
    def get_selected_rows_data(self):
        # 获取表格中选中的行
        selected_indexes = self.TextureManagerWin.TexturelList.selectionModel().selectedRows()

        # 如果没有选中任何行，提前返回
        if not selected_indexes:
            self.feedback.CPW(self.lang['get_selected_rows_data']['01']) # 没有选中任何行
            return []

        # 使用列表推导式获取所有选中行的数据
        all_selected_rows_data = [
            [self.TextureManagerWin.TEXTURELIST_MODEL.index(index.row(), column).data()
             for column in range(self.TextureManagerWin.TEXTURELIST_MODEL.columnCount())]
            for index in selected_indexes
        ]

        return all_selected_rows_data

    # 给文件名称结尾添加后缀名称
    def add_suffix_to_filename(self, file_path, suffix):
        # 获取文件名和扩展名
        file_name, file_ext = os.path.splitext(file_path)

        # 检查文件名是否已有指定后缀
        if file_name.endswith(suffix):
            return file_path
        else:
            # 如果没有后缀，添加后缀
            new_file_name = file_name + suffix + file_ext
            return new_file_name

    # 检测并复制文件带后缀
    def copy_file_with_suffix(self, old_info_path, new_file_path):

        # 检查带后缀的文件是否存在
        if os.path.exists(new_file_path):
            return
        else:
            try:
                # 如果不存在，复制原始文件并命名为带后缀的文件，不复制权限
                shutil.copyfile(old_info_path, new_file_path)

                return
            except Exception as e:
                self.feedback.CPW(self.lang['copy_file_with_suffix']['01']) # 复制备份文件时出错

                return

    # 修改文件命格式
    def modify_file_extension(self, file_path, new_extension):
        # 获取文件名和目录
        directory, file_name = os.path.split(file_path)
        # 修改文件扩展名
        new_file_name = os.path.splitext(file_name)[0] + '.' + new_extension
        # 返回新的完整路径
        return os.path.join(directory, new_file_name)


    class ImageProcessing:
        def __init__(self, outer_instance):

            # 实例数据管理器
            self.dataM = DataManager()  # 数据管理
            self.dataP = DataProcessor()  # 数据处理
            self.feedback = FeedbackPrompt()  # 错误提示模块
            self.getnodedata = GetNodeData()  # 获取节点数据模块
            self.imageP = ImageProcessor()  # 处理图像


            # 配置文件
            self.config = self.dataM.bin_load_data(outer_instance.TM_image_processing_config_FilePath)
            self.congig_path = outer_instance.TM_image_processing_config_FilePath
            self.outer_instance = outer_instance  # 存储对外部类实例的引用

            self.old_material_node_all_info_dict = self.outer_instance.TextureManagerWin.MterialNodeAllInfoDict



            # 图像处理后的后缀名称
            self.image_processed_suffix = self.config['processed_suffix']

            # 输出格式与扩展名映射
            self.format_mapping = {
                'jpg': 'jpg',
                'jpeg': 'jpg',
                'png': 'png',
                'tif': 'tiff',
                'bmp': 'bmp',
            }

        def _find_udim_textures(self, filepath):
            """
            根据给定的贴图文件路径，查找同一目录下所有同名且带有 UDIM 编号的文件。
            参数:
                filepath (str): 带有 UDIM 编号的贴图文件路径，例如 "C:\\path\\to\\texture.1001.jpeg"
            返回:
                list: 同一目录下所有匹配的 UDIM 贴图文件名列表，例如 ["texture.1002.jpeg", "texture.1003.jpeg"]
            """
            directory = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            # 使用正则表达式解析文件名，提取基名、UDIM 编号和扩展名
            # 例如，"Helmet_emissive.1001.jpeg" 中 base="Helmet_emissive", udim="1001", ext="jpeg"
            udim_pattern = re.compile(r'^(?P<base>.+)\.(?P<udim>\d{4})\.(?P<ext>[^.]+)$')
            match = udim_pattern.match(filename)

        def _parse_udim_filename(self, filename):
            """
            UDIM文件名解析函数
            格式规范：文件名.<UDIM编号>.<扩展名>
            UDIM要求：4位数字，范围1001-9999（Maya官方规范）

            :param filename: 完整文件名(需包含扩展名)
            :return: 解析结果字典
            """
            # 分离基础名称和扩展名
            base_name, file_ext = os.path.splitext(filename)
            parts = base_name.split('.')

            # UDIM正则检测（严格模式）
            udim_pattern = r'^(1\d{3}|[2-9]\d{3})$'  # 1001-9999

            # 反向遍历寻找UDIM编号
            for i in reversed(range(len(parts))):
                if re.match(udim_pattern, parts[i]):
                    # 分离名称部分和UDIM编号
                    udim_id = parts[i]
                    name_part = '.'.join(parts[:i])
                    return {
                        'is_udim': True,
                        'file_name': name_part,
                        'udim_id': udim_id,
                        'extension': file_ext.lower().lstrip('.')
                    }

            # 未找到符合UDIM编号的情况
            return {
                'is_udim': False,
                'file_name': base_name,
                'extension': file_ext.lower().lstrip('.')
            }

        def _find_similar_filenames(self, dirList, keyword, excludeFormats):
            """
            查找与关键字相似（文件名中包含关键字），
            并且排除掉指定格式的文件名。

            参数：
                dirList (list[str]): 文件名或路径的列表
                keyword (str): 搜索关键词
                excludeFormats (list[str]): 需要排除的格式列表，例如 ["jpg", "png"] 等

            返回：
                list[str]: 返回符合要求的关键字匹配且未被排除格式过滤掉的文件名列表
            """
            result = []
            for file_name in dirList:
                # 提取文件扩展名
                ext = file_name.split('.')[-1].lower()

                # 如果文件后缀在排除列表中，跳过
                if ext in excludeFormats:
                    continue

                # 如果文件名中包含关键词，加入结果列表
                if keyword.lower() in file_name.lower():
                    result.append(file_name)

            return result

        def _find_udim_textures(self, filepath):
            """
            根据给定的贴图文件路径，查找同一目录下所有同名且带有 UDIM 编号的文件。
            参数:
                filepath (str): 带有 UDIM 编号的贴图文件路径，例如 "C:\\path\\to\\texture.1001.jpeg"
            返回:
                list: 同一目录下所有匹配的 UDIM 贴图文件名列表，例如 ["texture.1002.jpeg", "texture.1003.jpeg"]
            """
            directory = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            # 使用正则表达式解析文件名，提取基名、UDIM 编号和扩展名
            # 例如，"Helmet_emissive.1001.jpeg" 中 base="Helmet_emissive", udim="1001", ext="jpeg"
            udim_pattern = re.compile(r'^(?P<base>.+)\.(?P<udim>\d{4})\.(?P<ext>[^.]+)$')
            match = udim_pattern.match(filename)

            if not match:
                print(f"输入文件名 '{filename}' 不符合 UDIM 命名约定。")
                return []
            base = match.group('base')
            ext = match.group('ext')
            # 构建用于匹配的正则表达式
            search_pattern = re.compile(rf'^{re.escape(base)}\.(\d{{4}})\.{re.escape(ext)}$')
            # 列出目录中所有文件
            try:
                all_files = os.listdir(directory)
            except FileNotFoundError:
                print(f"目录 '{directory}' 不存在。")
                return []
            except PermissionError:
                print(f"没有权限访问目录 '{directory}'。")
                return []
            # 筛选出匹配的 UDIM 文件（除了输入文件本身）
            udim_files = [
                f for f in all_files
                if search_pattern.match(f) and os.path.isfile(os.path.join(directory, f)) and f != filename
            ]
            return udim_files

        def _udim_file_process(self, texture_path, old_file_info):
            # 寻找其他的udim文件
            udim_files = self._find_udim_textures(texture_path)

            dir_path = os.path.dirname(texture_path)


            for udim_file in udim_files:



                    # 构建完整的文件路径
                    udim_file_path = os.path.join(dir_path, udim_file)


                    # 2，如果路径不存在会直接跳过这个循环
                    if not os.path.exists(udim_file_path):
                        self.feedback.CP(self.lang['image_conversion']['01'] + udim_file_path) # 你的这张图片路径连接失败
                        continue  # 如果路径不存在，跳过这个循环



                    # 分离文件名和扩展名 如果是UDIM文件名则会返回一个字典
                    old_file_info = self._parse_udim_filename(udim_file)

                    # 获取源文件的路径
                    if self.image_processed_suffix in old_file_info['file_name']:
                        # 步骤 1：从文件名中删除处理后缀（例如 "_TMProc"）
                        delete_suffix_name = old_file_info['file_name'].replace(self.image_processed_suffix, '')

                        # 步骤 2：列出旧文件所在目录中的所有文件
                        files_in_directory = os.listdir(dir_path)

                        if old_file_info['is_udim']:
                            # UDIM 文件处理分支
                            # 筛选条件：
                            # 1. 文件名包含删除后缀后的基础名（例如 "Helmet_roughness"）
                            # 2. 不包含处理后缀（避免重复处理）
                            # 3. 正则匹配 UDIM ID（例如 .1001.）
                            source_file_name = [
                                filename for filename in files_in_directory
                                if (
                                        delete_suffix_name in filename and
                                        self.config['processed_suffix'] not in filename and
                                        re.search(rf'\.{old_file_info["udim_id"]}\.', filename)
                                )
                            ]

                            # 取第一个匹配的文件名构建完整路径
                            source_file_path = os.path.join(dir_path, source_file_name[0])
                        else:
                            # 非 UDIM 文件处理分支
                            # 筛选条件：
                            # 1. 文件名包含基础名
                            # 2. 不包含处理后缀
                            source_file_name = [
                                filename for filename in files_in_directory
                                if delete_suffix_name in filename and
                                   self.config['processed_suffix'] not in filename
                            ]
                            source_file_path = os.path.join(dir_path, source_file_name)

                    else:
                        # 如果原始文件名不包含处理后缀，直接使用旧路径
                        source_file_path = udim_file_path



                    # 构建备份文件路径
                    if old_file_info['is_udim']:
                        # UDIM 备份路径格式：基础名 + 处理后缀 + UDIM ID + 扩展名
                        # 示例：Helmet_roughness_TMProc.1001.jpeg
                        backup_image_file_path = os.path.join(
                            dir_path,
                            old_file_info['file_name'].replace(self.image_processed_suffix, '')  # 删除旧后缀
                            + self.image_processed_suffix  # 重新添加后缀（可能需验证逻辑）
                            + '.' + old_file_info['udim_id']  # 插入 UDIM ID
                            + '.' + old_file_info['extension']  # 文件扩展名
                        )
                    else:
                        # 非 UDIM 备份路径格式：基础名 + 处理后缀 + 扩展名
                        # 示例：Helmet_roughness_TMProc.jpeg
                        backup_image_file_path = os.path.join(
                            dir_path,
                            old_file_info['file_name'].replace(self.image_processed_suffix, '')  # 删除旧后缀
                            + self.image_processed_suffix  # 重新添加后缀
                            + '.' + old_file_info['extension']  # 文件扩展名
                        )

                    # 检查是否需要转换格式
                    if self.config['convert_format']:
                        # 根据输出格式生成输出路径
                        if self.config['format'] in self.format_mapping:
                            # 通过分割文件名，去掉原文件扩展名，并添加新的扩展名
                            convert_format_backup_image_name = f"{backup_image_file_path.rsplit('.', 1)[0]}.{self.format_mapping[self.config['format']]}"
                            backup_image_file_path = convert_format_backup_image_name

                        else:
                            # 如果格式不被支持，输出反馈信息并返回
                            self.feedback.CP(f"{self.lang['image_conversion']['02']} {self.config['format']}")  # 不支持的格式

                        # 执行格式转换，使用备份图像文件名作为输入和输出路径
                        convert_image_format_state = self.imageP.convert_image_format(input_path=source_file_path,
                                                                                      output_path=convert_format_backup_image_name,
                                                                                      output_format=self.format_mapping[
                                                                                          self.config['format']],
                                                                                      jpg_quality=self.config['JPG_quality'],
                                                                                      png_compression=self.config[
                                                                                          'PNG_quality'])

                        # 如果图片处理返回False直接退出循环
                        if convert_image_format_state == False:
                            return

                        dirlist = os.listdir(dir_path)
                        # 删除相同名称的其他格式文件
                        self.outer_instance.delete_other_formats(dir_path, dirlist,
                                                                 os.path.basename(backup_image_file_path),
                                                                 self.format_mapping[self.config['format']])

                        # 如果需要缩放，则在转换格式后进行缩放
                        if self.config['scale_texture']:
                            resize_image_state = self.imageP.resize_image(input_path=convert_format_backup_image_name,
                                                                          output_path=convert_format_backup_image_name,
                                                                          scale_percent=int(self.config['zoom']),
                                                                          resample_mode=str(self.config['resampling_mode']))
                            if resize_image_state == False:
                                continue

                    # 如果没有进行格式转换，但需要缩放，则直接缩放
                    elif self.config['scale_texture']:
                        resize_image_state = self.imageP.resize_image(input_path=source_file_path,
                                                                      output_path=backup_image_file_path,
                                                                      scale_percent=int(self.config['zoom']),
                                                                      resample_mode=str(self.config['resampling_mode']))

                        # 如果图片处理返回False直接退出循环
                        if resize_image_state == False:
                            continue

        def process(self):
            # 0,创建一个空的字典用来存储处理后的贴图
            need_update_dict = {}


            # 1, 如果没有勾选转换格式和缩放比例那不会有任何操作，会直接退出函数
            if not self.config.get('convert_format', False) and not self.config.get('scale_texture', False):
                return  # 如果两者都是 False，直接 return

            # 2, 获取选中的行数据
            select_data = self.outer_instance.TextureManagerWin.get_selected_table_data(
                self.config['modify_scope_options'])

            # 3, 如果没有选中任何行，提前返回
            if select_data == {} or select_data == {'lambert1': {}, 'standardSurface1': {}, 'Unlisted Textures': {}}:
                self.feedback.CPW("没有选中任何内容")
                return  # 如果没有选中任何行，提前返回


            # 4，对选择的内容遍历
            for material_name, texture_data in list(select_data.items()):
                for texture_name, texture_info in list(texture_data.items()):
                    # 1,  获取旧路径并标准化路径
                    old_path = os.path.normpath(texture_info['Path'])

                    # 2，如果路径不存在会直接跳过这个循环
                    if not os.path.exists(old_path):
                        self.feedback.CP(self.lang['image_conversion']['01'] + old_path) # 你的这张图片路径连接失败
                        continue  # 如果路径不存在，跳过这个循环

                    # 分离文件路径和文件名
                    old_file_dir, old_file_name = os.path.split(old_path)

                    # 分离文件名和扩展名 如果是UDIM文件名则会返回一个字典
                    old_file_info = self._parse_udim_filename(old_file_name)

                    # 获取源文件的路径
                    if self.image_processed_suffix in old_file_info['file_name']:
                        # 步骤 1：从文件名中删除处理后缀（例如 "_TMProc"）
                        delete_suffix_name = old_file_info['file_name'].replace(self.image_processed_suffix, '')

                        # 步骤 2：列出旧文件所在目录中的所有文件
                        files_in_directory = os.listdir(old_file_dir)

                        if old_file_info['is_udim']:
                            # UDIM 文件处理分支
                            # 筛选条件：
                            # 1. 文件名包含删除后缀后的基础名（例如 "Helmet_roughness"）
                            # 2. 不包含处理后缀（避免重复处理）
                            # 3. 正则匹配 UDIM ID（例如 .1001.）
                            source_file_name = [
                                filename for filename in files_in_directory
                                if (
                                        delete_suffix_name in filename and
                                        self.config['processed_suffix'] not in filename and
                                        re.search(rf'\.{old_file_info["udim_id"]}\.', filename)
                                )
                            ]

                            # 取第一个匹配的文件名构建完整路径
                            source_file_path = os.path.join(old_file_dir, source_file_name[0])
                        else:
                            # 非 UDIM 文件处理分支
                            # 筛选条件：
                            # 1. 文件名包含基础名
                            # 2. 不包含处理后缀
                            source_file_name = [
                                filename for filename in files_in_directory
                                if delete_suffix_name in filename and
                                   self.config['processed_suffix'] not in filename
                            ]
                            source_file_path = os.path.join(old_file_dir, source_file_name)

                    else:
                        # 如果原始文件名不包含处理后缀，直接使用旧路径
                        source_file_path = old_path


                    # 构建备份文件路径
                    if old_file_info['is_udim']:
                        # UDIM 备份路径格式：基础名 + 处理后缀 + UDIM ID + 扩展名
                        # 示例：Helmet_roughness_TMProc.1001.jpeg
                        backup_image_file_path = os.path.join(
                            old_file_dir,
                            old_file_info['file_name'].replace(self.image_processed_suffix, '')  # 删除旧后缀
                            + self.image_processed_suffix  # 重新添加后缀（可能需验证逻辑）
                            + '.' + old_file_info['udim_id']  # 插入 UDIM ID
                            + '.' + old_file_info['extension']  # 文件扩展名
                        )
                    else:
                        # 非 UDIM 备份路径格式：基础名 + 处理后缀 + 扩展名
                        # 示例：Helmet_roughness_TMProc.jpeg
                        backup_image_file_path = os.path.join(
                            old_file_dir,
                            old_file_info['file_name'].replace(self.image_processed_suffix, '')  # 删除旧后缀
                            + self.image_processed_suffix  # 重新添加后缀
                            + '.' + old_file_info['extension']  # 文件扩展名
                        )

                    # 检查是否需要转换格式
                    if self.config['convert_format']:
                        # 根据输出格式生成输出路径
                        if self.config['format'] in self.format_mapping:
                            # 通过分割文件名，去掉原文件扩展名，并添加新的扩展名
                            convert_format_backup_image_name = f"{backup_image_file_path.rsplit('.', 1)[0]}.{self.format_mapping[self.config['format']]}"
                            backup_image_file_path = convert_format_backup_image_name

                        else:
                            # 如果格式不被支持，输出反馈信息并返回
                            self.feedback.CP(f"{self.lang['image_conversion']['02']} {self.config['format']}") # 不支持的格式



                        # 执行格式转换，使用备份图像文件名作为输入和输出路径
                        convert_image_format_state = self.imageP.convert_image_format(input_path=source_file_path,
                                                                                     output_path=convert_format_backup_image_name,
                                                                                     output_format=self.format_mapping[self.config['format']],
                                                                                     jpg_quality=self.config['JPG_quality'],
                                                                                     png_compression=self.config['PNG_quality'])

                        # 如果图片处理返回False直接退出循环
                        if convert_image_format_state == False:
                            return


                        dirlist = os.listdir(old_file_dir)
                        # 删除相同名称的其他格式文件
                        self.outer_instance.delete_other_formats(old_file_dir, dirlist,
                                                  os.path.basename(backup_image_file_path),
                                                  self.format_mapping[self.config['format']])

                        # 如果需要缩放，则在转换格式后进行缩放
                        if self.config['scale_texture']:
                            resize_image_state = self.imageP.resize_image(input_path=convert_format_backup_image_name,
                                                                         output_path=convert_format_backup_image_name,
                                                                         scale_percent=int(self.config['zoom']),
                                                                         resample_mode=str(self.config['resampling_mode']))
                            if resize_image_state == False:
                                continue

                    # 如果没有进行格式转换，但需要缩放，则直接缩放
                    elif self.config['scale_texture']:
                        resize_image_state = self.imageP.resize_image(input_path=source_file_path,
                                                                     output_path=backup_image_file_path,
                                                                     scale_percent=int(self.config['zoom']),
                                                                     resample_mode=str(self.config['resampling_mode']))

                        # 如果图片处理返回False直接退出循环
                        if resize_image_state == False:
                            continue

                    # 检测UDIM贴图，如果有也进行修改
                    if old_file_info['is_udim']:
                        self._udim_file_process(old_path, old_file_info)


                    # 更新 Maya 节点中的文件路径
                    try:
                        cmds.setAttr(f"{texture_name}.fileTextureName", backup_image_file_path, type="string")
                    except Exception as e:
                        self.feedback.CPW(f"{self.lang['image_conversion']['03']} {texture_name} {self.lang['image_conversion']['04']} {e}") # 更新节点 # 失败

                    # 最后一部 修改主窗口缓存数据
                    self.old_material_node_all_info_dict[material_name][texture_name]['Path'] = backup_image_file_path

                    # 把更新目标写入字典
                    need_update_dict[texture_name]= material_name

                # 更新主窗口字典数据
                new_MterialNodeAllInfoDict = self.getnodedata.TM_StickerUpdateStatusDict(need_update_dict,
                                                                                         self.old_material_node_all_info_dict)



                # 把新的MterialNodeAllInfoDict字典传递回主窗口并刷新窗口
                self.outer_instance.new_MterialNodeAllInfoDict_signal.emit(new_MterialNodeAllInfoDict, need_update_dict)



    # 转换格式按钮
    def image_conversion(self):
        image_processing = self.ImageProcessing(self)
        image_processing.process()


    # 删除相同名称的其他格式文件
    def delete_other_formats(self, file_dir, files_in_directory, name_with_suffix, format):
        # 获取目标文件的名称（不包含后缀）
        target_name = os.path.splitext(name_with_suffix)[0]

        # 遍历目录中的所有文件
        for file_name in files_in_directory:
            # 分离文件名和后缀
            file_name_without_suffix, file_format = os.path.splitext(file_name)

            # 检查文件名是否与目标名称相同，且文件格式不同于指定的格式列表
            if file_name_without_suffix == target_name and file_format != f".{format}":
                # 构造完整路径并删除文件
                file_path = os.path.join(file_dir, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.TM_image_processing_config_FilePath)

        config[key] = cont

        self.dataM.bin_save_data(self.TM_image_processing_config_FilePath, config)
    # --------------------保存设置内容的函数


    # 删除存在objectname的窗口

#______________________________________________________________________________>>>贴图管理器的打包器 支持打包贴图到新的路径中
class TM_TexturePack(QtWidgets.QDialog):

    # 定义一个信号，传递多个变量
    new_MterialNodeAllInfoDict_signal = Signal(dict, dict)

    def __init__(self, WinName='', parent=None):
        super(TM_TexturePack, self).__init__(parent)

        self.TextureManagerWin = parent  # 保存主窗口的引用

        # 0. 初始化全局配置
        self.initial_global_config()

        # 1. 初始化窗口配置
        self.initialize_window_config(WinName)

        # 2. 创建菜单
        self.menu_widgets()

        # 3. 创建控件
        self.create_widgets()

        # 4. 创建布局
        self.create_layouts()

        # 5. 初始化控件
        self.initial_widgets_settings()

    def initial_global_config(self):
        # 实例数据管理器
        self.dataM = DataManager()  # 数据管理
        self.dataP = DataProcessor()  # 数据处理
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData()  # 获取节点数据模块


        # TM_ImageProcessing配置文件路径
        self.TM_texture_pack_config_FilePath = os.path.normpath(os.path.join(script_path, "Datas", "texture_manager",
                                                            "TM_texture_pack_config.bin"))

        # 如果TM_image_processing_config配置文件不存在会重新创建一次
        if not os.path.exists(self.TM_texture_pack_config_FilePath):
            self.dataM.bin_save_data(self.TM_texture_pack_config_FilePath, TM_texture_pack_config_dict)

    def initialize_window_config(self, WinName):
        # 命名常量命名
        WINDOWS_NAME = '贴图打包器' + WinName

        delete_window_if_existe('TM_TexturePack_Win')

        self.setObjectName('TM_TexturePack_Win')
        self.setWindowTitle(WINDOWS_NAME)

        # 窗口长宽
        self.setMinimumHeight(200)
        self.setMinimumWidth(650)

    def menu_widgets(self):
        pass

    def create_widgets(self):
        # ______________________________________________________________________>>> 加载配置文件数据
        config = self.dataM.bin_load_data(self.TM_texture_pack_config_FilePath)  # 加载配置文件

        # ______________________________________________________________________>>> 第一行：输出路径选择框
        # 输出路径输入框
        self.output_path_input = QtWidgets.QLineEdit(self)  # 创建路径输入框
        self.output_path_input.setFixedHeight(40)  # 设置输入框高度
        self.output_path_input.setPlaceholderText("请选择输出文件夹路径...")  # 设置占位提示文本
        self.output_path_input.setText(config["path_edit"])  # 设置默认文本为配置文件中保存的路径
        # 当文本变化时，更新配置文件中的路径信息
        self.output_path_input.textChanged.connect(lambda *args:
                                                   self.modify_config(key="path_edit",
                                                                      cont=self.output_path_input.text()))

        # 输出路径选择按钮
        self.output_path_button = QtWidgets.QPushButton(". . .", self)  # 创建按钮
        self.output_path_button.setFixedHeight(38)  # 设置按钮高度
        self.output_path_button.setFixedWidth(35)  # 设置按钮宽度
        # 绑定点击事件：选择输出路径
        self.output_path_button.clicked.connect(self.select_output_path)

        # ______________________________________________________________________>>> 第二行：选项单选按钮
        # 创建单选按钮组
        self.modify_group = QtWidgets.QButtonGroup(self)
        self.radio_all = QtWidgets.QRadioButton('全部')  # '全部'选项
        self.radio_table = QtWidgets.QRadioButton('表格内')  # '表格内'选项
        self.radio_selection = QtWidgets.QRadioButton('选择中')  # '选择中'选项
        self.modify_group.addButton(self.radio_all, 1)  # 将按钮加入组
        self.modify_group.addButton(self.radio_table, 2)
        self.modify_group.addButton(self.radio_selection, 3)
        # 当选择变化时，更新配置文件中的选项
        self.modify_group.buttonClicked.connect(
            lambda button: self.modify_config('modify_scope_options', self.modify_group.id(button)))

        # 设置默认选中按钮（通过配置文件中的ID）
        modify_group_button = self.modify_group.button(config['modify_scope_options'])
        if modify_group_button:
            modify_group_button.setChecked(True)  # 设置该按钮为选中状态

        # ______________________________________________________________________>>> 第二行：删除源文件和修改路径复选框
        # 删除源文件复选框
        self.delete_source_checkbox = QtWidgets.QCheckBox("删除源文件")
        self.delete_source_checkbox.setChecked(config["delete_source_files"])  # 根据配置设置是否选中
        # 当选项状态变化时，更新配置文件中的删除源文件选项
        self.delete_source_checkbox.stateChanged.connect(lambda *args:
                                                         self.modify_config(key="delete_source_files",
                                                                            cont=self.delete_source_checkbox.isChecked()))

        # 修改路径复选框
        self.change_path_checkbox = QtWidgets.QCheckBox("修改路径")
        self.change_path_checkbox.setChecked(config["modify_path"])  # 根据配置设置是否选中
        # 当选项状态变化时，更新配置文件中的修改路径选项
        self.change_path_checkbox.stateChanged.connect(lambda *args:
                                                       self.modify_config(key="modify_path",
                                                                          cont=self.change_path_checkbox.isChecked()))

        self.copy_tx_files_checkbox = QtWidgets.QCheckBox("打包tx文件")
        self.copy_tx_files_checkbox.setChecked(config["copy_tx_files"])  # 根据配置设置是否选中
        self.copy_tx_files_checkbox.stateChanged.connect(lambda *args:
                                                         self.modify_config(key="copy_tx_files",
                                                                            cont=self.copy_tx_files_checkbox.isChecked()))
        self.delete_source_tx_files_checkbox = QtWidgets.QCheckBox("删除源tx文件")
        self.delete_source_tx_files_checkbox.setChecked(config["delete_source_tx_files"])  # 根据配置设置是否选中
        self.delete_source_tx_files_checkbox.stateChanged.connect(lambda *args:
                                                         self.modify_config(key="delete_source_tx_files",
                                                                            cont=self.delete_source_tx_files_checkbox.isChecked()))
        # ______________________________________________________________________>>> 第三行：打包按钮
        self.pack_button = QtWidgets.QPushButton("打包", self)  # 创建打包按钮
        # 点击按钮时，执行打包操作
        self.pack_button.clicked.connect(lambda *args: self.start_pack())

    def create_layouts(self):
        # 使用垂直布局
        main_layout = QtWidgets.QVBoxLayout()

        # 第一行：输出路径选择
        output_layout = QtWidgets.QHBoxLayout()
        output_layout.addWidget(self.output_path_input)
        output_layout.addWidget(self.output_path_button)

        selection_layout = QtWidgets.QHBoxLayout()
        selection_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_all)
        selection_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_table)
        selection_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        selection_layout.addWidget(self.radio_selection)
        selection_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 第二行：操作选择
        option_layout = QtWidgets.QHBoxLayout()

        option_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        option_layout.addWidget(self.change_path_checkbox)
        option_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        option_layout.addWidget(self.copy_tx_files_checkbox)
        option_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        option_layout.addWidget(self.delete_source_checkbox)
        option_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        option_layout.addWidget(self.delete_source_tx_files_checkbox)
        option_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 第三行：打包按钮
        pack_button_layout = QtWidgets.QHBoxLayout()
        pack_button_layout.addWidget(self.pack_button)

        # 添加所有行到主布局
        main_layout.addLayout(output_layout)
        main_layout.addLayout(selection_layout)
        main_layout.addLayout(option_layout)
        main_layout.addLayout(pack_button_layout)

        self.setLayout(main_layout)

    def initial_widgets_settings(self):
        # 初始化控件设置
        pass

    def select_output_path(self):
        # 打开文件选择框，请选择输出文件夹路径
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "请选择输出文件夹路径")
        if folder:
            folder = os.path.normpath(folder)
            self.output_path_input.setText(folder)

    class TexturePack:
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance  # 外部类实例引用

            # 初始化功能模块
            self.dataM = DataManager()
            self.feedback = FeedbackPrompt()
            self.getnodedata = GetNodeData()

            # 加载配置文件
            self.config = self.dataM.bin_load_data(self.outer_instance.TM_texture_pack_config_FilePath)

            self.old_table_data = self.outer_instance.TextureManagerWin.MterialNodeAllInfoDict
        # 寻找指定的 .tx 文件
        def _find_tx_files(self, image_path):
            # 获取原始文件名（不含扩展名）
            base_name = os.path.splitext(os.path.basename(image_path))[0]

            # 获取文件所在目录
            dir_name = os.path.dirname(image_path)

            # 获取目录下所有文件
            all_files = os.listdir(dir_name)

            # 定义正则表达式，匹配以原始文件名开头，后跟任意字符，最后以 '.tx' 结尾的文件
            pattern = re.compile(rf"^{re.escape(base_name)}.*\.tx$")

            # 筛选出所有匹配的 .tx 文件
            tx_files = [f for f in all_files if pattern.match(f)]

            # 返回完整路径的 .tx 文件列表
            return [os.path.join(dir_name, f) for f in tx_files]

        # 更新节点的路径
        def _update_node_path(self, node_name, new_path):
            try:
                cmds.setAttr(f"{node_name}.fileTextureName", new_path, type="string")
            except Exception as e:
                self.feedback.CPW(f"更新节点 {node_name} 路径失败: {e}")

        # 执行贴图复制操作
        def _copy_to_output(self, old_info_path, new_file_path):
            try:
                shutil.copy(old_info_path, new_file_path)
                self.feedback.CP(f"复制文件: {old_info_path} -> {new_file_path}")
            except Exception as e:
                self.feedback.CPW(f"复制备份文件时出错: {e}")

        # 删除路径下文件函数
        def _delete_files(self, file_path):
            try:
                os.remove(file_path)
                self.feedback.CP(f"删除文件: {file_path}")
            except Exception as e:
                self.feedback.CP(f"删除文件时出错: {e}")

        # 更新主窗口的贴图路径
        def _refresh_main_window_texture_path_data(self, mat_name, node_name ,new_path):

            # update_dict字典是为了储存接下来需要更新主数据
            update_dict = {}

            # 修改旧表格数据
            self.old_table_data[mat_name][node_name]['Path'] = new_path

        # 刷新主窗口的贴图数据
        def _refresh_main_window_texture_data(self, update_dict):
            # 更新主窗口的表格数据
            new_MterialNodeAllInfoDict = self.getnodedata.TM_StickerUpdateStatusDict(update_dict,
                                                                                     self.old_table_data)

            # 获取零时的表格列表数据
            temp_TextureManager_texture_table_data = self.dataM.bin_load_data(self.outer_instance.TextureManagerWin.TextureManager_texture_table_data_temp_path)

            # 获取当前表格中都有那些贴图
            table_tex_list = []
            for index, key in enumerate(temp_TextureManager_texture_table_data):
                table_tex_list.append(temp_TextureManager_texture_table_data[index][0])

            # 把表格中有的贴图做成的列表在总信息中筛选出来
            select_texture_dict = {}
            for index, table_list in enumerate(temp_TextureManager_texture_table_data):
                select_texture_dict[temp_TextureManager_texture_table_data[index][0]] = \
                temp_TextureManager_texture_table_data[index][1]


            # 把新的MterialNodeAllInfoDict字典传递回主窗口并刷新窗口
            self.outer_instance.new_MterialNodeAllInfoDict_signal.emit(new_MterialNodeAllInfoDict, select_texture_dict)

        def _find_udim_textures(self, filepath):
            """
            根据给定的贴图文件路径，查找同一目录下所有同名且带有 UDIM 编号的文件。
            参数:
                filepath (str): 带有 UDIM 编号的贴图文件路径，例如 "C:\\path\\to\\texture.1001.jpeg"
            返回:
                list: 同一目录下所有匹配的 UDIM 贴图文件名列表，例如 ["texture.1002.jpeg", "texture.1003.jpeg"]
            """
            directory = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            # 使用正则表达式解析文件名，提取基名、UDIM 编号和扩展名
            # 例如，"Helmet_emissive.1001.jpeg" 中 base="Helmet_emissive", udim="1001", ext="jpeg"
            udim_pattern = re.compile(r'^(?P<base>.+)\.(?P<udim>\d{4})\.(?P<ext>[^.]+)$')
            match = udim_pattern.match(filename)

            if not match:
                print(f"输入文件名 '{filename}' 不符合 UDIM 命名约定。")
                return []
            base = match.group('base')
            ext = match.group('ext')
            # 构建用于匹配的正则表达式
            search_pattern = re.compile(rf'^{re.escape(base)}\.(\d{{4}})\.{re.escape(ext)}$')
            # 列出目录中所有文件
            try:
                all_files = os.listdir(directory)
            except FileNotFoundError:
                print(f"目录 '{directory}' 不存在。")
                return []
            except PermissionError:
                print(f"没有权限访问目录 '{directory}'。")
                return []
            # 筛选出匹配的 UDIM 文件（除了输入文件本身）
            udim_files = [
                f for f in all_files
                if search_pattern.match(f) and os.path.isfile(os.path.join(directory, f)) and f != filename
            ]
            return udim_files

        def process(self):
            # 0, 定义变量
            # update_dict字典是为了储存接下来需要更新主数据
            update_dict = {}

            # 1, 初始检查
            if not os.path.exists(self.config["path_edit"]):
                self.feedback.CPW('打包输出路径无效')
                return


            # 2, 获取新路径并标准化路径
            new_output_path = os.path.normpath(self.config["path_edit"])

            # 3, 获取处理范围
            need_pack_texture_dict = self.outer_instance.TextureManagerWin.get_selected_table_data(self.config['modify_scope_options'])


            # 4, 检查是否有需要处理的数据 如果没有直接返回
            if not need_pack_texture_dict:
                return

            # 5, 遍历每个纹理并处理每个纹理
            for mat_name in need_pack_texture_dict:
                for node_name, node_cont in need_pack_texture_dict[mat_name].items():

                    ## 1, 获取旧路径并标准化路径和新路径
                    old_info_path = os.path.normpath(node_cont['Path'])
                    new_path = os.path.join(new_output_path, os.path.basename(old_info_path))

                    ## 2, 检查路径是否有效
                    if not os.path.exists(old_info_path):
                        self.feedback.CPW(f"文件路径不存在: {os.path.basename(old_info_path)}")
                        continue

                    ## 3，检测这个文件是否是UDIM贴图
                    if self._find_udim_textures(old_info_path) != []:
                        # 如果是UDIM贴图就获取所有的UDIM贴图
                        old_file_udim = self._find_udim_textures(old_info_path)
                        self.feedback.CP(f"检测到{os.path.basename(old_info_path)}是UDIM，其他UDIM贴图: {str(old_file_udim).replace('[','').replace(']','')}")
                    else:
                        old_file_udim = None

                    ## 4, 复制文件到输出路径
                    if new_output_path == os.path.normpath(os.path.dirname(old_info_path)):
                        self.feedback.CP(f"文件已经存在目标文件夹中: {os.path.basename(old_info_path)}")
                        continue
                    else:
                        self._copy_to_output(old_info_path, new_output_path)

                    ## 5, 检查是否需要打包tx文件
                    if self.config['copy_tx_files']:
                        tx_files = self._find_tx_files(old_info_path)
                        for tx_file in tx_files:
                            new_tx_file_path = os.path.join(new_output_path, os.path.basename(tx_file))
                            self._copy_to_output(tx_file, new_tx_file_path)

                    ## 6, 检查是否需要删除源文件
                    if self.config['delete_source_files']:
                        self._delete_files(old_info_path)

                    ## 7, 检查是否需要删除源tx文件
                    if self.config['delete_source_tx_files']:
                        for tx_file in tx_files:
                            self._delete_files(tx_file)


                    ## 8，执行UDIM贴图的处理
                    if old_file_udim:
                        # 遍历每一个UDIM贴图文件
                        for udim_file_name in old_file_udim:
                            # 获取新/旧文件目录路径
                            new_dir_name = os.path.dirname(new_path)
                            old_dir_name = os.path.dirname(old_info_path)

                            # 构建完整的旧UDIM文件路径和新目标路径
                            old_udim_file_path = os.path.join(old_dir_name, udim_file_name)
                            new_udim_file_path = os.path.join(new_dir_name, udim_file_name)

                            ## 8.1, 复制文件到输出路径
                            # 如果目标路径已存在相同文件，跳过复制
                            if new_udim_file_path == old_udim_file_path:
                                self.feedback.CP(f"文件已经存在目标文件夹中: {new_udim_file_path}")
                                continue
                            else:
                                # 执行文件复制操作
                                self._copy_to_output(old_udim_file_path, new_udim_file_path)

                            ## 8.2, 检查是否需要打包tx文件
                            # 如果配置要求复制tx文件（Arnold压缩纹理）
                            if self.config['copy_tx_files']:
                                # 查找当前UDIM文件对应的tx文件
                                udim_tx_files = self._find_tx_files(old_udim_file_path)
                                # 遍历并复制所有关联的tx文件
                                for tx_file in udim_tx_files:
                                    new_tx_file_path = os.path.join(new_dir_name, os.path.basename(tx_file))
                                    self._copy_to_output(tx_file, new_tx_file_path)

                            ## 8.3, 检查是否需要删除源文件
                            # 如果配置要求删除原始文件
                            if self.config['delete_source_files']:
                                self._delete_files(old_udim_file_path)

                            ##8.4, 检查是否需要删除源tx文件
                            # 如果配置要求删除原始tx文件
                            if self.config['delete_source_tx_files']:
                                # 遍历并删除所有关联的tx文件
                                for tx_file in udim_tx_files:
                                    self._delete_files(tx_file)

                    ## 8，检测是否要修改路径
                    if self.config['modify_path']:
                        # 如果需要修改路径，更新节点的路径
                        if os.path.exists(new_path):
                            self._update_node_path(node_name, new_path)

                        ## 9, 修改主窗口数据的贴图路径
                        self._refresh_main_window_texture_path_data(mat_name, node_name, new_path)

                        ## 10, 存入需要修改的数据
                        update_dict[node_name] = mat_name

            # 6, 更新主窗口的贴图数据
            if self.config['modify_path']:
                # 如果需要修改路径，更新主窗口的贴图数据
                self._refresh_main_window_texture_data(update_dict)


    def start_pack(self):

        TexturePack_processor = self.TexturePack(self)
        TexturePack_processor.process()






    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.TM_texture_pack_config_FilePath)

        config[key] = cont

        self.dataM.bin_save_data(self.TM_texture_pack_config_FilePath, config)
    # --------------------保存设置内容的函数

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

    def __init__(self, parent = MayaMainWindows()):

        super(AOVLightGroupManager, self).__init__(parent)

        # 创建实例类
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData()  # 提取数据模块
        self.dataM = DataManager()  # 储存模块
        self.dataP = DataProcessor()  # 数据处理模块


        self.WINDOWS_NAME = f"AOV灯光组管理器  {SoftwareState} : {SoftwareVersion}"


        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('AOVLightGroupManager')

        self.setObjectName('AOVLightGroupManager')
        self.setWindowTitle(self.WINDOWS_NAME)

        # ...窗口长宽
        self.setMinimumSize(1200, 800)  # 设置一个比较小的最小尺寸


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

        self.cache_path = os.path.join(script_path, "Datas", "aov_light_group_manager", "cache.bin")

        # 如果缓存文件不存在则创建
        if not os.path.exists(self.cache_path):
            self.dataM.bin_save_data(self.cache_path, cache)

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
        self._select_aov_select_list_texts(self.dataM.bin_load_data(self.cache_path))


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
            'default': os.path.join(icon_path, 'aiAreaLight.svg')  # 如果找不到对应的图标就用这个
        }

        # 父级节点的通用图标
        parent_icon = QtGui.QIcon(os.path.join(icon_path, 'BakeGeometryShelf_200.png'))

        # 创建树形结构
        for light_group, lights in light_groups.items():
            print(light_group)

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
        aov_channels = self.dataM.bin_load_data(self.cache_path)

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
        selected_channels = self.dataM.bin_load_data(self.cache_path)

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
        3. 使用 self.dataM.bin_save_data() 方法将数据保存到缓存文件路径。
        """

        def modify_cache():
            # 从 QListWidget 中获取当前选中的项列表
            selected_items = self.aov_select_list_widget.selectedItems()

            # 提取每个选中项的文本内容，组成新的缓存数据列表
            new_cache_data = [item.text() for item in selected_items]

            # 将缓存数据保存到指定路径 (self.cache_path)
            self.dataM.bin_save_data(self.cache_path, new_cache_data)

        # 使用 Qt 的定时器单次调用机制来延迟执行保存操作
        QtCore.QTimer.singleShot(0, lambda *args: modify_cache())


def delete_window_if_existe(window_name):
    for widget in QtWidgets.QApplication.allWidgets():
        if widget.objectName() == window_name:
            widget.close()
            widget.deleteLater()

# 设置不可编辑
class NonEditableColumnsModel(QtGui.QStandardItemModel):
    def __init__(self, rows, columns, non_editable_columns, parent=None):
        """
        自定义的 QStandardItemModel，允许指定某些列不可编辑。

        参数:
        - rows: 初始行数
        - columns: 初始列数
        - non_editable_columns: 不可编辑的列索引列表
        - parent: 父对象（通常是 QWidget）
        """
        super().__init__(rows, columns, parent)
        self.non_editable_columns = non_editable_columns  # 保存不可编辑的列索引列表

    def flags(self, index):
        """
        重写 QStandardItemModel 的 flags 方法，根据列索引来控制单元格的可编辑性。

        参数:
        - index: 当前单元格的 QModelIndex 对象

        返回:
        - 如果当前单元格位于不可编辑的列中，则返回仅可选择和可启用的标志；
          否则，返回默认的标志（可编辑、可选择等）。
        """
        # 如果当前列在不可编辑列的索引列表中
        if index.column() in self.non_editable_columns:
            # 返回仅可选择（ItemIsSelectable）和可启用（ItemIsEnabled）的标志，表示该单元格不可编辑
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        # 否则，调用父类的 flags 方法，返回默认的标志，保持单元格的可编辑性
        return super().flags(index)

# 设置文本对齐方式为居中对齐
class CenterDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        """
        初始化并设置单元格的样式选项。

        :param option: QStyleOptionViewItem，表示单元格的样式选项
        :param index: QModelIndex，表示当前单元格的索引
        """
        # 调用父类的 initStyleOption 方法，以确保基础选项的初始化
        super().initStyleOption(option, index)

        # 设置文本对齐方式为居中对齐
        # Qt.AlignCenter 表示文本会在水平方向和垂直方向上都居中
        option.displayAlignment = QtCore.Qt.AlignCenter

# 设置文本对齐方式为左对齐和垂直居中
class LeftAlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        """
        初始化并设置单元格的样式选项。

        :param option: QStyleOptionViewItem，表示单元格的样式选项
        :param index: QModelIndex，表示当前单元格的索引
        """
        # 调用父类的 initStyleOption 方法，以确保基础选项的初始化
        super().initStyleOption(option, index)

        # 设置文本对齐方式为左对齐和垂直居中
        # Qt.AlignLeft 表示文本在水平方向上左对齐
        # Qt.AlignVCenter 表示文本在垂直方向上居中对齐
        option.displayAlignment = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

#______________________________________________________________________________>>> 贴图管理器实例窗口
def  TextureManagerWinInstance():
    texture_manager = TextureManagerWin()
    texture_manager.show()

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
    texture_processing_data = dataM.bin_load_data(
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
        self.Render_settings_Data = self.dataM.bin_load_data(
            os.path.normpath(
                os.path.join(datas_path, 'render_presets', menu_sl_val + '.bin')
            )
        )
        # 读取渲染配置参数
        config = self.dataM.bin_load_data(
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

            # 03, 将渲染器属性保存到二进制文件中
            if not os.path.exists(os.path.join(write_data_path, self.import_val + ".bin")):
                self.dataM.bin_save_data(os.path.join(write_data_path, self.import_val + ".bin"), Render_settings)



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
                render_preset_path,  sl_name+ '.bin'
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
        self.config = self.dataM.bin_load_data(
            os.path.join(settings_path, AMS_Config))


        self.texture_processing_data = self.dataM.bin_load_data(
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

        matching_completed_dict = self.detect_and_calculate_similarity()

        # alt 只会创建贴图
        if keyboard.is_pressed('alt') or keyboard.is_pressed('shift'):

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
            if keyboard.is_pressed('shift'):
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
            dir_name_path = self.pathD.detection_path_content(target_dirname, self.config['path_detection_params']['exclude'])

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
        self.config = self.dataM.bin_load_data(
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


        # if keyboard.is_pressed('alt'):
        #     self.auto_connect_node()
        # else:
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
            if keyboard.is_pressed('shift'):
                mat_name = cmds.shadingNode('aiStandardSurface', asShader=True)

        return mat_name

    # 修改材质名称
    def modify_mat_name(self,original_mat_name,  file_name):

        texture_processing_data = self.dataM.bin_load_data(
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


class ConvertOldMaterialsToArnold:
    def __init__(self, materials_list):
        config_path  = os.path.join(script_path, 'config', 'maya_to_arnold_shader_map.json')

        with open(config_path, 'r') as f:
            self.convert_info = json.load(f)

        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor() # 节点处理模块





# 实例使用路径连接
def path_detection_connection_button():
    PDC = Path_Detection_Connection()
    PDC.main()

# 实例使用魔法连接
def magic_connection_button():
    MC = Magic_Node_Connection()
    MC.main()

    # 混合颜色节点

# 颜色混合
def blend_rgba_node():

    BlendNM = BlendNodeManager() # 混合节点模块
    feedback = FeedbackPrompt()  # 错误提示模块

    select_node = process_sl_data()

    if select_node is None:
        return

    for key in select_node:
        if key == 'file':
            BlendNM.blend_file_rgba_node()
            return
        elif key == 'aiLayerRgba':
            BlendNM.blend_rgba_aiLayerRgba_node()
            return
        elif key == 'aiStandardSurface':
            BlendNM.blend_aiStandardSurface_rgba()
            return
        else:
            pass

# 混合灰度通道
def blend_greg_manager():

    BlendNM = BlendNodeManager() # 混合节点模块
    feedback = FeedbackPrompt()  # 错误提示模块

    select_node = process_sl_data()

    if select_node is None:
        return

        # 根据选择的节点类型调用对应的处理函数
    for key in select_node():
        if  'aiLayerRgba' in select_node and 'file' in  select_node:
            BlendNM.blend_aiLayerRgba_mask()
            return
        elif 'aiLayerShader' in select_node and 'file' in  select_node:
            BlendNM.blend_aiStandardSurface_mask()
            return
        elif key == 'file':
            BlendNM.blend_aiLayerFloat_mask()
            return
        else:
            pass

# 场景名称优化
class SceneNameOptimization:
    def __init__(self):
        self.dataM = DataManager() # 数据管理模块
        self.feedback = FeedbackPrompt() # 错误提示模块
        self.pathD = PathDetection() # 数据检测模块
        self.nodeP = NodeProcessor() # 节点处理模块

        self.scene_nodes = get_scene_all_data()

        self.config = self.dataM.bin_load_data(
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

# 主要运行程序
def Main_program():

    # 创建窗口
    indowInstance = Arnold_Magic_Node_UI()

# 测试主程序
def test_program():
    pass