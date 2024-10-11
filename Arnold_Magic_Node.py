##############################################################################################
# # ++ 导入所需的库和模块
from time import sleep

# 1. Maya 库
import maya.cmds as cmds  # 导入 Maya 的 cmds 模块，用于执行 Maya 命令和操作场景
import maya.OpenMayaUI as omui  # 导入 Maya 的 OpenMayaUI 模块，用于操作 Maya 的用户界面

# 2. 文件与系统操作
import os  # 提供与操作系统交互的功能，如文件路径操作、目录遍历等
import sys  # 提供与 Python 解释器交互的功能，如获取脚本路径、调整模块搜索路径等
import importlib  # 用于动态导入和重新加载模块，支持模块的按需加载
import pathlib  # 提供面向对象的文件系统路径操作，增强对路径的处理能力
import shutil

# 3. 数据处理
import json  # 用于序列化和反序列化 JSON 数据，方便与外部数据进行交换
import ast  # 用于解析和操作 Python 代码的抽象语法树，适用于代码分析和转换
import copy  # 提供对象的浅拷贝和深拷贝功能，确保数据在复制时不会相互影响
import msgpack  # 用于高效的二进制序列化和反序列化，比 JSON 更节省空间和更快
from ahocorapy.keywordtree import KeywordTree  # 用于高效的多模式匹配，适合文本搜索和过滤

# 4. 字符串处理
import re  # 提供正则表达式操作，用于模式匹配、搜索和替换字符串
import difflib  # 用于比较文本差异，生成差异报告或补丁，适合版本控制和文本分析

# 5. 图像处理
import imghdr  # 用于识别图像文件的类型，如 JPEG、PNG、GIF 等
from PIL import Image  # 导入 Pillow 库，用于图像打开、编辑和保存，支持多种图像格式和高级图像处理功能

# 6. 时间管理
import time  # 提供时间相关的函数，如时间戳获取、延时操作等
from datetime import datetime  # 提供日期和时间的对象和操作方法，支持更复杂的时间处理

# 7. 网络操作
import webbrowser  # 提供在 Web 浏览器中打开 URL 的功能，支持跨平台操作
import keyboard  # 用于监听和发送键盘事件，适合自动化任务和快捷键实现

# 8. PySide 库
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

# ------------------------------------------
# 获取脚本路径
SCRIPT_PATH = os.path.join(os.path.dirname(__file__))  # 获取当前脚本的目录路径
# ------------------------------------------

# 9. 自定义库导入与依赖管理
import Arnold_Magic_Node_lib  # 导入自定义的 Arnold 魔法节点库
importlib.reload(Arnold_Magic_Node_lib)  # 在开发阶段，重新加载模块以反映对库的更改
from Arnold_Magic_Node_lib import *  # 从自定义库中导入所有内容

import DependenciesLibs  # 导入自定义的依赖管理模块
DependenciesLibs.importLibs()  # 调用自定义模块中的函数，动态导入和初始化所需的依赖库

import InitialConfigFile

# 10. 初始化变量
# 创建初始化变量
LicenseV_device_fingerprint = None
LicenseV_public_key = None
LicenseV_public_password = None
LicenseV_remaining_time = None
LicenseV_type = None
LicenseV_type_name = None

# 这个是默认窗口的名称记录函数
AMN_UI_WorkSpaceControl = None

##############################################################################################

# --------------------初始变量开始
SoftwareState = "Beta"
SoftwareVersion = "0.6.4.2"

pluginHomePath = r"https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69"
pluginFeedbackURL = r"https://flowus.cn/form/7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69"

datas_path = os.path.join(SCRIPT_PATH, "Datas") # 定义数据文件夹  ->全局变量

settings_path = os.path.join(datas_path, "settings") # 定义设置配置文件夹  ->全局变量

icon_path = os.path.join(SCRIPT_PATH, "icon") # 定义图标路径  ->全局变量


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
    "search_subfolders_checkbox" : False,
    "multiple_subfolder_search_checkbox" : False,
    "ignore_case_checkbox" : False
}

TM_ImageProcessing_config_dict = {
    "format" : "jpg",
    "zoom" : "100",
    "resampling_mode" : 1,
    "JPG_quality" : 90,
    "PNG_quality" : 7,
    "backup_suffix" : '_TM_backup',
    "processed_suffix" : "_TM_processed" ,
    "convert_format" : True,
    "scale_texture" : False,
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

# 插件窗口
class Arnold_Magic_Node_UI(object):
    def __init__(self):
        global AMN_UI_WorkSpaceControl
        WIN_TITLE = f"Arnold_Magic_Node  {SoftwareState} : {SoftwareVersion}   {LicenseV_type_name} : {str(LicenseV_remaining_time)}"

        # 判断窗口是否存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)

        # 创建主窗口
        self.window = cmds.workspaceControl(WIN_TITLE, retain=False, floating=True,w=300,h=300)
        AMN_UI_WorkSpaceControl = self.window

        # 初始化全局数据
        self.initial_global_config()

        # 创建窗口控件
        self.create_widgets()

        # 显示窗口
        cmds.showWindow(self.window)


    def create_widgets(self):

        cmds.rowLayout(numberOfColumns=30)
        # 创建按钮

        # 菜单========= 
        customMenu = cmds.popupMenu(button=3)

        cmds.menuItem(label= '贴图处理工具', divider=True) # 添加分割线

        cmds.menuItem(label= '贴图管理器', c=lambda *args: TextureManagerWinInstance(),
                      i = icon_path + "\\TXManagerShelf_200.png")

        cmds.menuItem(label= '贴图批量导入器', c=lambda *args: TextureBatchImporterWin(),
                      i = icon_path + "\\RenderToTextureShelf_200.png")

        cmds.menuItem(label= '渲染预设设置',
                      divider=True) # 添加分割线

        cmds.menuItem(label= '添加渲染预设',
                      c=lambda *args: rendering_preset_settings_button(self.rendering_preset))

        cmds.menuItem(label= '修改渲染预设',
                      c= lambda *args: modify_rendering_preset_menuItem(
                          cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                          cmds.optionMenu(self.rendering_preset, query=True, value=True), self.rendering_preset_name, self.rendering_preset))

        cmds.menuItem(label= '删除渲染预设',
                      c= lambda *args: delete_rendering_preset_menuItem(
                          cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                          cmds.optionMenu(self.rendering_preset, query=True, value=True), self.rendering_preset_name))

        cmds.menuItem(label= '打开渲染预设文件夹',
                      c= lambda *args: os.startfile(os.path.join(SCRIPT_PATH, 'Datas', 'render_settings')))

        cmds.menuItem(divider=True)

        default_rendering_properties_options = cmds.menuItem(label= '输出 默认参数',
                                                             cb= True,
                                                             c= lambda *args: self.modify_rendering_properties_write_options('default_rendering_properties_write_options', cmds.menuItem(default_rendering_properties_options, query=True, checkBox=True)))

        rendering_properties_options = cmds.menuItem(label= '输出 阿诺德参数',
                                                     cb= True,
                                                     c= lambda *args: self.modify_rendering_properties_write_options('rendering_properties_write_options', cmds.menuItem(rendering_properties_options, query=True, checkBox=True) ))

        aov_properties_properties_options = cmds.menuItem(label= '输出 AOV参数',
                                                          cb= True,
                                                          c= lambda *args: self.modify_rendering_properties_write_options('AOV_properties_properties_write_options', cmds.menuItem(aov_properties_properties_options, query=True, checkBox=True) ))
        cmds.menuItem(divider=True)

        cmds.menuItem(label= '设置',
                      c= lambda *args: ArnoldMagicNodeSettingsPanel())

        # 读取settings_path文件夹下的render_preset_config_dict文件
        render_preset_config_dict =  self.dataM.bin_load_data(
            os.path.join(settings_path, 'render_preset_config.bin'))

        # 修改默认值
        cmds.menuItem(default_rendering_properties_options,
                      edit = True,
                      checkBox = render_preset_config_dict['default_rendering_properties_write_options'])
        cmds.menuItem(rendering_properties_options,
                      edit = True,
                      checkBox = render_preset_config_dict['rendering_properties_write_options'])
        cmds.menuItem(aov_properties_properties_options,
                      edit = True,
                      checkBox = render_preset_config_dict['AOV_properties_properties_write_options'])
        # 菜单=========

        cmds.text(label=" "*1)




        # Magic_Connection
        self.magic_connection = cmds.button(label="魔法连接",c=lambda *args: magic_connection_button())

        self.path_detection_connection = cmds.button(label="路径拾取连接",c=lambda *args: path_detection_connection_button())

        # Direct_Connection
        self.direct_connection = cmds.button(label="直连",c=lambda *args: direct_connection_button())
        # Unify Uv Node
        self.unify_uv_node = cmds.button(label="统一UV",c=lambda *args: unify_uv_node_button())

        cmds.text(label=" "*2)

        self.uv_preset = cmds.optionMenu(mvi = 8, cc=lambda* args:uv_preset_menu(cmds.optionMenu(self.uv_preset, query=True, value=True)))
        # 用循环创建uv_mode_list 的menu
        uv_mode_list = ['禁用','0型(ZBrush)','1型(Mudbox)','UDIM(Mari)','显示平铺']
        for uv_mode_name in uv_mode_list:
            cmds.menuItem(label=uv_mode_name)




        self.color_space_preset = cmds.optionMenu(mvi = 16, cc=lambda* args:color_space_preset_menu(cmds.optionMenu(self.color_space_preset, query=True, value=True)))
        # 用循环创建color_space_list的menu

        # 读取settings_path文件夹下的texture_processing_data文件
        texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin')
        )
        
        # 循环创建色彩空间菜单选项
        for color_space_name in texture_processing_data['ColorSpace']['ColorSpaceData']:
            cmds.menuItem(label = color_space_name)

        # 自动色彩空间的按钮
        cmds.button(label="自动色彩空间",c=lambda *args: AutoSet_TexColorSpace())

        cmds.text(label=" "*2)

        self.ai_aov_switch = cmds.button(label="AOV开关",c=lambda *args: ai_aov_switch_button())

        # 渲染预设的菜单 —————————————————— 开始
        self.rendering_preset_name = {}
        self.rendering_preset =  cmds.optionMenu(mvi = 8, cc=lambda* args:rendering_preset_menu(cmds.optionMenu(self.rendering_preset, query=True, value=True)))
        # self.rendering_preset_settings = cmds.button(label="添加预设",c=lambda *args: rendering_preset_settings_button(self.rendering_preset))


        renderer_data_path =  SCRIPT_PATH + r"\Datas\Render_settings"

        # 获取文件名字
        file_names = os.listdir(renderer_data_path)

        # 删除文件名中的 ".json" 部分并存储在列表中
        file_names_without_json_list = [file_name.replace(".json", "") for file_name in file_names]

        for renderer_data_mode_name in file_names_without_json_list:
            self.rendering_preset_name[renderer_data_mode_name] = cmds.menuItem(label=renderer_data_mode_name.replace('.bin', ''))


        # 渲染预设的菜单 —————————————————— 结束


        cmds.text(label="                     "*1)
        # self.Arnold_Magic_Node_Settings_Panel = cmds.button(label="设置",c=lambda *args: Arnold_Magic_Node_Settings_Panel())
        # self.test = cmds.iconTextButton(i=SCRIPT_PATH+ r'\icon\TEST.png',c=lambda *args: test(), h=37.5/1.8,w=80)
        cmds.iconTextButton(i = os.path.join(icon_path, 'Autodesk_Arnold_logo.png'),
                            h=37.5/1.8,
                            w=155/1.8,
                            c=lambda *args: ArnoldMagicNodeSettingsPanel())

        cmds.text(label=" "*1)

    # 初始化全局数据
    def initial_global_config(self):
        self.dataM = DataManager()
        self.dataP = DataProcessor()
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData() # 获取节点数据模块

    # 修改渲染属性写入选项
    def modify_rendering_properties_write_options(self, write_name, val):
        # 读取渲染文件
        new_render_preset_config =  self.dataM.bin_load_data(
            os.path.join(settings_path, 'render_preset_config.bin'))

        # 修改数据
        new_render_preset_config[write_name] = val

        # 保存修改完的渲染预设配置
        self.dataM.bin_save_data(os.path.join(settings_path, 'render_preset_config.bin'),
                                 new_render_preset_config)

# 插件设置按钮qt写
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
        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

        # 加载语言配置文件并获取 'language_config' 键的值
        language_config = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'settings', 'language_config.json'))['language_config']

        # 动态加载相应语言的JSON文件，并读取 'ArnoldMagicNode' 中的 'AMNSP_WIN' 键
        self.language = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'languages', f'{language_config}.json'))['ArnoldMagicNode']['AMNSP_WIN']

    def initialize_window_config(self):

        WINDOWS_NAME = f"{self.language['initialize_window_config']['WINDOWS_NAME']}  {SoftwareState} : {SoftwareVersion}  {LicenseV_type_name} : {str(LicenseV_remaining_time)} "  # Win名称

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
        self.reset_data_action = QAction(self.language['create_menu']['settings_menu'], self) # 重置设置数据
        # 连接“重置数据”动作的触发信号到对应的槽函数
        self.reset_data_action.triggered.connect(lambda *args: (os.remove(os.path.join(settings_path, 'texture_processing_data.bin')),
                                                          InitialConfigFile.Main_program()))
        self.settings_menu.addAction(self.reset_data_action)

        # 许可证菜单及其动作
        self.license_menu = self.main_menu_bar.addMenu(self.language['create_menu']['license_menu']) # 许可证

        # 创建“更换许可证”动作
        self.change_license_action = QAction(self.language['create_menu']['change_license_action'], self) # 更换许可证
        self.change_license_action.triggered.connect(lambda *args: self.replace_license())

        # 将动作添加到许可证菜单
        self.license_menu.addAction(self.change_license_action)


        # 关于菜单及其动作
        self.about_menu = self.main_menu_bar.addMenu(self.language['create_menu']['about_menu']) # 关于

        # 创建“赞助”动作

        # 创建“联系/反馈”动作
        self.contact_feedback_action = QAction(self.language['create_menu']['contact_feedback_action'], self) # 联系/反馈
        self.contact_feedback_action.triggered.connect(
            lambda *args:  QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginFeedbackURL)))
        # 创建“帮助文档”动作并连接到打开帮助文档的槽函数
        self.help_document_action = QAction(self.language['create_menu']['help_document_action'], self)
        self.help_document_action.triggered.connect(
            lambda *args: QtGui.QDesktopServices.openUrl(QtCore.QUrl(pluginHomePath)))

        # 将动作添加到关于菜单

        self.about_menu.addAction(self.contact_feedback_action)
        self.about_menu.addAction(self.help_document_action)


    def create_widgets(self):
        # 创建选项卡部件
        self.tab_widget = QtWidgets.QTabWidget()

        # 创建各个选项卡页面
        self.create_magic_connection_tab()
        self.create_color_space_tab()
        self.create_node_connection_tab()
        self.create_path_matching_tab()

    def create_layouts(self):
        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setMenuBar(self.main_menu_bar)
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    # 初始化控件的设置，例如设置默认值，连接信号和槽等
    def initial_widgets_settings(self):
        # 初始化 连接时智能修改色彩空间 控件值
        self.auto_color_space_connection.setChecked(
            self.texture_processing_data['ProcSet_Options']['MagicConnectionSetColorSpace'])

        # 初始化 连接时修改材质名称 控件值
        self.magic_change_material_name_options.setChecked(
            self.texture_processing_data['ProcSet_Options']['change_material_name'])

        self.update_similarity_max_slider_ui()

    # 魔法连接的标签页面
    def create_magic_connection_tab(self):
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        # 创建一个用于存放内容的 QWidget
        content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content_widget)

        # [1] 连接设置
        
        self.add_line_with_text(layout , "魔法连接设置")
         
        self.auto_color_space_connection = QtWidgets.QCheckBox('连接时智能修改色彩空间')

        # auto_color_space_connection 连接修改配置函数
        self.auto_color_space_connection.stateChanged.connect(lambda *args: self.modify_nested_config(
                self.auto_color_space_connection.isChecked(),
                ['ProcSet_Options', 'MagicConnectionSetColorSpace']))

        layout.addWidget(self.auto_color_space_connection)

        self.magic_change_material_name_options = QtWidgets.QCheckBox('连接时修改材质名称')

        # auto_color_space_connection 连接修改配置函数
        self.magic_change_material_name_options.stateChanged.connect(lambda *args: self.modify_nested_config(
                self.magic_change_material_name_options.isChecked(),
                ['ProcSet_Options', 'change_material_name']))

        layout.addWidget(self.magic_change_material_name_options)

        
        # [2] 自定义连接的贴图
        self.add_line_with_text(layout , "自定义连接的贴图")
         
        self.tex_first_filter_options_list = QtWidgets.QListWidget()

        ## 设置tex_first_filter_options_list参数

        # 设置大小
        self.tex_first_filter_options_list.setFixedHeight(530)

        # 设置选择模式
        self.tex_first_filter_options_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        # 循环创建每一个选项
        for name, value in self.texture_processing_data['ProcSet_Options']['Magic_Connection_Options'].items():
            item = QtWidgets.QListWidgetItem(name.capitalize()) # 让名称的第一个字大写
            item.setFont(font)
            self.tex_first_filter_options_list.addItem(item)

            item.setSelected(value)
        # 触发绑定函数
        self.tex_first_filter_options_list.selectionModel().selectionChanged.connect(
            lambda *args: self.modify_tex_first_filter_options_list_config())

        layout.addWidget(self.tex_first_filter_options_list)

        
        # [3] 自定义过滤名字
        self.add_line_with_text(layout , "自定义过滤名字")
         

        self.texture_filter_fields = {}

        for channel, filters in self.texture_processing_data['TexFirstFilter'].items():
            # 创建标题 第一个字母大写
            channel_label = QtWidgets.QLabel(f"{channel.capitalize()} :")
            # 加粗字体
            channel_label.setStyleSheet("font-weight: bold;")
            # 添加到layout
            layout.addWidget(channel_label)

            # 创建输入框，并设置初始文本为过滤器的组合
            self.texture_filter_fields[channel] = QtWidgets.QLineEdit(", ".join(filters))

            # 设置默认值
            self.texture_filter_fields[channel].setText(
                str(filters)
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , "))


            # 编辑时触发函数，绑定到具体的 QLineEdit 对象
            self.texture_filter_fields[channel].textChanged.connect(
                lambda text, ch=channel: self.modify_texture_filter_fields_config(ch, text)
            )

            # 添加到layout
            layout.addWidget(self.texture_filter_fields[channel])

        # 创建一个 QScrollArea，并将内容部件添加进去
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)  # 使滚动区域自适应内容大小
        scroll_area.setWidget(content_widget)  # 将内容部件设置为滚动区域的部件

        # 创建一个用于选项卡的 QWidget，并设置布局
        magic_connection_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(magic_connection_tab)
        tab_layout.addWidget(scroll_area)  # 将滚动区域添加到选项卡布局中

        # 将选项卡添加到 tab_widget
        self.tab_widget.addTab(magic_connection_tab, "魔法连接")

    # 颜色空间的标签页面
    def create_color_space_tab(self):
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        # 初始化变量
        color_spaces_data = self.texture_processing_data['ColorSpace']  # 示例色彩空间列表


        # 创建一个用于存放内容的 QWidget
        content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content_widget)

        
        # [1] 自定义色彩空间
        self.add_line_with_text(layout , "自定义色彩空间")
         
        self.color_space_text = QtWidgets.QPlainTextEdit()


        # 设置 color_space_text 的内容
        self.color_space_text.setPlainText(
            str(color_spaces_data['ColorSpaceData'])
            .replace('[', '')
            .replace(']', '')
            .replace("'", "")
            .replace(",", " , "))

        # 设置窗口高度是350
        self.color_space_text.setFixedHeight(350)

        # 设置字体
        self.color_space_text.setFont(font)

        # 修改激活函数 连接函数槽
        self.color_space_text.textChanged.connect(self.modify_color_space_text_config)




        layout.addWidget(self.color_space_text)
         
        # [2] 自动设置色彩空间
        self.add_line_with_text(layout , "自动设置色彩空间")
        
        self.auto_color_space_options = {}

        # 用来储存图标变量
        AutoSetColorSpaceMenuName = {}

        channels = self.texture_processing_data['TexFirstFilter']  # 示例通道列表

        for channel in channels:
            h_layout = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(f"{channel.capitalize()}:")

            # 加粗字体
            label.setStyleSheet("font-weight: bold;")

            AutoSetColorSpaceMenuName[channel] = QtWidgets.QComboBox()

            AutoSetColorSpaceMenuName[channel].addItems(color_spaces_data['ColorSpaceData'])

            # 设置默认值
            AutoSetColorSpaceMenuName[channel].setCurrentText(color_spaces_data['AutoSetColorSpaceConfig'][channel])

            # 设置激活函数
            AutoSetColorSpaceMenuName[channel].currentIndexChanged.connect(
                lambda _, ch=channel:
                self.modify_nested_config(AutoSetColorSpaceMenuName[ch].currentText(), ['ColorSpace',
                                                                                        'AutoSetColorSpaceConfig',
                                                                                        ch]))


            # self.auto_color_space_options[channel] = combo_box

            h_layout.addWidget(label)

            h_layout.addWidget(AutoSetColorSpaceMenuName[channel])

            layout.addLayout(h_layout)

        # 创建一个 QScrollArea，并将内容部件添加进去
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # 创建一个用于选项卡的 QWidget，并设置布局
        color_space_tab = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(color_space_tab)
        tab_layout.addWidget(scroll_area)

        # 将选项卡添加到 tab_widget
        self.tab_widget.addTab(color_space_tab, "颜色空间")

    # 节点连接的标签页面
    def create_node_connection_tab(self):
        # 创建配置变量
        node_connection_config = self.texture_processing_data['ProcSet_Options']

        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        # 节点连接选项卡
        node_connection_widget = QtWidgets.QWidget()
        node_connection_layout = QtWidgets.QVBoxLayout(node_connection_widget)

        # 使用QScrollArea实现滚动
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(scroll_content_widget)

        # [1] 自定义连接的节点
        
        self.add_line_with_text(layout , "自动连接处理节点设置")
         
        self.auto_node_connection_list = QtWidgets.QListWidget()
        self.auto_node_connection_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        for channel, value in node_connection_config['Auto_Node_Connection_Options'].items():
            item = QtWidgets.QListWidgetItem(channel.capitalize())  # 让名称的第一个字大写
            item.setSelected(True)
            item.setFont(font)
            self.auto_node_connection_list.addItem(item)

            item.setSelected(value)

        # 设置大小
        self.auto_node_connection_list.setFixedHeight(530)

        # 绑定修改自动连接处理界定啊配置函数
        self.auto_node_connection_list.selectionModel().selectionChanged.connect(
            lambda *args: self.modify_auto_node_connection_config())

        layout.addWidget(self.auto_node_connection_list)

        self.add_line_with_text(layout, "处理节点设置")

        input_port_combo = {}
        output_port_combo = {}
        self.node_list_edit = {}
        # 动态创建节点连接设置
        for channel, data in node_connection_config['ProcessingNodeData'].items():

            # 通道的名称标题
            layout.addWidget(self.create_section_label(channel.capitalize()+':'))

            # 创建一个横着的layout
            h_layout = QtWidgets.QHBoxLayout()

            # 输入端的多选
            input_port_combo[channel] = QtWidgets.QComboBox()
            input_port_combo[channel].addItems(node_connection_config['InputPortList'])  # 示例输入端口
            input_port_combo[channel].setCurrentText(
                node_connection_config['ProcessingNodeData'][channel]['InputPort'])
            input_port_combo[channel].setFixedWidth(130)
            input_port_combo[channel].currentIndexChanged.connect(
                lambda _, ch=channel:
                self.modify_nested_config(input_port_combo[ch].currentText(), ['ProcSet_Options',
                                                                                        'ProcessingNodeData',
                                                                                        ch, 'InputPort']))

            # 创建的节点输入列表
            self.node_list_edit[channel] = QtWidgets.QLineEdit()
            self.node_list_edit[channel].setText(
                str(node_connection_config['ProcessingNodeData'][channel]['NodeList'])
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , "))
            self.node_list_edit[channel].textChanged.connect(
                lambda text, ch=channel: self.modify_pro_node_list_config(ch, text)
            )

            # 输出端的多选
            output_port_combo[channel] = QtWidgets.QComboBox()
            output_port_combo[channel].addItems(node_connection_config['OutputPortList'])  # 示例输出端口
            output_port_combo[channel].setCurrentText(
                node_connection_config['ProcessingNodeData'][channel]['OutputPort'])
            output_port_combo[channel].setFixedWidth(130)
            output_port_combo[channel].currentIndexChanged.connect(
                lambda _, ch=channel:
                self.modify_nested_config(output_port_combo[ch].currentText(), ['ProcSet_Options',
                                                                                        'ProcessingNodeData',
                                                                                        ch, 'OutputPort']))
            # 加入到创建节点的列表中
            add_node_button = QtWidgets.QPushButton("<")
            add_node_button.setFixedWidth(30)
            add_node_button.setFixedHeight(28)
            add_node_button.clicked.connect(lambda *_, ch=channel: self.add_pro_node_to_list(ch))

            # 全部加入到layout中
            h_layout.addWidget(input_port_combo[channel])
            h_layout.addWidget(self.node_list_edit[channel])
            h_layout.addWidget(output_port_combo[channel])
            h_layout.addWidget(add_node_button)

            layout.addLayout(h_layout)

        # 将内容添加到滚动区域
        scroll_area.setWidget(scroll_content_widget)
        node_connection_layout.addWidget(scroll_area)

        # 添加到选项卡
        self.tab_widget.addTab(node_connection_widget, "节点连接")

    # 节点路径匹配页面
    def create_path_matching_tab(self):
        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(SMALL_FONT_SIZE)  # 设置字体大小
        font.setBold(True)  # 设置加粗

        # 定义一个通用的更新函数，用于更新滑杆的值和配置
        def update_slider_value(slider_name, value):
            adjusted_value = value * 0.001  # 将滑杆的整数值转换为小数
            self.modify_config(slider_name, adjusted_value, 'path_detection_config.bin')  # 更新配置文件
            # 动态获取对应的标签并更新显示
            label = getattr(self, f"{slider_name}_label")
            label.setText("{:.3f}".format(adjusted_value))

        # 加载路径检测配置
        path_detection_config = self.dataM.bin_load_data(
            os.path.join(settings_path, 'path_detection_config.bin')
        )

        # 创建节点路径匹配选项卡，使用QScrollArea实现滚动
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        path_matching_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(path_matching_widget)

        
        # [1] 连接时相关设置
        self.add_line_with_text(layout , "连接时相关设置")
         

        self.path_matching_checkbox = QtWidgets.QCheckBox('连接时智能修改色彩空间')
        self.path_matching_checkbox.setChecked(path_detection_config['PathDetectionConnectionSetColorSpace'])
        # 连接复选框的状态变化信号到修改配置函数
        self.path_matching_checkbox.stateChanged.connect(lambda *args:  self.modify_config(
            'PathDetectionConnectionSetColorSpace',
            self.path_matching_checkbox.isChecked(),
            'path_detection_config.bin'))

        layout.addWidget(self.path_matching_checkbox)

        self.path_matching_change_material_name_options = QtWidgets.QCheckBox('连接时修改材质名称')
        self.path_matching_change_material_name_options.setChecked(path_detection_config['change_material_name'])
        # 连接复选框的状态变化信号到修改配置函数
        self.path_matching_change_material_name_options.stateChanged.connect(lambda *args:  self.modify_config(
            'change_material_name',
            self.path_matching_change_material_name_options.isChecked(),
            'path_detection_config.bin'))

        layout.addWidget(self.path_matching_change_material_name_options)


        self.path_disable_feedback_options = QtWidgets.QCheckBox('关闭反馈')
        self.path_disable_feedback_options.setChecked(path_detection_config['disable_feedback'])
        # 连接复选框的状态变化信号到修改配置函数
        self.path_disable_feedback_options.stateChanged.connect(lambda *args:  self.modify_config(
            'disable_feedback',
            self.path_disable_feedback_options.isChecked(),
            'path_detection_config.bin'))

        layout.addWidget(self.path_disable_feedback_options)

         
        # [2] 排除名称
        self.add_line_with_text(layout , "筛选过程中排除含有文字的文件")
        
        self.exclude_list_text = QtWidgets.QPlainTextEdit()
        # 设置默认排除列表，并格式化显示
        self.exclude_list_text.setPlainText(str(path_detection_config['exclude_list'])
                                            .replace('[', '')
                                            .replace(']', '')
                                            .replace("'", "")
                                            .replace(",", " , "))
        self.exclude_list_text.setFont(font)

        # 当排除列表文本发生变化时，更新配置文件
        self.exclude_list_text.textChanged.connect(
            lambda *args:  self.modify_config(
                'exclude_list',
                [item.replace(' ', '') for item in self.exclude_list_text.toPlainText().split(",")]
                , 'path_detection_config.bin'))

        layout.addWidget(self.exclude_list_text)

         
        # [3] 格式名称
        self.add_line_with_text(layout , "在进行相似度检测时移除字符串中的特定内容")
        
        self.detection_excluded_list = QtWidgets.QPlainTextEdit()
        # 设置默认格式列表，并格式化显示
        self.detection_excluded_list.setPlainText(str(path_detection_config['detection_excluded_list'])
                                           .replace('[', '')
                                           .replace(']', '')
                                           .replace("'", "")
                                           .replace(",", " , "))
        self.detection_excluded_list.setFont(font)

        # 当格式列表文本发生变化时，更新配置文件
        self.detection_excluded_list.textChanged.connect(
            lambda *args:  self.modify_config(
                'detection_excluded_list',
                [item.replace(' ', '') for item in self.detection_excluded_list.toPlainText().split(",")]
                , 'path_detection_config.bin'))

        layout.addWidget(self.detection_excluded_list)

         
        # [4] 匹配时相关设置


        self.add_line_with_text(layout , "匹配时相关设置")

        self.auto_max_val_checkbox = QtWidgets.QCheckBox('自动选择最佳匹配')
        self.auto_max_val_checkbox.setChecked(path_detection_config['auto_max_val'])
        self.auto_max_val_checkbox.stateChanged.connect(lambda *args:  (
            self.modify_config(
                'auto_max_val',
                self.auto_max_val_checkbox.isChecked(),
                'path_detection_config.bin'),self.update_similarity_max_slider_ui()))



        layout.addWidget(self.auto_max_val_checkbox)
        self.auto_max_val_checkbox.setToolTip('如果选中，程序将自动使用最高的相似度值作为匹配阈值，无需手动设置。')

        self.add_line_with_text(layout, '匹配元素权重')

        # 初始化滑杆的权重值
        slider_values = {
            'name_weight': path_detection_config.get('name_weight', 0.25),  # 默认值为0.25
            'resolution_weight': path_detection_config.get('resolution_weight', 0.25),
            'format_weight': path_detection_config.get('format_weight', 0.25),
            'creation_time_weight': path_detection_config.get('creation_time_weight', 0.25),
        }

        # 定义更新权重的函数
        def update_weight(slider_name, value):
            # 更新当前滑杆的值
            current_value = value / 1000.0
            slider_values[slider_name] = current_value

            # 计算剩余的值
            remaining = 1.0 - current_value

            # 获取其他滑杆的名称和当前值
            other_sliders = {k: v for k, v in slider_values.items() if k != slider_name}

            # 计算其他滑杆的总值
            total_other_values = sum(other_sliders.values())

            # 防止除以零的情况
            if total_other_values == 0:
                # 如果其他滑杆的总值为0，平均分配剩余的值
                for key in other_sliders:
                    slider_values[key] = remaining / len(other_sliders)
            else:
                # 按比例调整其他滑杆的值，保持它们之间的相对比例
                for key in other_sliders:
                    proportion = other_sliders[key] / total_other_values
                    slider_values[key] = remaining * proportion

            # 更新UI和配置
            update_ui_and_config()

        # 定义更新UI和配置文件的函数
        def update_ui_and_config():
            # 阻断信号以防止递归调用
            self.name_weight_slider.blockSignals(True)
            self.resolution_weight_slider.blockSignals(True)
            self.format_weight_slider.blockSignals(True)
            self.creation_time_weight_slider.blockSignals(True)

            # 更新滑杆和标签显示
            self.name_weight_slider.setValue(int(slider_values['name_weight'] * 1000))
            self.name_weight_label.setText("{:.3f}".format(slider_values['name_weight']))

            self.resolution_weight_slider.setValue(int(slider_values['resolution_weight'] * 1000))
            self.resolution_weight_label.setText("{:.3f}".format(slider_values['resolution_weight']))

            self.format_weight_slider.setValue(int(slider_values['format_weight'] * 1000))
            self.format_weight_label.setText("{:.3f}".format(slider_values['format_weight']))

            self.creation_time_weight_slider.setValue(int(slider_values['creation_time_weight'] * 1000))
            self.creation_time_weight_label.setText("{:.3f}".format(slider_values['creation_time_weight']))

            # 解除信号阻断
            self.name_weight_slider.blockSignals(False)
            self.resolution_weight_slider.blockSignals(False)
            self.format_weight_slider.blockSignals(False)
            self.creation_time_weight_slider.blockSignals(False)

            # 保存更新后的权重值到配置文件
            self.modify_config('name_weight', slider_values['name_weight'], 'path_detection_config.bin')
            self.modify_config('resolution_weight', slider_values['resolution_weight'], 'path_detection_config.bin')
            self.modify_config('format_weight', slider_values['format_weight'], 'path_detection_config.bin')
            self.modify_config('creation_time_weight', slider_values['creation_time_weight'],
                               'path_detection_config.bin')

        # 名字权重滑杆和标签
        layout.addWidget(QtWidgets.QLabel("名字权重:"))
        name_weight_layout = QtWidgets.QHBoxLayout()
        self.name_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.name_weight_slider.setMinimum(0)
        self.name_weight_slider.setMaximum(1000)
        self.name_weight_slider.setValue(int(slider_values['name_weight'] * 1000))
        name_weight_layout.addWidget(self.name_weight_slider)
        self.name_weight_label = QtWidgets.QLabel("{:.3f}".format(slider_values['name_weight']))
        name_weight_layout.addWidget(self.name_weight_label)
        layout.addLayout(name_weight_layout)
        # 连接滑杆的值变化信号到更新权重函数
        self.name_weight_slider.valueChanged.connect(lambda value: update_weight('name_weight', value))

        # 分辨率权重滑杆和标签
        layout.addWidget(QtWidgets.QLabel("分辨率权重:"))
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

        # 格式权重滑杆和标签
        layout.addWidget(QtWidgets.QLabel("格式权重:"))
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

        # 创建时间权重滑杆和标签
        layout.addWidget(QtWidgets.QLabel("创建时间权重:"))
        creation_time_weight_layout = QtWidgets.QHBoxLayout()
        self.creation_time_weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.creation_time_weight_slider.setMinimum(0)
        self.creation_time_weight_slider.setMaximum(1000)
        self.creation_time_weight_slider.setValue(int(slider_values['creation_time_weight'] * 1000))
        creation_time_weight_layout.addWidget(self.creation_time_weight_slider)
        self.creation_time_weight_label = QtWidgets.QLabel("{:.3f}".format(slider_values['creation_time_weight']))
        creation_time_weight_layout.addWidget(self.creation_time_weight_label)
        layout.addLayout(creation_time_weight_layout)
        self.creation_time_weight_slider.valueChanged.connect(
            lambda value: update_weight('creation_time_weight', value))

        self.add_line_with_text(layout, "相似度的计算")

        # 相似度判断值滑杆和标签
        layout.addWidget(QtWidgets.QLabel("自定义相似度阈值:"))
        similarity_max_layout = QtWidgets.QHBoxLayout()
        self.similarity_max_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.similarity_max_slider.setMinimum(0)
        self.similarity_max_slider.setMaximum(1000)
        self.similarity_max_slider.setValue(int(path_detection_config['similarity_max'] * 1000))
        similarity_max_layout.addWidget(self.similarity_max_slider)
        self.similarity_max_label = QtWidgets.QLabel("{:.3f}".format(path_detection_config['similarity_max']))
        similarity_max_layout.addWidget(self.similarity_max_label)
        layout.addLayout(similarity_max_layout)
        self.similarity_max_slider.setToolTip('请输入相似度阈值（0.0 - 1.0）。程序将匹配相似度高于该阈值的结果。')

        # 连接滑杆的值变化信号到更新函数
        self.similarity_max_slider.valueChanged.connect(
            lambda value: update_slider_value('similarity_max', value)
        )

        # 相似度差异值滑杆和标签
        layout.addWidget(QtWidgets.QLabel("相似度容差范围:"))
        similarity_range_layout = QtWidgets.QHBoxLayout()
        self.similarity_range_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.similarity_range_slider.setMinimum(0)
        self.similarity_range_slider.setMaximum(1000)
        self.similarity_range_slider.setValue(int(path_detection_config['similarity_range'] * 1000))
        similarity_range_layout.addWidget(self.similarity_range_slider)
        self.similarity_range_label = QtWidgets.QLabel("{:.3f}".format(path_detection_config['similarity_range']))
        similarity_range_layout.addWidget(self.similarity_range_label)
        layout.addLayout(similarity_range_layout)
        self.similarity_range_slider.setToolTip(
            '设置匹配阈值的容差范围（0.0 - 1.0）。程序将匹配相似度在阈值上下浮动该范围内的结果。')

        self.similarity_range_slider.valueChanged.connect(
            lambda value: update_slider_value('similarity_range', value)
        )

        # 计算创建天数范围容差值
        layout.addWidget(QtWidgets.QLabel("计算创建天数范围容差值:"))
        day_range_layout = QtWidgets.QHBoxLayout()
        self.day_range_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.day_range_slider.setMinimum(1)
        self.day_range_slider.setMaximum(1000)
        self.day_range_slider.setValue(int(path_detection_config['creation_day_range_tolerance']))
        day_range_layout.addWidget(self.day_range_slider)
        self.day_range_label = QtWidgets.QLabel(str(path_detection_config['creation_day_range_tolerance']))
        day_range_layout.addWidget(self.day_range_label)
        layout.addLayout(day_range_layout)
        self.day_range_slider.setToolTip('test')

        self.day_range_slider.valueChanged.connect(lambda value: (
            self.day_range_label.setText(str(value)),
            self.modify_config('creation_day_range_tolerance'
                               , value,
                               'path_detection_config.bin')))  # 更新配置文件

        # 将path_matching_widget设置为scroll_area的子组件
        scroll_area.setWidget(path_matching_widget)

        # 添加到选项卡
        self.tab_widget.addTab(scroll_area, "节点路径匹配")

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

    def update_similarity_max_slider_ui(self):
        ### 初始化配置数据 这个是为了实时获得最新的
        path_detection_config = self.dataM.bin_load_data(
            os.path.join(settings_path, 'path_detection_config.bin'))

        if path_detection_config['auto_max_val']:
            self.similarity_max_slider.setEnabled(False)
        else:
            self.similarity_max_slider.setEnabled(True)
    # --------------------保存设置内容的函数 开始

    # -----通用
    def modify_config(self, key, cont, file_name = 'texture_processing_data.bin'):

        config = self.dataM.bin_load_data(
            os.path.join(settings_path, file_name))

        config[key] = cont

        self.dataM.bin_save_data(
            os.path.join(settings_path, file_name), config)

    def modify_nested_config(self, value, key_path):
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
        texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin')
        )

        # 根据给定的键路径逐层访问数据
        current_level = texture_processing_data
        for key in key_path[:-1]:  # 遍历到倒数第二个键
            current_level = current_level[key]  # 进入下一层级

        # 设置最终键的值为新值
        current_level[key_path[-1]] = value

        # 保存修改后的配置数据
        self.dataM.bin_save_data(
            os.path.join(settings_path, 'texture_processing_data.bin'),
            texture_processing_data
        )


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
            for channel in self.texture_processing_data['ProcSet_Options']['Magic_Connection_Options']:
                # 检查当前通道（大写）是否在选中的大写值中
                if channel.upper() in selected_values_uppercase:
                    # 如果匹配，更新配置文件为真
                    self.modify_nested_config(True, ['ProcSet_Options', 'Magic_Connection_Options', channel])
                else:
                    # 如果不匹配，更新配置文件为假
                    self.modify_nested_config(False, ['ProcSet_Options', 'Magic_Connection_Options', channel])

            # 重新刷新设置属性
            self.texture_processing_data = self.dataM.bin_load_data(
                os.path.join(settings_path, 'texture_processing_data.bin'))
            # 使用定时器确保 main 函数在事件队列的下一次迭代中执行

        QtCore.QTimer.singleShot(0, main)

    # 修改 texture_filter_fields 过滤配置文件
    def modify_texture_filter_fields_config(self, channel, val):

        # 处理写入值，并强制转为大写
        output_list = [item.strip().upper() for item in val.split(",")]

        # 保存修改值
        self.modify_nested_config(output_list, ['TexFirstFilter', channel])

        # 刷新输入框
        self.texture_filter_fields[channel].setText(
                str(output_list)
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , "))

        # 重新刷新设置属性
        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

    # 修改 color_space_text 过滤配置文件
    def modify_color_space_text_config(self):
        val = self.color_space_text.toPlainText()

        # 处理写入值，并强制转为大写
        output_list = [item.strip() for item in val.split(",")]

        # 保存修改值
        self.modify_nested_config(output_list, ['ColorSpace', 'ColorSpaceData'])

        # 重新刷新设置属性
        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

        # 刷新输入框 (BUG)
        # self.color_space_text.setPlainText(
        #     str(output_list)
        #     .replace('[', '')
        #     .replace(']', '')
        #     .replace("'", "")
        #     .replace(",", " , "))

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
            for channel in self.texture_processing_data['ProcSet_Options']['Auto_Node_Connection_Options']:
                # 检查当前通道（大写）是否在选中的大写值中
                if channel.upper() in selected_values_uppercase:
                    # 如果匹配，更新配置文件为真
                    self.modify_nested_config(True, ['ProcSet_Options', 'Auto_Node_Connection_Options', channel])
                else:
                    # 如果不匹配，更新配置文件为假
                    self.modify_nested_config(False, ['ProcSet_Options', 'Auto_Node_Connection_Options', channel])

            # 使用定时器确保 main 函数在事件队列的下一次迭代中执行

            # 重新刷新设置属性
            self.texture_processing_data = self.dataM.bin_load_data(
                os.path.join(settings_path, 'texture_processing_data.bin'))
        QtCore.QTimer.singleShot(0, main)

    def modify_pro_node_list_config(self, channel, val):
        # 处理写入值，并强制转为大写
        output_list = [item.strip() for item in val.split(",")]

        # 保存修改值
        self.modify_nested_config(output_list, ['ProcSet_Options',
                                                'ProcessingNodeData',
                                                channel, 'NodeList'])

        # 刷新输入框
        self.node_list_edit[channel].setText(
            str(output_list)
            .replace('[', '')
            .replace(']', '')
            .replace("'", "")
            .replace(",", " , "))

        # 重新刷新设置属性
        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

    def add_pro_node_to_list(self, channel):


        # 按住alt键可以清除全部的输入
        if keyboard.is_pressed('alt'):
            output_list = self.texture_processing_data["ProcSet_Options"]["ProcessingNodeData"][channel]["NodeList"]
            output_list.pop()
        else:
            # 获取选择到的节点
            try:
                select_node = list(process_sl_data().keys())[0]
            except AttributeError:
                return self.feedback.CP('添加到处理节点输入框 ->无法获取选择节点数据')

            output_list = self.texture_processing_data["ProcSet_Options"]["ProcessingNodeData"][channel]["NodeList"]
            output_list.append(select_node)

            self.modify_nested_config(output_list, key_path = ['ProcSet_Options', 'ProcessingNodeData', channel, 'NodeList'])

        self.node_list_edit[channel].setText(str(output_list)
        .replace('[', '')
        .replace(']', '')
        .replace("'", "")
        .replace(",", " , "))

        # 重新刷新设置属性
        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

    def replace_license(self):
        win_list = ['ArnoldMagicNodeSettingsPanel',
                    'TextureManagerWin',
                    'TM_FindAndReplace_Win',
                    'TM_RepathFiles_Win',
                    'TM_ImageProcessing_Win'
                    ]
        import LicenseValidator

        for win_obj in win_list:
            try:
                delete_window_if_existe(win_obj)
            except:
                pass

        # 判主窗口是否存在，如果存在则删除
        if cmds.window(AMN_UI_WorkSpaceControl, exists=True):
            cmds.deleteUI(AMN_UI_WorkSpaceControl)

        replace_license = LicenseValidator.LicenseWin()
        replace_license.show()

    # --------------------保存设置内容的函数 结束

# 贴图管理器 使用QT库写的窗口！！！
class TextureManagerWin(QtWidgets.QDialog):

    def __init__(self,parent = MayaMainWindows()):
        super(TextureManagerWin, self).__init__(parent)

        # 初始操作
        # 创建实例类
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData() # 提取数据模块
        self.dataM = DataManager() # 储存模块
        self.dataP = DataProcessor() # 数据处理模块

        self.TextureManager_texture_table_data_temp_path = os.path.join(SCRIPT_PATH, 'Temp', 'TM_texture_table.bin')
        self.TextureManager_config_path = os.path.join(SCRIPT_PATH, 'Datas', 'texture_manager', 'TM_config.bin')

        # 加载语言配置文件，将其解析为Python字典并获取其中的 'language_config' 键的值
        # 'language_config' 是从 'language_config.json' 文件中读取的指定语言（例如: 'en', 'zh'等）
        language_config = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH , 'Datas', 'settings', 'language_config.json') )['language_config']

        # 根据上一步加载的 'language_config'，动态加载相应语言的JSON文件
        # 这个文件应该位于 'Datas/languages' 目录中，文件名与 'language_config' 的值相同（如 'en.json'）
        # 从该语言文件中读取 'DLibs' 键的内容，通常用于加载与该语言相关的库或资源
        self.language = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH , 'Datas', 'languages', f'{language_config}.json') )['ArnoldMagicNode']['TM_WIN']

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

        self.WINDOWS_NAME = f"{self.language['__init__']['WINDOWS_NAME']}  {SoftwareState} : {SoftwareVersion}    {self.language['__init__']['remaining_time']} : {str(LicenseV_remaining_time)}"

        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('TextureManagerWin')



        self.setObjectName('TextureManagerWin')
        self.setWindowTitle(self.WINDOWS_NAME)
        self.setWindowIcon(QtGui.QIcon(icon_path + "\\TXManagerShelf_200.png"))
        #...窗口长宽
        self.setMinimumHeight(700)
        self.setMinimumWidth(1000)









        # 添加隐藏 放大/缩小 几个按钮
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.create_widgets()
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


    def create_widgets(self):
        lang = self.language['create_widgets']

        # MaterialListSearch 搜索框
        self.MaterialListSearch = QtWidgets.QLineEdit()
        self.MaterialListSearch.textChanged.connect(lambda item: self.material_list_search())
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
        self.MaterialList.currentItemChanged.connect(lambda item: self.material_list_clicked())
        self.MaterialList.itemChanged.connect(lambda item: self.material_list_material_rename())
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
        self.TexturelListSearch.textChanged.connect(lambda item: self.texture_list_search())
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
        self.MaterialList_SelectAll_Button = QtWidgets.QPushButton()
        self.MaterialList_SelectAll_Button.setIcon(QtGui.QIcon(icon_path + "\\select_all_icon.png"))
        self.MaterialList_SelectAll_Button.setFixedWidth(40)
        self.MaterialList_SelectAll_Button.setFixedHeight(40)
        self.MaterialList_SelectAll_Button.clicked.connect(lambda *args:  self.all_selected_materials())
        self.MaterialList_SelectAll_Button.setIconSize(QtCore.QSize(38, 38))

        # 取消所有选择
        self.TexturelList_Unselect_All_Button = QtWidgets.QPushButton() # 取消全选 lang['TexturelList_Unselect_All_Button']
        self.TexturelList_Unselect_All_Button.clicked.connect(lambda *args:  (
            self.MaterialList.clearSelection(),
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())
        ))
        self.TexturelList_Unselect_All_Button.setFixedHeight(40)
        self.TexturelList_Unselect_All_Button.setFixedWidth(40)
        self.TexturelList_Unselect_All_Button.setIcon(QtGui.QIcon(
            os.path.join(icon_path , 'deselect_all_icon.png')))
        self.TexturelList_Unselect_All_Button.setIconSize(QtCore.QSize(38, 38))

        # 反选
        self.TexturelList_reverse_selection = QtWidgets.QPushButton() # 反选 lang['TexturelList_reverse_selection']
        self.TexturelList_reverse_selection.setFixedHeight(40)
        self.TexturelList_reverse_selection.setFixedWidth(40)
        self.TexturelList_reverse_selection.setIconSize(QtCore.QSize(42, 42))
        self.TexturelList_reverse_selection.clicked.connect(lambda *args:  self.texture_list_reverse_selection())
        self.TexturelList_reverse_selection.setIcon(QtGui.QIcon(
            os.path.join(icon_path , 'invert_selection_icon.png')
        ))

        # 一键选出所有缺失贴图
        self.TexturelList_Find_Missing_Textures_Button = QtWidgets.QPushButton() # 选出缺失 lang['TexturelList_Find_Missing_Textures_Button']
        self.TexturelList_Find_Missing_Textures_Button.clicked.connect(
            lambda *args:  self.texture_list_find_missing_textures())
        self.TexturelList_Find_Missing_Textures_Button.setFixedHeight(40)
        self.TexturelList_Find_Missing_Textures_Button.setFixedWidth(40)
        self.TexturelList_Find_Missing_Textures_Button.setIconSize(QtCore.QSize(38, 38))
        self.TexturelList_Find_Missing_Textures_Button.setIcon(QtGui.QIcon(
            os.path.join(icon_path , 'select_missing_icon.png')
        ))

        # 选出最大贴图的按钮
        self.TexturelList_Intelligent_Find_Max_Size_Button = QtWidgets.QPushButton() # 选出大贴图 lang['TexturelList_Intelligent_Find_Max_Size_Button']
        self.TexturelList_Intelligent_Find_Max_Size_Button.clicked.connect(
                                                                            lambda *args:  self.texture_list_intelligent_find_max_size(self.dataM.bin_load_data(self.TextureManager_config_path)['listwidget_data']))
        self.TexturelList_Intelligent_Find_Max_Size_Button.setFixedHeight(40)
        self.TexturelList_Intelligent_Find_Max_Size_Button.setFixedWidth(40)
        self.TexturelList_Intelligent_Find_Max_Size_Button.setIconSize(QtCore.QSize(38, 38))
        self.TexturelList_Intelligent_Find_Max_Size_Button.setIcon(QtGui.QIcon(
            os.path.join(icon_path , 'select_large_textures_icon.png')
        ))

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

        # TexturelList 贴图列表
        self.TexturelList = QtWidgets.QTableView()
        TexturelList_Headers = lang['TexturelList_Headers'] # "贴图节点名称", "材质球", "大小", "像素大小", "格式", "引用次数", "状态", "路径"

        # 创建自定义的模型，设置第2到6列不可编辑
        self.TEXTURELIST_MODEL = NonEditableColumnsModel(0, 8, non_editable_columns=[2, 3, 4, 5, 6])
        self.TEXTURELIST_MODEL.setHorizontalHeaderLabels(TexturelList_Headers)

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
        self.TEXTURELIST_MODEL.dataChanged.connect(self.texture_list_texture_update)

        # 设置初始化值
        self.initial_settings()
        # ----------------------------列表 结束

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
        Texture_Search_Layout.addWidget(self.MaterialList_SelectAll_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Unselect_All_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Find_Missing_Textures_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Intelligent_Find_Max_Size_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_reverse_selection)
        Texture_Search_Layout.addWidget(self.tolerance_doubleSpinBox)
        Texture_Search_Layout.addWidget(self.TexturelListSearch)
        Texture_Search_Layout.addWidget(self.TexturelList_Search_And_Replace_Date_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Replace_Data_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Processed_Image_Button)

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
        Main_Layout.addLayout(Target_And_Edit_Area_Layout)

    def initial_settings(self):
        self.tolerance_doubleSpinBox.setValue(self.dataM.bin_load_data(self.TextureManager_config_path)['listwidget_data'])
    # material_list的功能++++++++++++++++++++++++++++++++++开始

    # material list 点击后激活
    def material_list_clicked(self):
        # 使用 QTimer 延迟处理选择

        # 刷新到贴图表格
        QtCore.QTimer.singleShot(0, self.refresh_to_texture_table)

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
            self.feedback.CP('请不要输入非法字符哦！')
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
        temp_TextureManager_texture_table_data = self.dataM.bin_load_data(self.TextureManager_texture_table_data_temp_path)

        texture_list_from_table = []

        # 从加载的数据中提取贴图列表
        for index, val in enumerate(temp_TextureManager_texture_table_data):
            texture_list_from_table.append(val[0])

        texture_list_from_main_dict = []

        # 从材质信息字典中提取所有贴图的列表
        for matName in self.MterialNodeAllInfoDict:
            for texName in self.MterialNodeAllInfoDict[matName]:
                texture_list_from_main_dict.append(texName)

        # 计算反选的贴图列表，即那些在主字典中存在但未在表格数据中出现的贴图
        reverse_selected_texture_list = list(set(texture_list_from_main_dict) - set(texture_list_from_table))

        # 根据反选的贴图列表过滤出对应的材质与贴图字典
        reverse_selected_texture_dict = self.dataP.filter_material_textures(reverse_selected_texture_list, self.MterialNodeAllInfoDict)

        # 为每个反选的贴图找到对应的材质，并准备要添加到表格中的数据
        add_multiple_rows_dict = {}
        reverse_selected_mat_list = []
        for matName in reverse_selected_texture_dict:
            reverse_selected_mat_list.append(matName)
            for texName in reverse_selected_texture_dict[matName]:
                add_multiple_rows_dict[texName] = matName

        # 将反选的贴图数据添加到表格模型中
        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, add_multiple_rows_dict)

        # 设置贴图列表的模型数据
        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 清除材质列表中所有项目的选中状态
        self.MaterialList.clearSelection()

        # 根据反选的材质列表，选择材质列表中对应的项目
        for i in range(self.MaterialList.count()):
            item = self.MaterialList.item(i)
            # 如果项目的文本在反选材质列表中，则选中该项目
            if item.text() in reverse_selected_mat_list:
                item.setSelected(True)

        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, _texture_data_list)

    # 选择缺失贴图
    def texture_list_find_missing_textures(self):
        # 在加载选择对应的行之前先清除之前的
        self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())

        select_texture_dict = {}
        select_matName_list = []
        for matName in self.MterialNodeAllInfoDict:
            for texName in self.MterialNodeAllInfoDict[matName]:
                if self.MterialNodeAllInfoDict[matName][texName]['isLoaded'] == False:
                    select_texture_dict[texName] = matName
                    select_matName_list.append(matName)

        # 先取消MaterialList中所有项目的选中状态
        self.MaterialList.clearSelection()
        
        # 选择出选中的材质
        for i in range(self.MaterialList.count()):
            item = self.MaterialList.item(i)
            # 如果项目的文本在select_texture_list中，就选择它
            if item.text() in select_matName_list:
                item.setSelected(True)

        _texture_data_list = self.add_multiple_rows(self.TEXTURELIST_MODEL, select_texture_dict)

        self.TexturelList.setModel(self.TEXTURELIST_MODEL)

        # 每次刷新贴图表格就把贴图表格的数据写到临时文件里
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
        tm_FindAndReplaceWin.base_data_signal.connect(self.replace_base_data_and_refresh_ui)
        tm_FindAndReplaceWin.base_data_bundle_signal.connect(self.replace_path_data_and_refresh_ui)

    def find_path_re_Win(self):
        tm_RepathFiles = TM_RepathFiles(self.WINDOWS_NAME, parent=self)
        tm_RepathFiles.show()

        tm_RepathFiles.new_MterialNodeAllInfoDict_signal.connect(self.replace_path_data_and_refresh_ui)

    def image_processing_Win(self):
        tm_ImageProcessing = TM_ImageProcessing(self.WINDOWS_NAME, parent=self)
        tm_ImageProcessing.show()

        tm_ImageProcessing.new_MterialNodeAllInfoDict_signal.connect(self.replace_path_data_and_refresh_ui)

    # 其他窗口-----------------------------------------结束
    def state_set_background_colors(self, model):
        # 遍历模型中的每一行
        for row in range(model.rowCount()):
            # 获取第六列（索引为5）的值
            status_item = model.item(row, 6)
            status_value = status_item.text()

            if status_value == "正常":
                # 更细致的绿色 (RGB: 34, 177, 76) 和 50% 透明度
                color = QtGui.QColor(34, 177, 76, 128)  # RGB + Alpha
            elif status_value == "缺失":
                # 更细致的红色 (RGB: 237, 28, 36) 和 50% 透明度
                color = QtGui.QColor(237, 28, 36, 128)  # RGB + Alpha
            else:
                color = QtGui.QColor(255, 255, 255, 255)  # 默认颜色，白色，不透明



            # # 设置整行的背景颜色
            # for col in range(model.columnCount()):
            #   item = model.item(row, col)
            #   item.setData(color, QtCore.Qt.BackgroundRole)


            # 设置第六行的背景颜色
            item = model.item(row, 6)

            item.setData(color, QtCore.Qt.BackgroundRole)

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
                    isLoaded = '正常'
                else:
                    isLoaded = '缺失'

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

    def test(self):
        print(self.MterialNodeAllInfoDict)

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

        # 把刷新的贴图数据存入缓存中
        self.dataM.bin_save_data(self.TextureManager_texture_table_data_temp_path, TextureManager_texture_table_data)

        # 刷新表格
        self.refresh_texture_table()

# 贴图管理器的搜索与替换界面
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

        self.config_path = os.path.join(SCRIPT_PATH, 'Datas', 'texture_manager', 'TM_find_and_replace_config.bin') # 历史写入路径

        # 加载语言配置文件并获取 'language_config' 键的值
        language_config = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'settings', 'language_config.json'))['language_config']

        # 动态加载相应语言的JSON文件，并读取 'ArnoldMagicNode' 中的 'TM_FAR_WIN' 键
        self.language = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'languages', f'{language_config}.json'))['ArnoldMagicNode']['TM_FAR_WIN']

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
            self.modify_config('modify_content_options', self.select_group.id(button)),
            self.select_group_logic(self.select_group.id(button))
        ))
        # 使用编号选中按钮（这里选中ID为1的按钮）
        # self.select_button_by_id(self.group1, 1)

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
        modify_content_layout = QtWidgets.QVBoxLayout()
        modify_content_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        modify_content_layout.addWidget(self.label_find)
        modify_content_layout.addWidget(self.line_edit_find)
        modify_content_layout.addWidget(self.label_replace)
        modify_content_layout.addWidget(self.line_edit_replace)

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

    def select_group_logic(self, cont):
        if cont == 1:
            self.radio_table.setEnabled(False)
            self.modify_config('radio_table_enabled', False)
        else:
            self.radio_table.setEnabled(True)
            self.modify_config('radio_table_enabled', True)

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

        self.radio_table.setEnabled(self.dataM.bin_load_data(self.config_path)['radio_table_enabled'])

        self.line_edit_find.setText(self.dataM.bin_load_data(self.config_path)['search_content'])
        self.line_edit_replace.setText(self.dataM.bin_load_data(self.config_path)['replace_content'])

        self.checkbox_case_sensitive.setChecked(self.dataM.bin_load_data(self.config_path)['case_sensitive'])
        self.checkbox_regex.setChecked(self.dataM.bin_load_data(self.config_path)['use_regex'])

    def replace_button(self):
        # 初始化默认变量
        config = self.dataM.bin_load_data(self.config_path)

        # 访问继承TextureManagerWin里面最新的MterialNodeAllInfoDict
        TM_MterialNodeAllInfoDict = self.TextureManagerWin.MterialNodeAllInfoDict

        # 获取零时数据
        temp_TextureManager_texture_table_data = self.dataM.bin_load_data(self.TextureManagerWin.TextureManager_texture_table_data_temp_path)

        tex_filter_list = []
        mat_filter_list = []
        # 1，全选
        if config['modify_scope_options'] == 1:
            MterialNodeAllInfoDict = TM_MterialNodeAllInfoDict

        # 2，选择表格内的数据
        elif config['modify_scope_options'] == 2:
            MterialNodeAllInfoDict = TM_MterialNodeAllInfoDict

            # 获取出表格中的所有贴图名称
            for index, value in enumerate(temp_TextureManager_texture_table_data):
                tex_filter_list.append(temp_TextureManager_texture_table_data[index][0])

        # 3，表格内选择的数据
        elif config['modify_scope_options'] == 3:
            MterialNodeAllInfoDict = TM_MterialNodeAllInfoDict

            # 获取出表格中
            selected_indexes = self.TextureManagerWin.TexturelList.selectionModel().selectedRows()
            if selected_indexes:
                # 用于存储所有选中行的数据
                all_selected_rows_data = []

                for index in selected_indexes:
                    selected_row = index.row()

                    # 获取该行的所有列内容
                    row_data = []
                    for column in range(self.TextureManagerWin.TEXTURELIST_MODEL.columnCount()):
                        cell_value = self.TextureManagerWin.TEXTURELIST_MODEL.index(selected_row, column).data()
                        row_data.append(cell_value)

                    # 将该行数据添加到所有选中行的数据列表中
                    all_selected_rows_data.append(row_data)
            else:
                self.feedback.CP("没有选中任何行")

            for index, value in enumerate(all_selected_rows_data):
                tex_filter_list.append(value[0])

            MaterialList_selected_items = self.TextureManagerWin.MaterialList.selectedItems()  # 获取所有选中的项
            mat_filter_list = [item.text() for item in MaterialList_selected_items]  # 获取选中项的文本列表

        # # 材质列表使用 set 去重（保留顺序）
        # mat_filter_list = list(dict.fromkeys(mat_filter_list))


        # 1，是修改材质
        if config['modify_content_options'] == 1:
            # 初始化一个新的字典，用于存储修改后的材质信息
            new_MterialNodeAllInfoDict = {}
            # 遍历现有的材质信息字典
            for matName, value in MterialNodeAllInfoDict.items():

                # 如果修改范围选项为3，则只修改过滤列表中的材质
                if config['modify_scope_options'] == 3:
                    # 检查材质名称是否在过滤列表中
                    if matName in mat_filter_list:
                        newContent = self.dataP.SimpleSearchAndReplaceData(matName,
                                                                           self.line_edit_find.text(),
                                                                           self.line_edit_replace.text(),
                                                                           config['case_sensitive'], config['use_regex'])
                    else:
                        newContent = matName
                    # 对所有材质进行查找和替换
                else:
                    newContent = self.dataP.SimpleSearchAndReplaceData(matName, self.line_edit_find.text(),
                                                                       self.line_edit_replace.text(),
                                                                      config['case_sensitive'], config['use_regex'])
                # 材质重命名
                try:
                    cmds.rename(matName, newContent)

                except RuntimeError:
                    self.feedback.CP('无法重命名只读节点:'+ str(newContent))

                    # 如果无法更改名称将会使用原来的名称
                    newContent = matName

                except :
                    self.feedback.CP("你的修改名称有非法字符:" + str(newContent) + a)

                    # 如果无法更改名称将会使用原来的名称
                    newContent = matName

                # 重构字典
                if not matName == newContent:
                    # 如果内容不一样就更新新的材质新名称进去
                    new_MterialNodeAllInfoDict[newContent] = value
                else:
                    # 如果内容一样就用之前的值继续重构
                    new_MterialNodeAllInfoDict[matName] = value

                # 修改零时缓存数据
                for index, value in enumerate(temp_TextureManager_texture_table_data):
                    if temp_TextureManager_texture_table_data[index][1] == matName:
                        temp_TextureManager_texture_table_data[index][1] = newContent

            # 重新保存修改过后的零时表格数据
            self.dataM.bin_save_data(self.TextureManagerWin.TextureManager_texture_table_data_temp_path, temp_TextureManager_texture_table_data)

            # 激活一次讯号到主窗口，并把修改好的字典传递回去
            self.base_data_signal.emit(new_MterialNodeAllInfoDict)

        # 2，是修改贴图名称
        elif config['modify_content_options'] == 2:
            # 修改完构建新字典的空字典
            new_MterialNodeAllInfoDict = {}



            for matName, matData in MterialNodeAllInfoDict.items():
                # 重构字典内容 先写入材质名称
                new_MterialNodeAllInfoDict[matName] = {}

                for texName, texData in MterialNodeAllInfoDict[matName].items():
                    if config['modify_scope_options'] in [2, 3]:
                        # 检查贴图名称是否在过滤列表中
                        if texName in tex_filter_list:
                            newContent = self.dataP.SimpleSearchAndReplaceData(texName,
                                                                               self.line_edit_find.text(),
                                                                               self.line_edit_replace.text(),
                                                                               config['case_sensitive'],
                                                                               config['use_regex'])
                        else:
                            newContent = texName

                        # 对所有材质进行查找和替换
                    else:
                        newContent = self.dataP.SimpleSearchAndReplaceData(texName,
                                                                           self.line_edit_find.text(),
                                                                           self.line_edit_replace.text(),
                                                                           config['case_sensitive'],
                                                                           config['use_regex'])
                    # 修改贴图名称
                    try:
                        cmds.rename(texName, newContent)

                    except RuntimeError:
                        self.feedback.CP('无法重命名只读节点:'+ str(newContent))

                        # 如果无法更改名称将会使用原来的名称
                        newContent = texName

                    # 重构字典内容 写入贴图名称 还有贴图的相关信息 如果名称一样就用回之前的名称，不一样就用新的名称
                    if texName == newContent:
                        new_MterialNodeAllInfoDict[matName][texName] = texData
                    else:
                        new_MterialNodeAllInfoDict[matName][newContent] = texData


                    # 修改零时缓存数据
                    for index, value in enumerate(temp_TextureManager_texture_table_data):
                        if temp_TextureManager_texture_table_data[index][0] == texName:
                            temp_TextureManager_texture_table_data[index][0] = newContent
                # 重新保存修改过后的零时表格数据
            self.dataM.bin_save_data(self.TextureManagerWin.TextureManager_texture_table_data_temp_path,  temp_TextureManager_texture_table_data)

            # 激活一次讯号到主窗口，并把修改好的字典传递回去
            self.base_data_signal.emit(new_MterialNodeAllInfoDict)

        # 3，是修改路径
        elif config['modify_content_options'] == 3:

            # 修改完构建新字典的空字典
            new_MterialNodeAllInfoDict = MterialNodeAllInfoDict

            # 修改完后的新数据空字典，暂时储存。   作用是更新列表中的大小 链接状况等的内容
            new_tex_tabl_temp_data = {}

            update_dict = {}

            for matName, matData in MterialNodeAllInfoDict.items():
                for texName, texData in matData.items():

                    # 旧的地址
                    old_path = MterialNodeAllInfoDict[matName][texName]['Path']

                    if config['modify_scope_options'] in [2, 3]:
                        # 检查贴图名称是否在过滤列表中
                        if texName in tex_filter_list:
                            # 搜索修改完的新内容
                            newContent = self.dataP.SimpleSearchAndReplaceData(old_path,
                                                                               self.line_edit_find.text(),
                                                                               self.line_edit_replace.text(),
                                                                               config['case_sensitive'],
                                                                               config['use_regex'])
                        else:
                            newContent = old_path

                        # 对所有材质进行查找和替换
                    else:
                        newContent = self.dataP.SimpleSearchAndReplaceData(old_path,
                                                                           self.line_edit_find.text(),
                                                                           self.line_edit_replace.text(),
                                                                           config['case_sensitive'],
                                                                           config['use_regex'])

                    # 修改贴图名称 在不同的情况下才会修改（也就是修改了内容才会修改内容，没有需改的则不修改）
                    if not old_path == newContent:
                        # 把修改了的贴图记录到new_tex_tabl_temp_data字典中
                        new_tex_tabl_temp_data[matName] = texName

                        try:
                            cmds.setAttr(f"{texName}.fileTextureName", newContent , type="string")
                        except :
                            pass

                        # 修改字典中的路径
                        new_MterialNodeAllInfoDict[matName][texName]['Path'] = newContent

                        # 写入需要更新的节点
                        update_dict[texName] = matName

            new_MterialNodeAllInfoDict  = self.getnodedata.TM_StickerUpdateStatusDict(update_dict, new_MterialNodeAllInfoDict)

            # 获取当前表格中都有那些贴图
            table_tex_list = []
            for index, key in enumerate(temp_TextureManager_texture_table_data):
                table_tex_list.append(temp_TextureManager_texture_table_data[index][0])

            # 把表格中有的贴图做成的列表在总信息中筛选出来
            select_texture_dict = {}
            for index, table_list in enumerate(temp_TextureManager_texture_table_data):
                select_texture_dict[temp_TextureManager_texture_table_data[index][0]] = temp_TextureManager_texture_table_data[index][1]

            # 激活一次讯号到主窗口，并把修改好的字典传递回去
            self.base_data_bundle_signal.emit(new_MterialNodeAllInfoDict, select_texture_dict)



    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.config_path)

        config[key] = cont

        self.dataM.bin_save_data(self.config_path, config)
    # --------------------保存设置内容的函数

# 贴图管理器的寻找路径修复界面
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

        # 3. 创建布局
        self.create_layouts()

        # 4. 初始化控件
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


        # 加载语言配置文件，将其解析为Python字典并获取其中的 'language_config' 键的值
        # 'language_config' 是从 'language_config.json' 文件中读取的指定语言（例如: 'en', 'zh'等）
        language_config = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'settings', 'language_config.json'))['language_config']

        # 根据上一步加载的 'language_config'，动态加载相应语言的JSON文件
        # 这个文件应该位于 'Datas/languages' 目录中，文件名与 'language_config' 的值相同（如 'en.json'）
        # 从该语言文件中读取 'DLibs' 键的内容，通常用于加载与该语言相关的库或资源
        self.language = self.dataM.ascii_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'languages', f'{language_config}.json'))['ArnoldMagicNode']['TM_RF_WIN']


        self.TM_repath_files_config_FilePath = os.path.join(SCRIPT_PATH, "Datas", "texture_manager", "TM_repath_files_config.bin")

        # 如果TM_repath_files_config配置文件不存在会重新创建一次
        if not os.path.exists(self.TM_repath_files_config_FilePath):
            self.dataM.bin_save_data(self.TM_repath_files_config_FilePath, TM_RepathFiles_config_dict)

    # 创建控件
    def create_widgets(self):
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setFixedHeight(40)
        self.path_edit.textChanged.connect(lambda text: self.modify_config('path_edit', text))

        self.select_folder_button = QtWidgets.QPushButton('. . .')
        self.select_folder_button.setFixedHeight(38)
        self.select_folder_button.setFixedWidth(35)
        self.select_folder_button.clicked.connect(lambda *args: self.select_folder())

        self.memory_search_mode_checkbox = QtWidgets.QCheckBox(
            self.language['create_widgets']['memory_search_mode_checkbox'])  # 记忆搜索模式
        self.memory_search_mode_checkbox.setEnabled(False)

        self.search_subfolders_checkbox = QtWidgets.QCheckBox(self.language['create_widgets']['search_subfolders_checkbox']) # 搜索子文件夹
        self.search_subfolders_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('search_subfolders_checkbox', self.search_subfolders_checkbox.isChecked()))

        self.multiple_subfolder_search_checkbox = QtWidgets.QCheckBox(self.language['create_widgets']['multiple_subfolder_search_checkbox']) # 多个子文件夹搜索
        self.multiple_subfolder_search_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('multiple_subfolder_search_checkbox', self.multiple_subfolder_search_checkbox.isChecked()))

        self.ignore_case_checkbox = QtWidgets.QCheckBox(self.language['create_widgets']['ignore_case_checkbox']) # 忽略大小写
        self.ignore_case_checkbox.stateChanged.connect(
            lambda *args:  self.modify_config('ignore_case_checkbox', self.ignore_case_checkbox.isChecked()))

        self.fix_path_button = QtWidgets.QPushButton(self.language['create_widgets']['fix_path_button'])
        self.fix_path_button.clicked.connect(lambda *args:  self.fix_path())

    # 创建布局
    def create_layouts(self):

        # 路径输入的窗口文件夹
        path_list_layout = QtWidgets.QHBoxLayout()
        path_list_layout.addWidget(self.path_edit)
        path_list_layout.addWidget(self.select_folder_button)
        # 配置选项输入
        config_checkbox_01 = QtWidgets.QHBoxLayout()
        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        config_checkbox_01.addWidget(self.memory_search_mode_checkbox)

        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        config_checkbox_01.addWidget(self.search_subfolders_checkbox)

        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        config_checkbox_01.addWidget(self.multiple_subfolder_search_checkbox)

        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        config_checkbox_01.addWidget(self.ignore_case_checkbox)

        config_checkbox_01.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))

        # 按钮
        button_01 = QtWidgets.QHBoxLayout()
        button_01.addWidget(self.fix_path_button)

        MainLayout = QtWidgets.QVBoxLayout(self)
        MainLayout.addLayout(path_list_layout)
        MainLayout.addLayout(config_checkbox_01)
        MainLayout.addLayout(button_01)

    # 初始化控件设置
    def initial_widgets_settings(self):
        self.path_edit.setText(self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['path_edit'])

        self.search_subfolders_checkbox.setChecked(self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['search_subfolders_checkbox'])
        self.multiple_subfolder_search_checkbox.setChecked(self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['multiple_subfolder_search_checkbox'])
        self.ignore_case_checkbox.setChecked(self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['ignore_case_checkbox'])

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

    # 寻找文件夹并修复确实文件夹
    def fix_path(self):
        # -----------------------------初始化 获取基本数据
        # 获取输入的路径
        path = self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['path_edit']

        # 判断输入路径是否存在
        if not os.path.exists(path):
            return self.feedback.CP('输入的路径不存在')

        # 从主窗口获取的材质所有数据
        old_MterialNodeAllInfoDict = self.TextureManagerWin.MterialNodeAllInfoDict

        # 初始化两个字典：
        # loaded_failed_tex_dict 用于存储连接失败的贴图信息，键为贴图的文件名（basename），值为贴图相关信息的列表
        loaded_failed_tex_dict = {}  # 连接失败的贴图字典

        # same_path_dict 用于存储具有相同文件名但不同路径的贴图信息，键为贴图的文件名，值为使用该文件名的纹理名称列表
        same_path_dict = {}  # 相同路径的字典

        # 遍历所有材质及其对应的贴图信息
        for MatName in old_MterialNodeAllInfoDict:
            for TexName, Contents in old_MterialNodeAllInfoDict[MatName].items():
                # 检查当前贴图是否未成功加载
                if not Contents['isLoaded'] == True:
                    # 获取贴图文件的基本名称（不含路径）
                    tex_file_name = os.path.basename(Contents['Path'])

                    # 判断该文件名是否已经存在于连接失败的贴图字典中
                    if tex_file_name in loaded_failed_tex_dict:
                        # 如果存在，说明有重复的贴图文件名，需要记录这些具有相同文件名的贴图
                        # 首先检查 same_path_dict 是否已经有该文件名的记录
                        if tex_file_name not in same_path_dict:
                            # 如果还没有记录，初始化一个空列表用于存储使用该文件名的纹理名称
                            same_path_dict[tex_file_name] = []
                        # 将当前纹理名称添加到对应文件名的列表中
                        same_path_dict[tex_file_name].append([TexName, MatName])
                    else:
                        # 如果该文件名尚未存在于连接失败的贴图字典中，添加新的条目
                        # 值列表包含纹理名称、材质名称以及原始路径
                        loaded_failed_tex_dict[tex_file_name] = [TexName, MatName, Contents['Path']]

        # 判断输入路径是否存在
        if not loaded_failed_tex_dict:
            return self.feedback.CP('没有连接失败的贴图')

        extensions = [
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif',
            '.raw','.tga', '.exr'
        ]



        start_time = time.time()
        # 寻找路径下的内容
        path_contenes = self.getnodedata.GetDirectoryContentsWithOptions(
            path,
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['search_subfolders_checkbox'],
            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['multiple_subfolder_search_checkbox'],
            extensions
            )


        get_path_contenes_time = time.time() - start_time




        correct_path_dictionary = self.dataP.searchKeysInDictUsingAhoCorapy(loaded_failed_tex_dict,
                                                                            path_contenes,
                                                                            self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)['ignore_case_checkbox'])


        if correct_path_dictionary == {}:
            return self.feedback.CP("没有寻找到对应的贴图文件")


        find_time = time.time() - start_time - get_path_contenes_time

        self.feedback.CP('查询文件夹过程时间：'+ format(get_path_contenes_time, '.2f'))
        self.feedback.CP('寻找对比过程时间：' + format(find_time, '.2f'))

        # update_dict字典是为了储存接下来需要更新主数据
        update_dict = {}


        for texFileName in correct_path_dictionary:
            # 获取失败贴图对应的节点名称、材质名称和旧路径
            node_name = loaded_failed_tex_dict[texFileName][0]  # 节点名称
            mat_name = loaded_failed_tex_dict[texFileName][1]  # 材质名称
            old_path = loaded_failed_tex_dict[texFileName][2]  # 旧路径（修正索引为2）
            new_path = correct_path_dictionary[texFileName]  # 新路径

            try:
                # 更新主节点的贴图路径
                cmds.setAttr(f"{node_name}.fileTextureName", new_path, type="string")
            except Exception as e:
                print(f"更新节点 {node_name} 失败: {e}")

            # 写入更新的node_name(节点名称)
            update_dict[node_name] = mat_name

            # 把旧总数据字典中的path（路径）更新成新替换完成的路径
            old_MterialNodeAllInfoDict[mat_name][node_name]['Path'] = new_path

            # 如果存在相同文件名的其他节点，逐一更新其贴图路径
            if texFileName in same_path_dict:


                for duplicate_node_list in same_path_dict[texFileName]:

                    try:
                        cmds.setAttr(f"{duplicate_node_list[0]}.fileTextureName", new_path, type="string")
                    except Exception as e:
                        print(f"更新节点 {duplicate_node_list[0]} 失败: {e}")

                    # 写入更新的node_name(节点名称)
                    update_dict[duplicate_node_list[0]] = duplicate_node_list[1]
                    # 把旧总数据字典中的path（路径）更新成新替换完成的路径
                    old_MterialNodeAllInfoDict[duplicate_node_list[1]][duplicate_node_list[0]]['Path'] = new_path


        new_MterialNodeAllInfoDict = self.getnodedata.TM_StickerUpdateStatusDict(update_dict, old_MterialNodeAllInfoDict)


        # 获取零时的表格列表数据
        temp_TextureManager_texture_table_data = self.dataM.bin_load_data(self.TextureManagerWin.TextureManager_texture_table_data_temp_path)

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
        self.new_MterialNodeAllInfoDict_signal.emit(new_MterialNodeAllInfoDict, select_texture_dict)

    def test(self):
        pass



    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.TM_repath_files_config_FilePath)

        config[key] = cont

        self.dataM.bin_save_data(self.TM_repath_files_config_FilePath, config)
    # --------------------保存设置内容的函数

# 贴图管理器的图像处理界面 支持转换格式和压缩图像
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
        WINDOWS_NAME =  '图像处理-' + WinName #Win名称

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
        self.TM_image_processing_config_FilePath = os.path.join(SCRIPT_PATH, "Datas", "texture_manager",
                                                            "TM_image_processing_config.bin")

        # 如果TM_image_processing_config配置文件不存在会重新创建一次
        if not os.path.exists(self.TM_image_processing_config_FilePath):
            self.dataM.bin_save_data(self.TM_image_processing_config_FilePath, TM_ImageProcessing_config_dict)



        # TM_ImageProcessing的缓存文件路径
        self.TM_image_processing_cache_FilePath = os.path.join(SCRIPT_PATH, "Datas", "texture_manager",
                                                            "TM_image_processing_cache.bin")

        # 如果TM_image_processing_cache缓存文件不存在会重新创建一次
        if not os.path.exists(self.TM_image_processing_cache_FilePath):
            self.dataM.bin_save_data(self.TM_image_processing_cache_FilePath, image_processing_cache_dict)

    def menu_widgets(self):
        # 创建菜单栏
        self.menu_bar = QtWidgets.QMenuBar(self)

        # 创建“编辑”菜单
        self.edit_menu = self.menu_bar.addMenu("编辑")

        self.clear_cache = QAction("清除缓存  ！谨慎删除！", self)
        self.clear_cache.triggered.connect(lambda *args: os.remove(self.TM_image_processing_cache_FilePath))

        self.redo_action = QAction("还原图像", self)

        self.edit_menu.addAction(self.clear_cache)
        self.edit_menu.addAction(self.redo_action)



        self.help_menu = self.menu_bar.addMenu("帮助")

        self.instructions_action = QAction("使用说明", self)
        self.help_menu.addAction(self.instructions_action)

    def create_widgets(self):
        common_font = QtGui.QFont()
        common_font.setPointSize(SMALL_FONT_SIZE)




        self.format_combo_box_label = QtWidgets.QLabel("格式：")

        format_list = ['jpg', 'png', 'tif', 'bmp']
        self.format_combo_box = QtWidgets.QComboBox()
        self.format_combo_box.addItems(format_list)  # 添加选项
        self.format_combo_box.currentTextChanged.connect(lambda *args: (
            self.modify_config('format', self.format_combo_box.currentText()), # 存入数据
            self.update_quality_controls_visibility()))


        # 创建一个显示输入结果的 QLabel
        self.zoom_ratios_combo_box_label = QtWidgets.QLabel("缩放：")

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
        self.resampling_mode_combo_box_label = QtWidgets.QLabel("重新取样：")

        # 重采样的模式
        resampling_mode_list = ['最近邻插值', '双线性插值', '三次插值', 'Lanczos 插值', '区域插值', '填充插值外点', '逆映射插值']
        self.resampling_combo_box = QtWidgets.QComboBox()
        self.resampling_combo_box.addItems(resampling_mode_list)  # 添加选项
        self.resampling_combo_box.currentTextChanged.connect(lambda *args: self.modify_config(
            'resampling_mode', self.resampling_combo_box.currentIndex()))

        self.jpg_label = QtWidgets.QLabel("JPG的品质: ")

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


        self.png_label = QtWidgets.QLabel("PNG的品质: ")

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



        self.convert_format_check_box = QtWidgets.QCheckBox('转换格式')
        self.convert_format_check_box.clicked.connect(
            lambda *args: self.modify_config('convert_format', self.convert_format_check_box.isChecked()))

        self.scale_texture_check_box = QtWidgets.QCheckBox('缩放贴图')
        self.scale_texture_check_box.clicked.connect(
            lambda *args:  self.modify_config('scale_texture', self.scale_texture_check_box.isChecked()))



        self.conversion_button = QtWidgets.QPushButton('开始转换')
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
        Main_Layout.addLayout(radio_button)
        Main_Layout.addLayout(conversion_layout)


        # 设置窗口的主布局
        self.setLayout(Main_Layout)

    def initial_widgets_settings(self):
        initial_config = self.dataM.bin_load_data(self.TM_image_processing_config_FilePath)

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
            self.feedback.CP("没有选中任何行")
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
                self.feedback.CP("复制备份文件时出错")
                print(e)
                return

    # 修改文件命格式
    def modify_file_extension(self, file_path, new_extension):
        # 获取文件名和目录
        directory, file_name = os.path.split(file_path)
        # 修改文件扩展名
        new_file_name = os.path.splitext(file_name)[0] + '.' + new_extension
        # 返回新的完整路径
        return os.path.join(directory, new_file_name)

    # 转换格式按钮
    def image_conversion(self):

        # 缓存文件
        cache_data = self.dataM.bin_load_data(self.TM_image_processing_cache_FilePath)
        # 配置文件
        initial_config = self.dataM.bin_load_data(self.TM_image_processing_config_FilePath)

        # 写入图片缓存数据
        def write_image_processing_cache(old_extension, backup_image_file_path):
            # 获取文件名称
            tex_file_name = os.path.basename(backup_image_file_path)

            # 分离文件名和扩展名
            tex_file_name_without_extension, tex_file_name_extension = os.path.splitext(tex_file_name)

            # 检查 cache_data 中是否存在该文件名
            if tex_file_name_without_extension not in cache_data:
                # 如果不存在，创建新的条目
                cache_data[tex_file_name_without_extension] = [old_extension,
                                                               tex_file_name_extension,
                                                               backup_image_file_path]
            else:
                # 如果已存在，修改扩展名和备份文件路径
                cache_data[tex_file_name_without_extension][1] = tex_file_name_extension
                cache_data[tex_file_name_without_extension][2] = backup_image_file_path

            # 保存缓存文件
            self.dataM.bin_save_data(self.TM_image_processing_cache_FilePath, cache_data)



        # 如果没有勾选转换格式和缩放比例那不会有任何操作，会直接退出函数
        if not initial_config.get('convert_format', False) and not initial_config.get('scale_texture', False):
            return  # 如果两者都是 False，直接 return

        # 如果没有选中内容不会执行
        if self.get_selected_rows_data() == []:
            return



        # 图像处理后的后缀名称
        image_processed_suffix = initial_config['processed_suffix']


        # 从主窗口获取的材质所有数据
        old_MterialNodeAllInfoDict = self.TextureManagerWin.MterialNodeAllInfoDict


        # 输出格式与扩展名映射
        format_mapping = {
            'jpg': 'jpg',
            'jpeg': 'jpg',
            'png': 'png',
            'tif': 'tif',
            'bmp': 'bmp',
        }

        need_update_dict = {}

        for val in self.get_selected_rows_data():

            old_info_path = old_MterialNodeAllInfoDict[val[1]][val[0]]['Path']

            # 如果路径不存在会直接跳过这个循环
            if not os.path.exists(old_info_path):
                self.feedback.CP('你的这张图片路径连接失败： ' + old_info_path)
                continue

            # 判断目前表格中的文件名称是否已经包含后缀
            if image_processed_suffix in os.path.basename(old_info_path):
                old_info_path = old_info_path.replace("_TM_processed", "")

            # -----------------
            old_tex_name = os.path.basename(old_info_path)
            # 分离文件名和扩展名
            old_tex_name_without_extension, old_tex_extension = os.path.splitext(old_tex_name)
            old_dir_path = os.path.dirname(old_info_path)


            # old_tex_name 带格式的旧贴图名称
            # old_tex_name_without_extension 不带格式的旧贴图名称
            # old_tex_extension 旧贴图格式
            # old_dir_path # 这是旧贴图路径
            # -----------------



            # 添加后缀并生成新的文件路径
            backup_image_file_path = os.path.normpath(
                f"{os.path.join(old_dir_path, old_tex_name_without_extension)}{image_processed_suffix}{old_tex_extension}")

            # 缓存中的图像的文件名（不带扩展名）
            backup_image_name = old_tex_name_without_extension + image_processed_suffix

            # 检查缓存中是否存在相同的备份图像
            if backup_image_name in cache_data:
                if cache_data[backup_image_name][0] != old_tex_extension:
                    cache_ori_path = self.modify_file_extension(old_info_path, cache_data[backup_image_name][0])
                    if os.path.exists(cache_ori_path):
                        old_info_path = cache_ori_path

            # 判断处理过的名称格式是否和这次选择的格式名称一样，如果一样就删除掉之前的格式名称，防止残留文件
            # 如果缓存中存在同名的图像文件
            if backup_image_name in cache_data:
                cached_old_format , cached_format, cached_file_path = cache_data[backup_image_name]
                # 如果缓存的文件格式与当前选择的格式不同
                if cached_format != initial_config['format']:
                    # 删除旧的缓存文件，防止残留文件
                    if os.path.exists(cached_file_path):
                        try:
                            os.remove(cached_file_path)  # 删除旧的缓存文件
                        except Exception as e:
                            self.feedback.CP('无法删除{}残留文件，原因：{}'.format(cached_file_path, e))



            # 检查是否需要转换格式
            if initial_config['convert_format']:

                # 根据输出格式生成输出路径
                if initial_config['format'] in format_mapping:
                    # 通过分割文件名，去掉原文件扩展名，并添加新的扩展名
                    backup_image_file_path = f"{backup_image_file_path.rsplit('.', 1)[0]}.{format_mapping[initial_config['format']]}"
                else:
                    # 如果格式不被支持，输出反馈信息并返回
                    self.feedback.CP(f"不支持的格式: {initial_config['format']}")
                    return

                # 执行格式转换，使用备份图像文件名作为输入和输出路径
                self.imageP.convert_image_format(input_path=old_info_path,
                                                 output_path=backup_image_file_path,
                                                 output_format=initial_config['format'],
                                                 jpg_quality=initial_config['JPG_quality'],
                                                 png_compression=initial_config['PNG_quality'])
                # 如果需要缩放，则在转换格式后进行缩放
                if initial_config['scale_texture']:
                    resize_image_state = self.imageP.resize_image(input_path=backup_image_file_path,
                                                                 output_path=backup_image_file_path,
                                                                 scale_percent=int(initial_config['zoom']),
                                                                 resample_mode=str(initial_config['resampling_mode']))
                    if resize_image_state == False:
                        continue

                # 写入缓存
                write_image_processing_cache(val[4], backup_image_file_path)

            # 如果没有进行格式转换，但需要缩放，则直接缩放
            elif initial_config['scale_texture']:
                resize_image_state = self.imageP.resize_image(input_path=old_info_path,
                                                             output_path=backup_image_file_path,
                                                             scale_percent=int(initial_config['zoom']),
                                                             resample_mode=str(initial_config['resampling_mode']))
                # 如果图片处理返回False直接退出循环
                if resize_image_state == False:
                    continue


                # 写入缓存
                write_image_processing_cache(val[4], backup_image_file_path)

            # 更新节点为新的路径
            try:
                cmds.setAttr(f"{val[0]}.fileTextureName", backup_image_file_path, type="string")
            except Exception as e:
                print(f"更新节点 {val[0]} 失败: {e}")

            # 最后一部 修改主窗口缓存数据
            old_MterialNodeAllInfoDict[val[1]][val[0]]['Path'] = backup_image_file_path

            # 把更新目标写入字典
            need_update_dict[val[0]] = val[1]

        # 更新主窗口字典数据
        new_MterialNodeAllInfoDict = self.getnodedata.TM_StickerUpdateStatusDict(need_update_dict,
                                                                                 old_MterialNodeAllInfoDict)

        # 把新的MterialNodeAllInfoDict字典传递回主窗口并刷新窗口
        self.new_MterialNodeAllInfoDict_signal.emit(new_MterialNodeAllInfoDict, need_update_dict)


    # --------------------保存设置内容的函数
    def modify_config(self, key, cont):
        config = self.dataM.bin_load_data(self.TM_image_processing_config_FilePath)

        config[key] = cont

        self.dataM.bin_save_data(self.TM_image_processing_config_FilePath, config)
    # --------------------保存设置内容的函数


    # 删除存在objectname的窗口



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

# class QTWinTableModify(QtCore.QAbstractTableModel):
#   def __init__(self, data, headers):
#       super(QTWinTableModify, self).__init__()
#       self._data = data
#       self._headers = headers
#
#   def rowCount(self, parent=None):
#       return len(self._data)
#
#   def columnCount(self, parent=None):
#       return len(self._data[0]) if self._data else 0
#
#   def data(self, index, role=QtCore.Qt.DisplayRole):
#       if role == QtCore.Qt.DisplayRole:
#           return self._data[index.row()][index.column()]
#
#   def headerData(self, section, orientation, role):
#       if role == QtCore.Qt.DisplayRole:
#           if orientation == QtCore.Qt.Horizontal:
#               return self._headers[section]
#           else:
#               return f" {section + 1} "




















# 贴图管理器实例窗口
def  TextureManagerWinInstance():
    texture_manager = TextureManagerWin()
    texture_manager.show()


# 贴图批量导入器
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

def test():
    pass

# 设置uv模式
class uv_preset_menu(object):
    def __init__(self,uv_preset):

        self.feedback = FeedbackPrompt() # 错误提示模块

        # 如果没有选择节点会返回None，返回None会关闭函数
        if process_sl_data() == None:
            return
        else:
            sl_data = process_sl_data()


        uv_mode_list = {'禁用':0,
                        '0型(ZBrush)':1,
                        '1型(Mudbox)':2,
                        'UDIM(Mari)':3,
                        '显示平铺':4}

        for i in uv_mode_list:
            if i == uv_preset:
                try:
                    for sl_node in sl_data["file"]:
                        cmds.setAttr(sl_node + ".uvTilingMode",uv_mode_list[i])
                        self.feedback.CP(f'已经把<{sl_node}>设置成<{i}>')
                    return
                except:
                    self.feedback.CP('请你选择<file>节点！')

# 设置颜色空间

def color_space_preset_menu(color_space_preset):
    feedback = FeedbackPrompt() # 错误提示模块
    dataM = DataManager()
    select_node = process_sl_data()

    # 如果没有选择节点会返回None，返回None会关闭函数
    if select_node is not None and 'file' not in select_node:
        return feedback.CP('请选择贴图节点')
    else:
        sl_data = process_sl_data()

    for i in sl_data['file']:
        cmds.setAttr(i + '.colorSpace', color_space_preset, type='string')
        feedback.CP(f"已经把<{i}>设置成<{color_space_preset}>")

# 自动设置颜色空间
def AutoSet_TexColorSpace():
    ### 实例模块
    dataM = DataManager() # 数据管理模块
    NodePro = NodeProcessor()
    # 加载数据
    texture_processing_data = dataM.bin_load_data(
        os.path.join(settings_path, 'texture_processing_data.bin'))

    FilterData = texture_processing_data["TexFirstFilter"] # 过滤贴图的数据

    select_node = process_sl_data()

    if select_node == None:
        return

    if 'file' not in select_node:
        return

    NodePro.AutoSetTexColorSpace(texture_processing_data['ColorSpace']['AutoSetColorSpaceConfig'] , select_node['file'], FilterData)

# !!!!!!!!!!如果要绑定到键位需要另外调整，需要让他有个写出路径，然后读取路径

direct_node_select = False
# 连接到一次输出节点可以把任意节点输出到这个输出节点上
class direct_connection_button(object):

    def __init__(self):
        global direct_node_select
        self.feedback = FeedbackPrompt() # 错误提示模块

        # 如果没有选择节点会返回None，返回None会关闭函数
        if process_sl_data() == None:
            return
        else:
            self.sl_data = process_sl_data()

        for i in self.sl_data:
            if i == "shadingEngine":
                direct_node_select = self.sl_data[i][0]
                self.feedback.CP(f"节点设置成功<{direct_node_select}>")
                return

        if direct_node_select == False:
            self.feedback.CP("请先选择输出节点")
            return


        self.connection_node()


    def connection_node(self):
        # 可以自行添加输出端口名字
        out_name = ["outColor","outAlpha","outValue"]

        for i in self.sl_data:
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
                if shadingEngine_input_node_name == self.sl_data[i][0]:
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

                node_name = self.sl_data[i][0]

                try:
                    cmds.connectAttr(node_name+'.'+out, direct_node_select+'.'+"surfaceShader", f=True)
                    return
                except:
                    self.feedback.CPW(f"你的<{node_name}:{out}>节点无法连接到<{direct_node_select}:shadingEngine>节点上")

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



# 渲染预设菜单设置
class rendering_preset_menu(object):

    def __init__(self,menu_sl_val):

        self.feedback = FeedbackPrompt() # 错误提示模块
        self.dataM = DataManager()
        self.attribute_types = ["bool", "int", "float", "string"]
        self.rederer_attribute_types = ["bool", "float", "string"]


        self.Render_settings_Data =  self.dataM.bin_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'render_settings' , menu_sl_val+ '.bin')
        )

        rendering_write_option_dict = self.dataM.bin_load_data(
            os.path.join(SCRIPT_PATH, 'Datas', 'settings', 'render_preset_config.bin')) # 读取渲染文件

        if rendering_write_option_dict['default_rendering_properties_write_options'] == True:
            self.set_default_rendering_properties()

        if rendering_write_option_dict['rendering_properties_write_options'] == True:
            self.set_rendering_properties()

        if rendering_write_option_dict['AOV_properties_properties_write_options'] == True:
            self.del_original_AOV()

            if self.Render_settings_Data['AOV_properties'] is not None:
                self.set_AOV(menu_sl_val)

    # 设置阿诺德默认参数
    def set_default_rendering_properties(self):
        for i in self.Render_settings_Data['default_rendering_properties']:
            for key, val in self.Render_settings_Data['default_rendering_properties'][i].items():
                try:
                    cmds.setAttr(f'{i}.{key}', val)
                except Exception as e:
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f'{i}.{key}', val, type= attribute_type)
                        except Exception as e:
                            pass


    # 阿诺德预设参数
    def set_rendering_properties(self):
        for i in self.Render_settings_Data['rendering_properties']:
            for key, val in self.Render_settings_Data['rendering_properties'][i].items():
                try:
                    cmds.setAttr(f'{i}.{key}', val)
                except Exception as e:
                    for attribute_type in self.attribute_types:
                        try:
                            cmds.setAttr(f'{i}.{key}', val, type= attribute_type)
                        except Exception as e:
                            pass

    # 设置AOV
    def set_AOV(self,menu_sl_val):
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

    # 输入窗口
    def import_name_win(self,menu_name):

        WIN_NAME = "import_name_win"
        if cmds.window(WIN_NAME, exists=True):
            cmds.deleteUI(WIN_NAME)

        # 创建一个窗口 
        cmds.window(WIN_NAME,title="输入你的预设名字", sizeable=False, mbr= True, tlb=False,w=300,h=40)

        # 创建布局
        layout = cmds.rowLayout(numberOfColumns=50)

        # 创建字符串输入控件
        cmds.text(label=" "*2)
        text_field = cmds.textField(w=300)

        # 创建按钮布局
        cmds.text(label=" "*3)
        cmds.button(label="确定",c=lambda *args: determine())
        cmds.text(label=" | ")
        cmds.button(label="取消",c=lambda *args: cancellation())
        cmds.text(label=" "*3)
        # 设置按钮布局的父级为窗口的布局
        cmds.setParent(layout)

        # 显示窗口
        cmds.showWindow(WIN_NAME)


        def determine():
            global new_rendering_preset_name

            # 01, 获取需要的变量
            self.import_val = cmds.textField(text_field, query=True, text=True) # 获取输入值
            default_rendering_properties = self.get_default_rendering_properties() # 获取默认渲染设置
            rendering_properties = self.get_rendering_properties() # 获取阿诺德渲染设置
            AOV_properties = self.get_AOV_properties() # 获取AOV设置
            write_data_path =  SCRIPT_PATH + r"\Datas\Render_settings" # 路径

            # 02 把变量写入数据结构
            Render_settings = {
                'default_rendering_properties' : default_rendering_properties,
                'rendering_properties' : rendering_properties,
                'AOV_properties' : AOV_properties
            }

            # 03, 创建并写出渲染器属性
            if not os.path.exists(os.path.join(write_data_path, self.import_val+".bin")):
                self.dataM.bin_save_data(os.path.join(write_data_path, self.import_val+".bin"), Render_settings)

            # 04, 给菜单增加新的元素
            edit_menu = menu_name  # 获取菜单的名字或者 ID
            existing_items = cmds.menu(edit_menu, query=True, itemArray=True)  # 获取菜单中所有项目的列表

            # 确定新项目应该插入的位置，例如在第一个项目之后
            insert_after_item = existing_items[0] if existing_items else None

            # 添加新的菜单项
            new_rendering_preset_name[self.import_val] = cmds.menuItem('new_item', parent=edit_menu, insertAfter=insert_after_item, label=self.import_val)

            cmds.deleteUI(WIN_NAME)
            return

        def cancellation():
            cmds.deleteUI(WIN_NAME)
            return

# 删除渲染预设设置
def delete_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name):
    global new_rendering_preset_name
    # # 1,删除选项
    # cmds.menuItem(rendering_preset_path, edit=True, deleteAllItems=True)

    for i in rendering_preset_name:
        if sl_name == i:
            cmds.deleteUI(rendering_preset_name[i], menuItem=True)

    for i in new_rendering_preset_name:
        if sl_name == i:
            cmds.deleteUI(new_rendering_preset_name[i], menuItem=True)

    # 2, 删除本地文件
    file_path = SCRIPT_PATH + '\\Datas\\Render_settings\\'
    os.remove(file_path + sl_name+ '.json')


    # # 3，重新添加控件的选项
    # renderer_data_path =  SCRIPT_PATH + "\\Data\\Render_settings\\renderer"

    # # 获取文件名字
    # file_names = os.listdir(renderer_data_path)

    # # 删除文件名中的 ".json" 部分并存储在列表中
    # file_names_without_json_list = [file_name.replace(".json", "") for file_name in file_names]

    # for renderer_data_mode_name in file_names_without_json_list:
    #   cmds.menuItem(rendering_preset_path, label=renderer_data_mode_name)

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
        return feedback.CP("未创建AOV")

    for aov in connections:
        # 获取当前属性状态
        enabled = cmds.getAttr(aov + ".enabled")

        # 如果 enabled 属性为 1，则将其设置为 0
        if enabled == 1:
            cmds.setAttr(aov + ".enabled", 0)

        # 否则，将 enabled 属性设置为 1
        else:
            cmds.setAttr(aov + ".enabled", 1)

class Path_Detection_Connection:
    def __init__(self):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor()
        ### 初始化配置数据

        # 如果路径检测配置文件不存在会再创建一次配置文件 （很保险的方法，保证不会用不了）
        if os.path.exists(os.path.join(settings_path, 'texture_processing_data.bin')):
            InitialConfigFile.Main_program()

        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

        self.path_detection_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'path_detection_config.bin'))

        self.texture_filter_dict = self.texture_processing_data["TexFirstFilter"]  # 过滤贴图的数据

        self.exclude_list = self.path_detection_data['exclude_list'] # 前期需要排除的名称列表

        self.select_node_data = process_sl_data()  # 调用函数获取处理后的节点数据



    def main(self):

        # 如果没有返回有效的数据，直接退出
        if self.select_node_data is None:
            return

        # 检查数据中是否包含 'file' 键
        if 'file' not in self.select_node_data:
            return self.feedback.CPW('请选择贴图节点哦')

        matching_completed_dict = self.detect_and_calculate_similarity()

        # alt 只会创建贴图
        if keyboard.is_pressed('alt') or keyboard.is_pressed('shift'):

            need_connect_node_lists = self.create_nodes_from_list(matching_completed_dict)

            # 判断是否要修改颜色空间
            if self.path_detection_data['PathDetectionConnectionSetColorSpace']:
                for need_connect_node_list in need_connect_node_lists:
                    self.nodeP.AutoSetTexColorSpace(
                        auto_set_color_space_config=self.texture_processing_data['ColorSpace']['AutoSetColorSpaceConfig'],
                        node_list=need_connect_node_list,
                        filter_data=self.texture_filter_dict)

            # shift 会创建材质并连接
            if keyboard.is_pressed('shift'):
                for need_connect_node_list in need_connect_node_lists:

                    # 判断是否要修改材质的名称
                    if self.path_detection_data['change_material_name']:

                        # 材质球名称会用列表的第一个索引的名称
                        file_name = need_connect_node_list[0]

                        processing_mat_name = self.nodeP.clean_material_name(file_name, self.texture_processing_data["TexFirstFilter"])

                        new_mat_name = cmds.shadingNode('aiStandardSurface', asShader=True, name=processing_mat_name)
                    else:
                        new_mat_name = cmds.shadingNode('aiStandardSurface', asShader=True)




                    matching_dict = self.nodeP.AutoNodeConnect(need_connect_node_list,
                                               new_mat_name,
                                               self.texture_processing_data["TexFirstFilter"], # 过滤贴图的数据
                                               self.texture_processing_data['ProcSet_Options']['ProcessingNodeData'], # 相应贴图节点的参数
                                               self.texture_processing_data['ProcSet_Options']['Magic_Connection_Options'], # 相应贴图是否要连接的参数
                                               self.texture_processing_data['ProcSet_Options']['Auto_Node_Connection_Options']) # 相应贴图是否要连接相应的节点

                    # 判断是否要修改颜色空间
                    if self.path_detection_data['PathDetectionConnectionSetColorSpace']:
                        self.nodeP.AutoSetTexColorSpace(
                            auto_set_color_space_config=self.texture_processing_data['ColorSpace']['AutoSetColorSpaceConfig'],
                            matching_channel=matching_dict)

    def detect_and_calculate_similarity(self):
        # 用来储存匹配完成的数据字典
        matching_completed_dict = {}

        for node_name in self.select_node_data['file']:
            # 1.获取节点路径
            target_object, target_dirname = self.pathD.get_node_path(node_name)

            # 2.寻找子路径下的文件并排除不需要参加匹配的格式
            dir_name_path = self.pathD.detection_path_content(target_dirname, self.exclude_list)

            # 3.获取文件的元属性
            dir_tex_info = self.pathD.get_file_info(dir_name_path)
            target_object_info = self.pathD.get_file_info(target_object)

            # 4.处理匹配名称
            processed_dir_tex_info = self.pathD.process_dict_key_name(dir_tex_info,
                                                                 self.path_detection_data['detection_excluded_list'],
                                                                 self.texture_filter_dict)

            processed_target_object_info = self.pathD.process_dict_key_name(target_object_info,
                                                                       self.path_detection_data['detection_excluded_list'],
                                                                       self.texture_filter_dict)

            # 删除原本选择的
            original_name = list(target_object.keys())[0]  # 获取原始名称
            del processed_dir_tex_info[original_name]

            similarity_dict = self.pathD.calculate_similarity(processed_target_object_info,
                                                         processed_dir_tex_info,
                                                         self.path_detection_data,
                                                         self.path_detection_data['creation_day_range_tolerance'])


            # 判断数据匹配数据
            auto_max_val = self.path_detection_data['auto_max_val']
            similarity_max = self.path_detection_data['similarity_max']
            similarity_range = self.path_detection_data['similarity_range']
            matching_list = self.pathD.determine_connection(similarity_dict, auto_max_val, similarity_max, similarity_range)

            if not self.path_detection_data['disable_feedback']:
                # 发出反馈提醒
                self.feedback_prompt(similarity_dict, matching_list, original_name)

            # 储存匹配好的数据
            matching_completed_dict[node_name] = [matching_list, target_dirname]

        return matching_completed_dict

    def feedback_prompt(self, similarity_dict, matching_list, original_name):
        self.feedback.CP("===================================匹配相似度=================================")
        for tex_name, similarity in similarity_dict.items():
            formatted_similarity = "{:.5f}".format(similarity)
            self.feedback.CP(f"匹配源：{original_name}，匹配目标：{tex_name}，相似度：{formatted_similarity}")

        self.feedback.CP("===================================完成匹配列表=================================")
        self.feedback.CP(f'匹配的对象|{original_name}')
        for target, similarity in matching_list:
            formatted_similarity = "{:.5f}".format(similarity)
            self.feedback.CP(f"完成匹配| {target}，相似度：{formatted_similarity}")

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


class Magic_Node_Connection:
    def __init__(self):
        ### 实例各种模块
        self.dataM = DataManager()  # 数据管理模块
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.pathD = PathDetection()  # 数据检测模块
        self.nodeP = NodeProcessor()

        ### 初始化配置数据
        # 加载数据
        self.texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

        self.texture_filter_dict = self.texture_processing_data[
            "TexFirstFilter"]  # 过滤贴图的数据
        self.processing_node_data = self.texture_processing_data[
            'ProcSet_Options'][
            'ProcessingNodeData']  # 相应贴图节点的参数
        self.magic_connection_options = self.texture_processing_data[
            'ProcSet_Options'][
            'Magic_Connection_Options']  # 相应贴图是否要连接的参数
        self.auto_node_connection_options = self.texture_processing_data[
            'ProcSet_Options'][
            'Auto_Node_Connection_Options']  # 相应贴图是否要连接相应的节点


        # 获取选择节点
        self.select_node = process_sl_data()

    def main(self):

        # 如果没有选择节点将会直接退出函数
        if self.select_node is None:
            return

        if keyboard.is_pressed('alt'):
            pass
        else:
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


        # 如果材质变量是None的话就不需要处理
        if mat_name is None:
            return

        new_mat_name = self.modify_mat_name(original_mat_name=mat_name, file_name=self.select_node['file'][0])

        self.feedback.CP('已完成 {} 材质连接'.format(new_mat_name))

        self.modify_color_space()

    # 检测并创建材质
    def detect_and_create_materials(self):
        mat_name = None
        # 检测有没有选择材质球
        if 'aiStandardSurface' in self.select_node:
            mat_name = self.select_node['aiStandardSurface'][0]
        else:
            if keyboard.is_pressed('shift'):
                mat_name = cmds.shadingNode('aiStandardSurface', asShader=True)


        return mat_name

    # 修改材质名称
    def modify_mat_name(self,original_mat_name,  file_name):

        texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

        # 修改材质名称
        if texture_processing_data['ProcSet_Options']['change_material_name']:
            new_mat_name = self.nodeP.clean_material_name(file_name, self.texture_filter_dict)
        else:
            return original_mat_name

        # 修改材质节点名称
        cmds.rename(original_mat_name, new_mat_name)

        self.feedback.CP('已将 {} 材质名称修改成 {}'.format(original_mat_name, new_mat_name))

        return new_mat_name

    # 修改颜色空间
    def modify_color_space(self):
        texture_processing_data = self.dataM.bin_load_data(
            os.path.join(settings_path, 'texture_processing_data.bin'))

        if texture_processing_data['ProcSet_Options']['MagicConnectionSetColorSpace']:
            self.nodeP.AutoSetTexColorSpace(
                auto_set_color_space_config = texture_processing_data['ColorSpace']['AutoSetColorSpaceConfig'],
                matching_channel = self.matching_dict)
        else:
            return

def path_detection_connection_button():
    PDC = Path_Detection_Connection()
    PDC.main()

def magic_connection_button():
    MC = Magic_Node_Connection()
    MC.main()

def Main_program(cached_device_fingerprint, public_key, public_password, validating):
    # cached_device_fingerprint, public_key, public_password, remaining_time
    global LicenseV_device_fingerprint, LicenseV_public_key, LicenseV_public_password, LicenseV_type, LicenseV_type_name,  LicenseV_remaining_time

    dataM = DataManager()  # 数据管理

    language_config = dataM.ascii_load_data(
        os.path.join(SCRIPT_PATH, 'Datas', 'settings', 'language_config.json'))['language_config']

    language = dataM.ascii_load_data(
        os.path.join(SCRIPT_PATH, 'Datas', 'languages', f'{language_config}.json'))['ArnoldMagicNode']['licenses_name']



    # 把验证完的相关信息传回主程序，备着使用
    LicenseV_device_fingerprint = cached_device_fingerprint
    LicenseV_public_key = public_key
    LicenseV_public_password = public_password
    LicenseV_type = validating['license_type']
    LicenseV_type_name = language[LicenseV_type]

    if validating['expiry_date'] == None:
        LicenseV_remaining_time = language['expiry_date_01']
    else:
        current_time = datetime.utcnow()


        remaining_time = validating['expiry_date'] - current_time

        LicenseV_remaining_time = remaining_time.days




    # 创建窗口
    indowInstance = Arnold_Magic_Node_UI()
