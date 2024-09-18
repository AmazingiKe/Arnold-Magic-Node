##############################################################################################
# # ++ 导入所需的库和模块

# 1. Maya 库
import maya.cmds as cmds  # 导入 Maya 的 cmds 模块，用于执行 Maya 命令和操作场景
import maya.OpenMayaUI as omui  # 导入 Maya 的 OpenMayaUI 模块，用于操作 Maya 的用户界面

# 2. 文件与系统操作
import os  # 提供与操作系统交互的功能，如文件路径操作、目录遍历等
import sys  # 提供与 Python 解释器交互的功能，如获取脚本路径、调整模块搜索路径等
import importlib  # 用于动态导入和重新加载模块，支持模块的按需加载
import pathlib  # 提供面向对象的文件系统路径操作，增强对路径的处理能力

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
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtGui
    from shiboken2 import wrapInstance
    from PySide2.QtCore import Signal, Slot
except ImportError:
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtGui
    from shiboken6 import wrapInstance
    from PySide6.QtCore import Signal, Slot

# ------------------------------------------
# 获取脚本路径
Script_path = os.path.join(os.path.dirname(__file__))  # 获取当前脚本的目录路径
Icon_path = Script_path + "\icon"  # 定义图标路径，假设图标位于脚本目录下的 'icon' 文件夹
# ------------------------------------------

# 9. 自定义库导入与依赖管理
import Arnold_Magic_Node_lib  # 导入自定义的 Arnold 魔法节点库
importlib.reload(Arnold_Magic_Node_lib)  # 在开发阶段，重新加载模块以反映对库的更改
from Arnold_Magic_Node_lib import *  # 从自定义库中导入所有内容

import DependenciesLibs  # 导入自定义的依赖管理模块
DependenciesLibs.importLibs()  # 调用自定义模块中的函数，动态导入和初始化所需的依赖库

# 10. 初始化变量
# 创建初始化变量
LicenseV_device_fingerprint = None
LicenseV_public_key = None
LicenseV_public_password = None
LicenseV_remaining_time = None

##############################################################################################

# --------------------初始变量开始
SoftwareState = "Beta"
SoftwareVersion = "0.5.1"

pluginHomePath = r"https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69"
pluginFeedbackURL = r"https://flowus.cn/form/7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69"
# --------------------初始变量结束



# --------------------初始变量结束

# ----------------------------------------------------初始配置变量 开始

TEX_PROCESSING_DATA = {
    "TexFirstFilter": [
        {"TexFirstFilterData": {
            'base': ['BASE_MASK'],
            'baseColor': ["ALBEDO", "BASE_COLOR", "BASECOLOR", "DIFFUSE"],
            'diffuseRoughness': ['DIFFUSEROUGHNESS'],
            'metalness': ["METALNESS", "METALLIC", "METALIC", "METAL","DIFFUSE"],
            'specular': ["SPECULAR", "SPEC"],
            'specularColor': ["SPECULARCOLOR"],
            'specularRoughness': ["ROUGHNESS", "ROUGH"],
            'specularAnisotropy': ["SPECULARANISOTROPY"],
            'specularRotation': ["SPECULARROTATION"],
            'subsurface': ['SUBSURFACE', 'SSS'],
            'subsurfaceColor': ["TRANSLUCENCY", "SUBSURFACECOLOR"],
            'subsurfaceRadius': ["SUBSURFACERADIUS", "SUBSURFACE-RADIUS", "SUBSURFACE-RAD"],
            'emission': ["EMISSION", "ILLUMINATION"],
            'emissionColor': ["EMISSIONCOLOR"],
            'opacity': ["ALPHA", "ALPHAMASKED", "MASK", "OPACITY", "TRANSPARENCY"],
            'normalCamera': ["NORMAL","NORMALMAP","NRM"]
        }},
        {"TexSoloFilterData": {
            "AO": ["AO", "AMBIENT_OCCLUSION", "OCC", "AMBIENT", "OCCLUSION"],
            "Bump": ["BUMP", "BMP"],
            "Displacement": ["HEIGHT","DISPLACEMENT", "DISP", "DEPTH", "HEIGHTMAP"]
        }}
    ],
    "ColorSpace": [
        {"ColorSpaceData": ['sRGB', 'Gamma 2.2 / Rec.709', 'Rec.1886 / Rec.709 video', 'AdobeRGB',
                            'PCI-P3 D65', 'ACEScg', 'ACES2065-1', 'scene-linear Rec.709-sRGB',
                            'scene-linear DCI-P3 D65', 'scene-linear Rec.2020', 'Raw', 'ACEScct',
                            'Utility-Raw', 'Utility - linear - sRGB', 'Utility - sRGB - Texture']},
        {"AutoSetColorSpaceConfig":{
            'base': 'Raw',
            'baseColor': 'sRGB',
            'diffuseRoughness': 'Raw',
            'metalness': 'Raw',
            'specular': 'Raw',
            'specularColor': 'sRGB',
            'specularRoughness': 'Raw',
            'specularAnisotropy': 'Raw',
            'specularRotation': 'Raw',
            'subsurface': 'Raw',
            'subsurfaceColor': 'sRGB',
            'subsurfaceRadius': 'Raw',
            'emission': 'Raw',
            'emissionColor': 'sRGB',
            'opacity': 'Raw',
            'normalCamera': 'Raw',
            "AO": 'Raw',
            "Bump": 'Raw',
            "Displacement": 'Raw'
        }}
    ],
    "ProcSet_Options":{
        'TexFirstFilter_Options': {
            'base': False,
            'baseColor': True,
            'diffuseRoughness': False,
            'metalness': True,
            'specular': False,
            'specularColor': False,
            'specularRoughness': True,
            'specularAnisotropy': False,
            'specularRotation': False,
            'subsurface': False,
            'subsurfaceColor': False,
            'subsurfaceRadius': False,
            'emission': False,
            'emissionColor': False,
            'opacity': True,
            'normalCamera': True,
            "AO": False,
            "Bump": False,
            "Displacement": False
            },
        "TexSoloFilterData_Options" :{
            "AO": True,
            "Bump": False,
            "Displacement": True
            },
        "Auto_Node_Connection_Options" : {
            'base': False,
            'baseColor': True,
            'diffuseRoughness': False,
            'metalness': False,
            'specular': False,
            'specularColor': False,
            'specularRoughness': True,
            'specularAnisotropy': False,
            'specularRotation': False,
            'subsurface': False,
            'subsurfaceColor': False,
            'subsurfaceRadius': False,
            'emission': False,
            'emissionColor': False,
            'opacity': True,
            'normalCamera': True,
            "AO": False,
            "Bump": False,
            "Displacement": True
            },
        "ProcessingNodeData" : {
        'base': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'baseColor': {
            "NodeList": ["aiColorCorrect"],
            "InputPort": "input",
            "OutputPort": "outColor"
        },
        'diffuseRoughness': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'metalness': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'specular': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'specularColor': {
            "NodeList": ["aiColorCorrect"],
            "InputPort": "input",
            "OutputPort": "outColor"
        },
        'specularRoughness': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'specularAnisotropy': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'specularRotation': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'subsurface': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'subsurfaceColor': {
            "NodeList": ["aiColorCorrect"],
            "InputPort": "input",
            "OutputPort": "outColor"
        },
        'subsurfaceRadius': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'emission': {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        'emissionColor': {
            "NodeList": ["aiColorCorrect"],
            "InputPort": "input",
            "OutputPort": "outColor"
        },
        'opacity': {
            "NodeList": ["aiColorCorrect"],
            "InputPort": "input",
            "OutputPort": "outColor"
        },
        'normalCamera': {
            "NodeList": ["aiColorCorrect"],
            "InputPort": "input",
            "OutputPort": "outColor"
        },
        "AO": {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        "Bump": {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        },
        "Displacement": {
            "NodeList": ["aiRampRgb", "aiRange"],
            "InputPort": "input",
            "OutputPort": "outColorR"
        }
    },
        'InputPortList': ["input", "passthrough"],
        'OutputPortList': ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB"],
        'GraysList' : ["base", 'diffuseRoughness', 'metalness', 'specularRoughness', 'subsurface', 'emission', 'AO', 'Bump', 'Displacement'],
        'ColorList' : ['baseColor', 'specularColor', 'subsurfaceColor', 'subsurfaceRadius', 'emissionColor', 'opacity', 'normalCamera'],
        'MagicConnectionSetColorSpace' : True,
        'PathDetectionConnectionSetColorSpace' : True
    },
    "Path_Detection":{
            'exclude_list' : ['.tx', '_PREVIEW', '_preview', 'LOD1','LOD2', 'LOD3', 'LOD4', 'LOD5', 'LOD6', 'LOD7', 'LOD8', 'LOD9', 'LOD10'],
            'format_list' : ['jpg', 'png', 'tiff', 'exr', 'tif', 'ex', "psd", "raw"],
            'similarity_range' : 0.1,
            'similarity_max' : 1,
            'length_weight' : 0.3,
            'auto_max_val' : True,
            'near_one_value' : False,
            'case_sensitive' : True,
    },
    "Other_Settings" :{
        "language" : "zh_CN",
    }
                }

RENDERING_WRITE_OPTION_DATA = {
    'default_rendering_properties_write_options' : True,
    'rendering_properties_write_options' : True,
    'AOV_properties_properties_write_options' : True
                                }

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
        WIN_TITLE = "Arnold_Magic_Node  Beta:1.1    许可证剩余时间 : {}天".format(str(LicenseV_remaining_time))

        # 判断窗口是否存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)

        # 创建主窗口
        self.window = cmds.workspaceControl(WIN_TITLE, retain=False, floating=True,w=300,h=300)




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
        cmds.menuItem(label= '贴图管理器', c=lambda *args:TextureManagerWinInstance(), i = Icon_path + "\\TXManagerShelf_200.png")
        cmds.menuItem(label= '贴图批量导入器', c=lambda *args:TextureBatchImporterWin(), i = Icon_path + "\\RenderToTextureShelf_200.png")

        cmds.menuItem(label= '渲染预设设置', divider=True) # 添加分割线
        cmds.menuItem(label= '添加渲染预设', c=lambda *args:rendering_preset_settings_button(self.rendering_preset))
        cmds.menuItem(label= '修改渲染预设', c= lambda *args:modify_rendering_preset_menuItem(cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True), cmds.optionMenu(self.rendering_preset, query=True, value=True), self.rendering_preset_name, self.rendering_preset))
        cmds.menuItem(label= '删除渲染预设', c= lambda *args:delete_rendering_preset_menuItem(cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True), cmds.optionMenu(self.rendering_preset, query=True, value=True), self.rendering_preset_name))
        cmds.menuItem(label= '打开渲染预设文件夹', c= lambda *args:os.startfile(Script_path + "\Data\Render_settings"))
        cmds.menuItem(divider=True)
        default_rendering_properties_options = cmds.menuItem(label= '输出 默认参数', cb= True, c= lambda *args:self.modify_rendering_properties_write_options('default_rendering_properties_write_options', cmds.menuItem(default_rendering_properties_options, query=True, checkBox=True)))
        rendering_properties_options = cmds.menuItem(label= '输出 阿诺德参数', cb= True, c= lambda *args:self.modify_rendering_properties_write_options('rendering_properties_write_options', cmds.menuItem(rendering_properties_options, query=True, checkBox=True) ))
        aov_properties_properties_options = cmds.menuItem(label= '输出 AOV参数', cb= True, c= lambda *args:self.modify_rendering_properties_write_options('AOV_properties_properties_write_options', cmds.menuItem(aov_properties_properties_options, query=True, checkBox=True) ))
        cmds.menuItem(divider=True)

        cmds.menuItem(label= '设置', c= lambda *args:Arnold_Magic_Node_Settings_Panel())




        # 修改默认值
        RENDERING_WRITE_OPTION_DICT =  load_data("RENDERING_WRITE_OPTION_DATA") # 读取渲染文件
        cmds.menuItem(default_rendering_properties_options, edit= True, checkBox= RENDERING_WRITE_OPTION_DICT['default_rendering_properties_write_options'])
        cmds.menuItem(rendering_properties_options, edit= True, checkBox= RENDERING_WRITE_OPTION_DICT['rendering_properties_write_options'])
        cmds.menuItem(aov_properties_properties_options, edit= True, checkBox= RENDERING_WRITE_OPTION_DICT['AOV_properties_properties_write_options'])
        # 菜单=========

        cmds.text(label=" "*1)




        # Magic_Connection
        self.magic_connection = cmds.button(label="魔法连接",c=lambda *args:magic_connection_button())

        self.path_detection_connection = cmds.button(label="路径拾取连接",c=lambda *args:path_detection_connection_button())

        # Direct_Connection
        self.direct_connection = cmds.button(label="直连",c=lambda *args:direct_connection_button())
        # Unify Uv Node
        self.unify_uv_node = cmds.button(label="统一UV",c=lambda *args:unify_uv_node_button())

        cmds.text(label=" "*2)

        self.uv_preset = cmds.optionMenu(mvi = 8, cc=lambda* args:uv_preset_menu(cmds.optionMenu(self.uv_preset, query=True, value=True)))
        # 用循环创建uv_mode_list 的menu
        uv_mode_list = ['禁用','0型(ZBrush)','1型(Mudbox)','UDIM(Mari)','显示平铺']
        for uv_mode_name in uv_mode_list:
            cmds.menuItem(label=uv_mode_name)




        self.color_space_preset = cmds.optionMenu(mvi = 16, cc=lambda* args:color_space_preset_menu(cmds.optionMenu(self.color_space_preset, query=True, value=True)))
        # 用循环创建color_space_list的menu
        color_space_list = load_data('TEX_PROCESSING_DATA')["ColorSpace"][0]['ColorSpaceData']
        for uv_mode_name in color_space_list:
            cmds.menuItem(label=uv_mode_name)

        # 自动色彩空间的按钮
        cmds.button(label="自动色彩空间",c=lambda *args:AutoSet_TexColorSpace())

        cmds.text(label=" "*2)

        self.ai_aov_switch = cmds.button(label="AOV开关",c=lambda *args:ai_aov_switch_button())

        # 渲染预设的菜单 —————————————————— 开始
        self.rendering_preset_name = {}
        self.rendering_preset =  cmds.optionMenu(mvi = 8, cc=lambda* args:rendering_preset_menu(cmds.optionMenu(self.rendering_preset, query=True, value=True)))
        # self.rendering_preset_settings = cmds.button(label="添加预设",c=lambda *args:rendering_preset_settings_button(self.rendering_preset))


        renderer_data_path =  Script_path + r"\Datas\Render_settings"

        # 获取文件名字
        file_names = os.listdir(renderer_data_path)

        # 删除文件名中的 ".json" 部分并存储在列表中
        file_names_without_json_list = [file_name.replace(".json", "") for file_name in file_names]

        for renderer_data_mode_name in file_names_without_json_list:
            self.rendering_preset_name[renderer_data_mode_name] = cmds.menuItem(label=renderer_data_mode_name)


        # 渲染预设的菜单 —————————————————— 结束


        cmds.text(label="                     "*1)
        # self.Arnold_Magic_Node_Settings_Panel = cmds.button(label="设置",c=lambda *args:Arnold_Magic_Node_Settings_Panel())
        # self.test = cmds.iconTextButton(i=Script_path+ r'\icon\TEST.png',c=lambda *args:test(), h=37.5/1.8,w=80)
        cmds.iconTextButton(i=Script_path+ r'\icon\Autodesk_Arnold_logo.png', h=37.5/1.8, w=155/1.8, c=lambda *args:TextureManagerWinInstance())
        cmds.text(label=" "*1)

    # 修改渲染属性写入选项
    def modify_rendering_properties_write_options(self, write_name, val):
        RENDERING_WRITE_OPTION_DICT =  load_data("RENDERING_WRITE_OPTION_DATA") # 读取渲染文件
        RENDERING_WRITE_OPTION_DICT[write_name] = val
        file_path = os.path.join(os.path.dirname(__file__)) +'\\RENDERING_WRITE_OPTION_DATA.json'
        write_data(file_path, RENDERING_WRITE_OPTION_DICT)

# 插件设置按钮
class  Arnold_Magic_Node_Settings_Panel(object):
    def __init__(self):
        WIN_TITLE = "Arnold_Magic_Node_Settings_Panel"

        # 判断窗口是否存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)


        # 创建主窗口
        self.window = cmds.window(WIN_TITLE, title=WIN_TITLE,sizeable=False, widthHeight=(530, 600))





        self.create_widgets()



        # 显示窗口
        cmds.showWindow(self.window)


    def create_widgets(self):


        # 创建菜单栏
        menu_bar_layout = cmds.menuBarLayout()


        Setting_menu = cmds.menu(label='设置')
        cmds.menuItem(label='重置数据', c=lambda *args:self.resetData())

        # 许可证的菜单
        license_menu = cmds.menu(label='许可证')

        cmds.menuItem(label='更换许可证')
        cmds.menuItem(label='详细信息')


        # 关于的菜单
        about_menu = cmds.menu(label='关于')

        # 添加菜单项到关于菜单
        cmds.menuItem(label='赞助')
        cmds.menuItem(label='联系/反馈')
        cmds.menuItem(label='帮助文档', c=lambda *args:webbrowser.open('https://flowus.cn/amazingike/93cfb135-4ab3-4536-8a5b-9b3e53042b51'))





        # 创建多标签的布局
        tab_layout = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)



        #------------------------>自定义过滤名字   开始
        TexFirstFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][0]["TexFirstFilterData"]
        TexSoloFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][1]["TexSoloFilterData"]
        TexFirstFilter_Options = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["TexFirstFilter_Options"]

        # 这个是存下来的控件信息
        self.TexFirstFilter_widgets_name = {}
        self.TexSoloFilter_widgets_name = {}

        # 创建滚动布局
        TexFirstFilter_scroll_layout = cmds.scrollLayout(horizontalScrollBarThickness=16, verticalScrollBarThickness=16, parent=tab_layout)




        cmds.text(label = " [1] ---------->连接设置:", fn="smallBoldLabelFont", h= 35)

        ModifyMagicConnectionSetColorSpace = cmds.checkBox(l='连接时开启自动色彩空间',
                                                                            value = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["MagicConnectionSetColorSpace"],
                                                                            cc = lambda *args:self.ModifyConfigurationFile(cmds.checkBox(ModifyMagicConnectionSetColorSpace, query=True, value=True), ["ProcSet_Options","MagicConnectionSetColorSpace"]))






        cmds.text(label = " [2] ---------->自定义连接的贴图:", fn="smallBoldLabelFont", h= 35)
        # 创建TexFirstFilter_Options列表
        TexFirstFilter_Options_scroll_list = cmds.textScrollList(allowMultiSelection=True,w = 500, h= 275, sc= lambda *args:self.SetTexFirstFilterOptions(cmds.textScrollList(TexFirstFilter_Options_scroll_list, query=True, selectItem=True)))
        for name, value in TexFirstFilter_Options.items():
            #new_name = name.capitalize()
            cmds.textScrollList(TexFirstFilter_Options_scroll_list, edit=True, append= name)
            if value:  # 如果值为True，则将键添加到选中项列表中
                cmds.textScrollList(TexFirstFilter_Options_scroll_list, edit=True, selectItem= name)






        cmds.text(label = " [3] ---------->自定义过滤名字:", fn="smallBoldLabelFont", h= 35)
        # 创建TexFirstFilterData输入框
        for channel in TexFirstFilterData:

            # 将每个输入框添加到滚动布局中
            cmds.text(label = channel.capitalize()+" :", parent = TexFirstFilter_scroll_layout, fn="smallBoldLabelFont")
            self.TexFirstFilter_widgets_name[channel] = cmds.textField(parent=TexFirstFilter_scroll_layout,
                                                #...删除掉[]还有双引号
                                                text= str((load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][0]["TexFirstFilterData"][channel])).replace('[', '').replace(']', '').replace("'", ""),
                                                ed= True,
                                                fn= "smallBoldLabelFont",
                                                w= 500,
                                                h= 35,
                                                tcc= lambda _, channel=channel: self.TexFirstFilterData_modify(channel))
        # 创建TexSoloFilterData输入框
        for channel in TexSoloFilterData:
            # 将每个输入框添加到滚动布局中
            cmds.text(label = channel.capitalize()+" :", parent = TexFirstFilter_scroll_layout, fn="smallBoldLabelFont")
            self.TexSoloFilter_widgets_name[channel] = cmds.textField(parent=TexFirstFilter_scroll_layout,
                                                #...删除掉[]还有双引号
                                                text= str((load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][1]["TexSoloFilterData"][channel])).replace('[', '').replace(']', '').replace("'", ""),
                                                ed= True,
                                                fn= "smallBoldLabelFont",
                                                w= 500,
                                                h= 35,
                                                tcc=lambda _, channel=channel: self.TexSoloFilterData_modify(channel))







        #------------------------>自定义过滤名字   结束











        #------------------------>颜色空间设置   开始


        ColorSpaceData = load_data('TEX_PROCESSING_DATA')["ColorSpace"][0]["ColorSpaceData"]

        ColorSpace_scroll_layout = cmds.scrollLayout(horizontalScrollBarThickness=16, verticalScrollBarThickness=16, parent=tab_layout)


        # cmds.text(label = " [1] ---------->一些色彩空间相关的设置:", fn="smallBoldLabelFont", h= 35)


        cmds.text(label = " [1] ---------->自定义色彩空间:", fn="smallBoldLabelFont", h= 35)
        color_space_preset_input_control = cmds.scrollField(parent = ColorSpace_scroll_layout,
                                                            tx= str(ColorSpaceData).replace('[', '').replace(']', '').replace("'", "").replace(",", " , "),
                                                            ed=True,
                                                            fn="smallBoldLabelFont",
                                                            wordWrap= True,
                                                            w = 510,
                                                            h = 300,
                                                            fns= 10,
                                                            cc = lambda *args:self.ColorSpaceData_modify(cmds.scrollField(color_space_preset_input_control , query=True, tx=True)),
                                                            kpc = lambda *args:self.ColorSpaceData_modify(cmds.scrollField(color_space_preset_input_control , query=True, tx=True)))
        cmds.text(label = " ", fn="smallBoldLabelFont")
        cmds.text(label = " [2] ---------->自动设置色彩空间:", fn="smallBoldLabelFont", h= 35)

        AutoSetColorSpaceMenuName = {}

        for i in load_data('TEX_PROCESSING_DATA')["ColorSpace"][1]['AutoSetColorSpaceConfig']:
            AutoSetColorSpaceMenuName[i] = cmds.optionMenu(mvi = 20, w=480, l=f'{i.capitalize()}:', h= 25)
            for ColorSpaceName in load_data('TEX_PROCESSING_DATA')["ColorSpace"][0]['ColorSpaceData']:
                cmds.menuItem(label=ColorSpaceName)
            cmds.optionMenu(AutoSetColorSpaceMenuName[i], edit= True, value= load_data('TEX_PROCESSING_DATA')["ColorSpace"][1]['AutoSetColorSpaceConfig'][i])
            cmds.optionMenu(AutoSetColorSpaceMenuName[i], edit= True, cc= lambda _, channel= AutoSetColorSpaceMenuName[i],sl_optionMenu= i : self.ModifyConfigurationFile(cmds.optionMenu(channel, query=True, value=True), ["ColorSpace", 1, 'AutoSetColorSpaceConfig', f"{sl_optionMenu}"]))
        cmds.text(label = " ", fn="smallBoldLabelFont")

        #------------------------>颜色空间设置   结束















        #------------------------>节点连接   开始
        Auto_Node_Connection_Options = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["Auto_Node_Connection_Options"]

        Node_Connection_layout = cmds.scrollLayout(horizontalScrollBarThickness=16, verticalScrollBarThickness=16, parent=tab_layout)

        cmds.text(label = " [1] ---------->自定义连接的节点:", fn="smallBoldLabelFont", h= 35)
        # Auto_Node_Connection_Options
        Auto_Node_Connection_Options_scroll_list = cmds.textScrollList(allowMultiSelection=True,w = 500, h= 275, sc= lambda *args:self.SetAuto_Node_Connection_Options(cmds.textScrollList(Auto_Node_Connection_Options_scroll_list, query=True, selectItem=True)))
        for name, value in Auto_Node_Connection_Options.items():
            #new_name = name.capitalize()
            cmds.textScrollList(Auto_Node_Connection_Options_scroll_list, edit=True, append= name)
            if value:  # 如果值为True，则将键添加到选中项列表中
                cmds.textScrollList(Auto_Node_Connection_Options_scroll_list, edit=True, selectItem= name)

        ProcessingNodeData = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["ProcessingNodeData"]
        ProcSet_Options = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]

        NodeInputPortOptionName = {}
        NodeOutputPortOptionName = {}
        NodeListFieldName = {}
        # 遍历 ProcessingNodeData 字典的每个 Channel
        for Channel in ProcessingNodeData:
            # 将当前布局的父布局设置为 Node_Connection_layout
            cmds.setParent(Node_Connection_layout)

            # 创建一个可调节列布局，用于组合相关控件
            column_layout = cmds.columnLayout(adjustableColumn=True)

            # 在列布局中添加 Channel 的标签文本控件
            # Channel 的标签文本内容是大写的
            cmds.text(label=Channel.upper(), fn="smallBoldLabelFont", h=25)

            # 在列布局中创建一个行布局，包含三个控件
            row_layout = cmds.rowLayout(numberOfColumns=10, adjustableColumn=2)

            # 创建一个输入端口选择菜单
            NodeInputPortOptionName[Channel] = cmds.optionMenu(h=25)

            # 遍历 InputPortList 列表，并将每个输入端口作为菜单项添加到 NodeInputPortOption
            for InputPort in ProcSet_Options["InputPortList"]:
                cmds.menuItem(label=InputPort, parent=NodeInputPortOptionName[Channel])

            # 设置NodeInputPortOptionName默认值
            cmds.optionMenu(NodeInputPortOptionName[Channel], edit= True, value= ProcessingNodeData[Channel]['InputPort'])
            cmds.optionMenu(NodeInputPortOptionName[Channel],
                            edit= True,
                            cc = lambda _, channel=Channel: self.ModifyConfigurationFile(cmds.optionMenu(NodeInputPortOptionName[channel], query=True, value=True), ["ProcSet_Options", "ProcessingNodeData", f"{channel}", "InputPort"]))

            # 创建一个文本输入框，用于显示和输入 NodeList 的内容
            # 初始文本内容来自 ProcessingNodeData[Channel]["NodeList"] 并进行格式化
            NodeListFieldName[Channel] = cmds.textField(
                placeholderText="Enter text here",
                w=268,
                h=25,
                text=str(ProcessingNodeData[Channel]["NodeList"])
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , "),
                tcc = lambda _, channel=Channel: self.NodeListField_modify(channel, cmds.textField(NodeListFieldName[channel], query=True, text=True)),
            )

            # 创建一个输出端口选择菜单
            NodeOutputPortOptionName[Channel] = cmds.optionMenu(h=25)

            # 遍历 OutputPortList 列表，并将每个输出端口作为菜单项添加到 NodeOutputPortOption
            for OutputPort in ProcSet_Options["OutputPortList"]:
                cmds.menuItem(label=OutputPort, parent=NodeOutputPortOptionName[Channel])

            # 设置NodeOutputPortOptionName默认值
            cmds.optionMenu(NodeOutputPortOptionName[Channel], edit= True, value= ProcessingNodeData[Channel]['OutputPort'])
            cmds.optionMenu(NodeOutputPortOptionName[Channel],
                            edit= True,
                            cc = lambda _, channel=Channel: self.ModifyConfigurationFile(cmds.optionMenu(NodeOutputPortOptionName[channel], query=True, value=True), ["ProcSet_Options", "ProcessingNodeData", f"{channel}", "OutputPort"]))
            # 创建一个按钮控件，标签为 "<" 并设置高度
            AddNodeButton = cmds.button(label="<", h=25, c = lambda _, channel=Channel, NodeListFieldName = NodeListFieldName[Channel]: self.AddNodeButton_modify(channel, cmds.textField(NodeListFieldName, query=True, text=True), NodeListFieldName))




        #------------------------>节点连接   结束











        #------------------------>节点路径匹配   开始
        Node_Path_Matching_layout = cmds.scrollLayout(horizontalScrollBarThickness=16, verticalScrollBarThickness=16, parent=tab_layout)
        cmds.text(label = " [1] ---------->连接时相关设置:", fn="smallBoldLabelFont", h= 35)
        ModifyPathDetectionConnectionSetColorSpace = cmds.checkBoxGrp(l='连接时开启自动色彩空间',
                                                                    v1 = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["MagicConnectionSetColorSpace"],
                                                                    cc = lambda *args:self.ModifyConfigurationFile(cmds.checkBoxGrp(ModifyPathDetectionConnectionSetColorSpace, query=True, v1=True), ["ProcSet_Options","PathDetectionConnectionSetColorSpace"]))


        cmds.text(label = " [2] ---------->排除名称:", fn="smallBoldLabelFont", h= 35)

        exclude_list = load_data('TEX_PROCESSING_DATA')["Path_Detection"]["exclude_list"]

        exclude_list_input_control = cmds.scrollField(parent = Node_Path_Matching_layout,
                                                            tx= str(exclude_list).replace('[', '').replace(']', '').replace("'", "").replace(",", " , "),
                                                            ed=True,
                                                            fn="smallBoldLabelFont",
                                                            wordWrap= True,
                                                            w = 510,
                                                            h = 100,
                                                            fns= 10,
                                                            cc = lambda *args:self.exclude_list_modify(cmds.scrollField(exclude_list_input_control , query=True, tx=True)),
                                                            kpc = lambda *args:self.exclude_list_modify(cmds.scrollField(exclude_list_input_control , query=True, tx=True)))
        cmds.text(label = " ", fn="smallBoldLabelFont")

        cmds.text(label = " [3] ---------->格式名称:", fn="smallBoldLabelFont", h= 35)

        format_list = load_data('TEX_PROCESSING_DATA')["Path_Detection"]["format_list"]

        format_list_input_control = cmds.scrollField(parent = Node_Path_Matching_layout,
                                                            tx= str(format_list).replace('[', '').replace(']', '').replace("'", "").replace(",", " , "),
                                                            ed=True,
                                                            fn="smallBoldLabelFont",
                                                            wordWrap= True,
                                                            w = 510,
                                                            h = 100,
                                                            fns= 10,
                                                            cc = lambda *args:self.format_list_modify(cmds.scrollField(format_list_input_control , query=True, tx=True)),
                                                            kpc = lambda *args:self.format_list_modify(cmds.scrollField(format_list_input_control , query=True, tx=True)))
        cmds.text(label = " ", fn="smallBoldLabelFont")

        cmds.text(label = " [4] ---------->匹配时相关设置:", fn="smallBoldLabelFont", h= 35)
        # 创建一个整数滑块控件
        case_sensitive_checkBox = cmds.checkBoxGrp(l='是否根据大小写进行判断:',
                                                 cc = lambda *args :self.ModifyConfigurationFile(cmds.checkBoxGrp(case_sensitive_checkBox, query=True, v1=True), ["Path_Detection", "case_sensitive"]),
                                                 v1 = load_data('TEX_PROCESSING_DATA')["Path_Detection"]["case_sensitive"])

        near_one_value_checkBox = cmds.checkBoxGrp(l='获取到接近1的值:',
                                                 cc = lambda *args :self.ModifyConfigurationFile(cmds.checkBoxGrp(near_one_value_checkBox, query=True, v1=True), ["Path_Detection", "near_one_value"]),
                                                 v1 = load_data('TEX_PROCESSING_DATA')["Path_Detection"]["near_one_value"])

        auto_max_val_checkBox = cmds.checkBoxGrp(l='自动获取最大值:',
                                                 cc = lambda *args :self.ModifyConfigurationFile(cmds.checkBoxGrp(auto_max_val_checkBox, query=True, v1=True), ["Path_Detection", "auto_max_val"] ),
                                                 v1 = load_data('TEX_PROCESSING_DATA')["Path_Detection"]["auto_max_val"])

        similarity_max_slider = cmds.floatSliderGrp(label="相似度判断值:", field=True, min=0, max=1, value=load_data('TEX_PROCESSING_DATA')["Path_Detection"]["similarity_max"] ,
                                                    precision=5,
                                                    p=Node_Path_Matching_layout, width= 500,
                                                    cc = lambda *args :self.ModifyConfigurationFile(cmds.floatSliderGrp(similarity_max_slider, query=True, value=True), ["Path_Detection", "similarity_max"]),
                                                    dc = lambda *args :self.ModifyConfigurationFile(cmds.floatSliderGrp(similarity_max_slider, query=True, value=True), ["Path_Detection", "similarity_max"]))

        similarity_range_slider = cmds.floatSliderGrp(label="相似度差异值:", field=True, min=0, max=1, value=load_data('TEX_PROCESSING_DATA')["Path_Detection"]["similarity_range"] ,
                                                      precision=5,
                                                      p=Node_Path_Matching_layout, width= 500,
                                                    cc = lambda *args :self.ModifyConfigurationFile(cmds.floatSliderGrp(similarity_range_slider, query=True, value=True), ["Path_Detection", "similarity_range"]),
                                                    dc = lambda *args :self.ModifyConfigurationFile(cmds.floatSliderGrp(similarity_range_slider, query=True, value=True), ["Path_Detection", "similarity_range"]))

        length_weight_slider = cmds.floatSliderGrp(label="内容相似/长度判断权重:", field=True, min=0, max=1, value=load_data('TEX_PROCESSING_DATA')["Path_Detection"]["length_weight"] ,
                                                   precision=5,
                                                   p=Node_Path_Matching_layout, width= 500,
                                                    cc = lambda *args :self.ModifyConfigurationFile(cmds.floatSliderGrp(length_weight_slider, query=True, value=True), ["Path_Detection", "length_weight"]),
                                                    dc = lambda *args :self.ModifyConfigurationFile(cmds.floatSliderGrp(length_weight_slider, query=True, value=True), ["Path_Detection", "length_weight"]))
        #------------------------>节点路径匹配   结束
        cmds.setParent(tab_layout)
        cmds.tabLayout(tab_layout, edit=True, tabLabel=((TexFirstFilter_scroll_layout, '魔法连接')))
        cmds.tabLayout(tab_layout, edit=True, tabLabel=((ColorSpace_scroll_layout, '颜色空间')))
        cmds.tabLayout(tab_layout, edit=True, tabLabel=((Node_Connection_layout, '节点连接')))
        cmds.tabLayout(tab_layout, edit=True, tabLabel=((Node_Path_Matching_layout, '节点路径匹配')))

    def TexFirstFilterData_modify(self, channel):
        for i in self.TexFirstFilter_widgets_name:
            if channel == i:
                #...读取文件
                TexFirstFilterData = load_data('TEX_PROCESSING_DATA')
                #...处理写入值，并强制转为大写
                input_str = "['" + "','".join(cmds.textField(self.TexFirstFilter_widgets_name[i], query=True, text=True).split(",")) + "']"
                input_str = input_str.upper()
                output_list = ast.literal_eval(input_str)

                #...并修改
                TexFirstFilterData["TexFirstFilter"][0]["TexFirstFilterData"][channel] = output_list
                write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)

    def TexSoloFilterData_modify(self, channel):
        for i in self.TexSoloFilter_widgets_name:
            if channel == i:
                #...读取文件
                TexFirstFilterData = load_data('TEX_PROCESSING_DATA')
                #...处理写入值，并强制转为大写
                input_str = "['" + "','".join(cmds.textField(self.TexSoloFilter_widgets_name[i], query=True, text=True).split(",")) + "']"
                input_str = input_str.upper()
                output_list = ast.literal_eval(input_str)

                #...并修改
                TexFirstFilterData["TexFirstFilter"][1]["TexSoloFilterData"][channel] = output_list
                write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)

    def ColorSpaceData_modify(self, tx_val):
        #...读取文件
        TexFirstFilterData = load_data('TEX_PROCESSING_DATA')

        #...处理写入值
        input_str = "['" + "','".join(tx_val.split(",")) + "']" # 转为列表字符串
        output_list = ast.literal_eval(input_str) # 转为列表
        output_list = [s.strip() for s in output_list] # 删除所有的空格
        #...并修改
        TexFirstFilterData["ColorSpace"][0]["ColorSpaceData"] = output_list
        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)

    def SetTexFirstFilterOptions(self, selected_items):

        TEX_PROCESSING_DATA = load_data('TEX_PROCESSING_DATA')
        for key , val in TEX_PROCESSING_DATA["ProcSet_Options"]["TexFirstFilter_Options"].items():
            # 先把所有值改为False
            TEX_PROCESSING_DATA["ProcSet_Options"]["TexFirstFilter_Options"][key] = False
            for i in selected_items:
                if i == key:
                    TEX_PROCESSING_DATA["ProcSet_Options"]["TexFirstFilter_Options"][key] = True

        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TEX_PROCESSING_DATA)

    def SetAuto_Node_Connection_Options(self, selected_items):

        TEX_PROCESSING_DATA = load_data('TEX_PROCESSING_DATA')
        for key , val in TEX_PROCESSING_DATA["ProcSet_Options"]["Auto_Node_Connection_Options"].items():
            # 先把所有值改为False
            TEX_PROCESSING_DATA["ProcSet_Options"]["Auto_Node_Connection_Options"][key] = False
            for i in selected_items:
                if i == key:
                    TEX_PROCESSING_DATA["ProcSet_Options"]["Auto_Node_Connection_Options"][key] = True

        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TEX_PROCESSING_DATA)

    def exclude_list_modify(self, tx_val):
        #...读取文件
        TexFirstFilterData = load_data('TEX_PROCESSING_DATA')

        #...处理写入值
        input_str = "['" + "','".join(tx_val.split(",")) + "']" # 转为列表字符串
        output_list = ast.literal_eval(input_str) # 转为列表
        output_list = [s.strip() for s in output_list] # 删除所有的空格
        #...并修改
        TexFirstFilterData["Path_Detection"]["exclude_list"] = output_list
        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)

    def format_list_modify(self, tx_val):
        #...读取文件
        TexFirstFilterData = load_data('TEX_PROCESSING_DATA')

        #...处理写入值
        input_str = "['" + "','".join(tx_val.split(",")) + "']" # 转为列表字符串
        output_list = ast.literal_eval(input_str) # 转为列表
        output_list = [s.strip() for s in output_list] # 删除所有的空格
        #...并修改
        TexFirstFilterData["Path_Detection"]["format_list"] = output_list
        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)

    def NodeListField_modify(self, Channel ,tx_val):
        #...读取文件
        TexFirstFilterData = load_data('TEX_PROCESSING_DATA')

        #...处理写入值
        input_str = "['" + "','".join(tx_val.split(",")) + "']" # 转为列表字符串
        output_list = ast.literal_eval(input_str) # 转为列表
        output_list = [s.strip() for s in output_list] # 删除所有的空格
        #...并修改
        TexFirstFilterData["ProcSet_Options"]["ProcessingNodeData"][Channel]["NodeList"] = output_list
        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)


    def AddNodeButton_modify(self, Channel ,tx_val, textField_Name):
        SlNode = list(process_sl_data().keys())[0]
        #...读取文件
        TexFirstFilterData = load_data('TEX_PROCESSING_DATA')
        if keyboard.is_pressed('alt'):
            output_list = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["ProcessingNodeData"][Channel]["NodeList"]
            output_list.pop()
        else:
            cont = tx_val +',' +SlNode
            #...处理写入值
            input_str = "['" + "','".join(cont.split(",")) + "']" # 转为列表字符串
            output_list = ast.literal_eval(input_str) # 转为列表
            output_list = [s.strip() for s in output_list] # 删除所有的空格
        #...并修改

        TexFirstFilterData["ProcSet_Options"]["ProcessingNodeData"][Channel]["NodeList"] = output_list
        write_data(Script_path+ '\TEX_PROCESSING_DATA.json', TexFirstFilterData)

        ProcessingNodeData = load_data('TEX_PROCESSING_DATA')["ProcSet_Options"]["ProcessingNodeData"]
        cmds.textField(textField_Name, edit= True, text=str(ProcessingNodeData[Channel]["NodeList"])
                .replace('[', '')
                .replace(']', '')
                .replace("'", "")
                .replace(",", " , "))

    # ...设置一些参数的函数

    # def ProcessInputString(self):
    # pass

    def ModifyConfigurationFile(self, value, key_path):
            """
            修改配置文件函数。

            参数:
            value -- 要设置的新值
            key_path -- 包含要修改的键的路径，以列表形式传递，例如 ["ProcSet_Options", "MagicConnectionSetColorSpace"]
            """
            # 读取文件
            TEX_PROCESSING_DATA = load_data('TEX_PROCESSING_DATA')

            # 根据给定的键路径设置值
            current_level = TEX_PROCESSING_DATA
            for key in key_path[:-1]:  # 迭代到倒数第二个键
                current_level = current_level[key]  # 进入下一层级
            current_level[key_path[-1]] = value  # 设置最终键的值

            # 修改并写回文件
            write_data(Script_path + '\TEX_PROCESSING_DATA.json', TEX_PROCESSING_DATA)


    # 设置菜单的函数

    # resetData删除配置文件
    def resetData(self):
        os.remove(Script_path+'\RENDERING_WRITE_OPTION_DATA.json')
        os.remove(Script_path+'\TEX_PROCESSING_DATA.json')



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

        self.TextureManager_texture_table_data_temp_path = Script_path + "\\Temp\\TM_texture_table_data.bin"
        self.TextureManager_config_path = Script_path + "\\Datas\\texture_manager\\TM_config_data.bin"


        language = self.dataM.ascii_load_data(os.path.join(Script_path, "TEX_PROCESSING_DATA.json"))["Other_Settings"]["language"]
        # 建语言文件路径
        language_file_path = os.path.join(Script_path, "Datas", "languages", f"{language}.json")
        # 加载语言文件
        self.DataPLT = self.dataM.ascii_load_data(language_file_path)['ArnoldMagicNode']['TM_WIN']


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

        self.WINDOWS_NAME = f"{self.DataPLT['__init__']['WINDOWS_NAME']}  {SoftwareState} : {SoftwareVersion}    {self.DataPLT['__init__']['remaining_time']} : {str(LicenseV_remaining_time)}{self.DataPLT['__init__']['day']}"

        # 判断窗口是否存在，如果存在则删除
        delete_window_if_existe('TextureManagerWin')



        self.setObjectName('TextureManagerWin')
        self.setWindowTitle(self.WINDOWS_NAME)
        self.setWindowIcon(QtGui.QIcon(Icon_path + "\\TXManagerShelf_200.png"))
        #...窗口长宽
        self.setMinimumHeight(1050)
        self.setMinimumWidth(2500)









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
        lang = self.DataPLT['create_widgets']

        # MaterialListSearch 搜索框
        self.MaterialListSearch = QtWidgets.QLineEdit()
        self.MaterialListSearch.textChanged.connect(lambda item: self.material_list_search())
        self.MaterialListSearch.setFixedWidth(350)
        self.MaterialListSearch.setFixedHeight(40)
        self.MaterialListSearch.setPlaceholderText(lang['MaterialListSearch_placeholder']) # 输入要搜索的材质球名称
        # MaterialListSearch 搜索框一些控件

        # 材质列表刷新
        self.MaterialList_Refresh_Button = QtWidgets.QPushButton()
        self.MaterialList_Refresh_Button.setIcon(QtGui.QIcon(Icon_path + "\\ResetMode_200.png"))
        self.MaterialList_Refresh_Button.clicked.connect(lambda *args: (self.refresh_scene_node_info(),
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
        self.MaterialList_Display_Slider.valueChanged.connect(lambda *args: self.updateMaterialListSlider())

        # TexturelListSearch 搜索框
        self.TexturelListSearch = QtWidgets.QLineEdit()
        self.TexturelListSearch.textChanged.connect(lambda item: self.texture_list_search())
        self.TexturelListSearch.setFixedHeight(40)
        self.TexturelListSearch.setPlaceholderText(lang['TexturelListSearch_placeholder']) # 输入要搜索的贴图球名称
        # TexturelListSearch 搜索框一些控件

        # 贴图列表的刷新
        self.TexturelList_Refresh_Button = QtWidgets.QPushButton()
        self.TexturelList_Refresh_Button.setIcon(QtGui.QIcon(Icon_path + "\\ResetMode_200.png"))
        self.TexturelList_Refresh_Button.setFixedWidth(40)
        self.TexturelList_Refresh_Button.setFixedHeight(40)
        self.TexturelList_Refresh_Button.setIconSize(QtCore.QSize(32, 32))
        self.TexturelList_Refresh_Button.clicked.connect(lambda: self.refresh_texture_table())
        self.TexturelList_Refresh_Button.setToolTip(lang['TexturelList_Refresh_Button_ToolTip']) # 根据缓存进行重新刷新

        # 全选材质节点
        self.MaterialList_SelectAll_Button = QtWidgets.QPushButton()
        self.MaterialList_SelectAll_Button.setIcon(QtGui.QIcon(Icon_path + "\\render_aiStandardSurface_Select.png"))
        self.MaterialList_SelectAll_Button.setFixedWidth(40)
        self.MaterialList_SelectAll_Button.setFixedHeight(40)
        self.MaterialList_SelectAll_Button.clicked.connect(lambda: self.all_selected_materials())
        self.MaterialList_SelectAll_Button.setIconSize(QtCore.QSize(32, 32))

        # 取消所有选择
        self.TexturelList_Unselect_All_Button = QtWidgets.QPushButton(lang['TexturelList_Unselect_All_Button']) # 取消全选
        self.TexturelList_Unselect_All_Button.clicked.connect(lambda: (
            self.MaterialList.clearSelection(),
            self.TEXTURELIST_MODEL.removeRows(0, self.TEXTURELIST_MODEL.rowCount())
        ))
        self.TexturelList_Unselect_All_Button.setFixedHeight(40)

        # 反选
        self.TexturelList_reverse_selection = QtWidgets.QPushButton(lang['TexturelList_reverse_selection']) # 反选
        self.TexturelList_reverse_selection.setFixedHeight(40)
        self.TexturelList_reverse_selection.clicked.connect(lambda: self.texture_list_reverse_selection())

        # 一键选出所有缺失贴图
        self.TexturelList_Find_Missing_Textures_Button = QtWidgets.QPushButton(lang['TexturelList_Find_Missing_Textures_Button']) # 选出缺失
        self.TexturelList_Find_Missing_Textures_Button.clicked.connect(
            lambda: self.texture_list_find_missing_textures())
        self.TexturelList_Find_Missing_Textures_Button.setFixedHeight(40)

        # 选出最大贴图的按钮
        self.TexturelList_Intelligent_Find_Max_Size_Button = QtWidgets.QPushButton(lang['TexturelList_Intelligent_Find_Max_Size_Button']) # 选出大贴图
        self.TexturelList_Intelligent_Find_Max_Size_Button.clicked.connect(
                                                                            lambda: self.texture_list_intelligent_find_max_size(self.dataM.bin_load_data(self.TextureManager_config_path)['listwidget_data']))
        self.TexturelList_Intelligent_Find_Max_Size_Button.setFixedHeight(40)

        # 选出最大贴图的容错率值
        self.tolerance_doubleSpinBox = QtWidgets.QDoubleSpinBox(self)
        self.tolerance_doubleSpinBox.setMinimum(0.0)  # 设置最小值
        self.tolerance_doubleSpinBox.setMaximum(10000.0)  # 设置最大值
        self.tolerance_doubleSpinBox.setValue(50.0)  # 设置默认值
        self.tolerance_doubleSpinBox.setSingleStep(0.1)  # 设置步长
        self.tolerance_doubleSpinBox.setDecimals(2)  # 设置小数点后的位数
        self.tolerance_doubleSpinBox.setFixedHeight(40)
        self.tolerance_doubleSpinBox.valueChanged.connect(
            lambda: self.TM_modify_config('listwidget_data', self.tolerance_doubleSpinBox.value()))

        # 替换名称
        self.TexturelList_Search_And_Replace_Date_Button = QtWidgets.QPushButton(
            lang['TexturelList_Search_And_Replace_Date_Button'])
        self.TexturelList_Search_And_Replace_Date_Button.setFixedHeight(40)
        self.TexturelList_Search_And_Replace_Date_Button.clicked.connect(lambda: self.batch_replace_data_Win())

        # 找回所有缺失路径
        self.TexturelList_Replace_Data_Button = QtWidgets.QPushButton(lang['TexturelList_Replace_Data_Button']) # 找回路径
        self.TexturelList_Replace_Data_Button.setFixedHeight(40)
        self.TexturelList_Replace_Data_Button.clicked.connect(lambda: self.find_path_re_Win())

        # 压缩贴图
        self.TexturelList_Processed_Image_Button = QtWidgets.QPushButton(lang['TexturelList_Processed_Image_Button']) # 处理图像
        self.TexturelList_Processed_Image_Button.setFixedHeight(40)
        self.TexturelList_Processed_Image_Button.clicked.connect(lambda: self.image_processing_Win())

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
        self.TexturelList.clicked.connect(lambda *args: self.selection_texture_sl_node_delay_selection_signal())

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
        Texture_Search_Layout.addWidget(self.TexturelList_reverse_selection)
        Texture_Search_Layout.addWidget(self.TexturelList_Find_Missing_Textures_Button)
        Texture_Search_Layout.addWidget(self.TexturelList_Intelligent_Find_Max_Size_Button)
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
        QtCore.QTimer.singleShot(0, lambda: self.select_nodes([item.text() for item in self.MaterialList.selectedItems()]))

    # 刷新material_list列表控件
    def refresh_material_list(self):
        # 刷新列表前先把列表清除干净
        self.MaterialList.clear()

        for mat_node_name in self.MterialNodeAllInfoDict:
            item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\render_aiImage.png"), mat_node_name)

            try:
                # 场景中存在的对象都可以获取到材质的类型
                node_type = cmds.nodeType(mat_node_name)
            except:
                # 如果获取不到就是缺失的贴图列表
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\render_aiImage.png"), mat_node_name)
                self.MaterialList.addItem(item)
                break

            if node_type == 'lambert':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\lambert.svg"), mat_node_name)

            elif node_type == 'standardSurface':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\standardSurface.svg"), mat_node_name)

            elif node_type == 'aiStandardSurface':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\render_aiStandardSurface.png"),
                                                 mat_node_name)

            elif node_type == 'aiStandardVolume':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\render_aiVolumeCollector.png"),
                                                 mat_node_name)

            elif node_type == 'aiStandardHair':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\render_aiHair.png"), mat_node_name)

            elif node_type == 'blinn':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\blinn.svg"), mat_node_name)

            elif node_type == 'phongE':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\phongE.svg"), mat_node_name)

            elif node_type == 'phong':
                item = QtWidgets.QListWidgetItem(QtGui.QIcon(Icon_path + "\\phong.svg"), mat_node_name)

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
        #       item = QtWidgets.QListWidgetItem(QtGui.QIcon (Icon_path + "\\render_aiStandardSurface.png"), matNodeName)
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
        QtCore.QTimer.singleShot(0,lambda *args: self.selection_texture_sl_node())

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
        QtCore.QTimer.singleShot(0,lambda: self.select_nodes(selected_data))

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

        self.config_path = os.path.join(Script_path, 'Datas', 'texture_manager', 'TM_find_and_replace_config.bin') # 历史写入路径

        language = self.dataM.ascii_load_data(os.path.join(Script_path, "TEX_PROCESSING_DATA.json"))["Other_Settings"]["language"]
        # 建语言文件路径
        language_file_path = os.path.join(Script_path, "Datas", "languages", f"{language}.json")
        # 加载语言文件
        self.DataPLT = self.dataM.ascii_load_data(language_file_path)['ArnoldMagicNode']['TM_FAR_WIN']

        # 命名常量命名
        WINDOWS_NAME =  self.DataPLT['__init__']['WINDOWS_NAME'] + WinName #Win名称

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
        lang = self.DataPLT['create_widgets']  # 获取当前语言的数据

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
            lambda *args: self.modify_config('search_content', self.line_edit_find.text()))

        self.label_replace = QtWidgets.QLabel(lang['label_replace'])  # ↓ ↓ ↓ ↓ ↓ ↓
        self.label_replace.setFont(font_10x)
        self.label_replace.setAlignment(QtCore.Qt.AlignCenter)  # 居中文字

        self.line_edit_replace = QtWidgets.QLineEdit()
        self.line_edit_replace.setFixedHeight(40)
        self.line_edit_replace.setPlaceholderText(lang['line_edit_replace_placeholder'])  # 请输入替换内容...
        self.line_edit_replace.textChanged.connect(
            lambda *args: self.modify_config('replace_content', self.line_edit_replace.text()))

        # 创建第三行的控件（复选框）
        self.checkbox_case_sensitive = QtWidgets.QCheckBox(lang['checkbox_case_sensitive'])  # 大小写忽略
        self.checkbox_case_sensitive.stateChanged.connect(
            lambda *args: self.modify_config('case_sensitive', self.checkbox_case_sensitive.isChecked()))

        self.checkbox_regex = QtWidgets.QCheckBox(lang['checkbox_regex'])  # 使用正则表达式
        self.checkbox_regex.stateChanged.connect(
            lambda *args: self.modify_config('use_regex', self.checkbox_regex.isChecked()))

        # 创建第四行的控件（替换按钮）
        self.button_replace = QtWidgets.QPushButton(lang['button_replace'])  # 替换
        self.button_replace.clicked.connect(lambda *args: self.replace_button())

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
        WINDOWS_NAME =  self.DataPLT['initialize_window_config']['WINDOWS_NAME'] + WinName #Win名称

        delete_window_if_existe('TM_RepathFiles_Win')

        self.setObjectName('TM_RepathFiles_Win')
        self.setWindowTitle(WINDOWS_NAME)

        #...窗口长宽
        #self.setMinimumHeight(400)
        self.setMinimumWidth(650)

    # 初始化全局设置
    def initial_global_config(self):
        # 实例数据管理器
        self.dataM = DataManager()
        self.dataP = DataProcessor()
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData() # 获取节点数据模块

        language = self.dataM.ascii_load_data(os.path.join(Script_path, "TEX_PROCESSING_DATA.json"))["Other_Settings"]["language"]
        # 建语言文件路径
        language_file_path = os.path.join(Script_path, "Datas", "languages", f"{language}.json")
        # 加载语言文件
        self.DataPLT = self.dataM.ascii_load_data(language_file_path)['ArnoldMagicNode']['TM_RF_WIN']

        self.TM_repath_files_config_FilePath = os.path.join(Script_path, "Datas", "texture_manager", "TM_repath_files_config.bin")

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
        self.select_folder_button.clicked.connect(lambda *args:self.select_folder())

        self.memory_search_mode_checkbox = QtWidgets.QCheckBox(
            self.DataPLT['create_widgets']['memory_search_mode_checkbox'])  # 记忆搜索模式
        self.memory_search_mode_checkbox.setEnabled(False)

        self.search_subfolders_checkbox = QtWidgets.QCheckBox(self.DataPLT['create_widgets']['search_subfolders_checkbox']) # 搜索子文件夹
        self.search_subfolders_checkbox.stateChanged.connect(
            lambda *args: self.modify_config('search_subfolders_checkbox', self.search_subfolders_checkbox.isChecked()))

        self.multiple_subfolder_search_checkbox = QtWidgets.QCheckBox(self.DataPLT['create_widgets']['multiple_subfolder_search_checkbox']) # 多个子文件夹搜索
        self.multiple_subfolder_search_checkbox.stateChanged.connect(
            lambda *args: self.modify_config('multiple_subfolder_search_checkbox', self.multiple_subfolder_search_checkbox.isChecked()))

        self.ignore_case_checkbox = QtWidgets.QCheckBox(self.DataPLT['create_widgets']['ignore_case_checkbox']) # 忽略大小写
        self.ignore_case_checkbox.stateChanged.connect(
            lambda *args: self.modify_config('ignore_case_checkbox', self.ignore_case_checkbox.isChecked()))

        self.fix_path_button = QtWidgets.QPushButton(self.DataPLT['create_widgets']['fix_path_button'])
        self.fix_path_button.clicked.connect(lambda *args: self.fix_path())

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

# 贴图管理器的图像处理界面
# 支持转换格式和压缩图像
class TM_ImageProcessing(QtWidgets.QDialog):
    def __init__(self, WinName = '', parent=None):
        super(TM_ImageProcessing, self).__init__(parent)

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
        WINDOWS_NAME =  'TM_ImageProcessing' + WinName #Win名称

        delete_window_if_existe('TM_ImageProcessing_Win')

        self.setObjectName('TM_ImageProcessing_Win')
        self.setWindowTitle(WINDOWS_NAME)

        #...窗口长宽
        #self.setMinimumHeight(400)
        self.setMinimumWidth(650)

    def initial_global_config(self):
        pass

    def create_widgets(self):
        self.format_combo_box_label = QtWidgets.QLabel("格式：")

        format_list = ['jpg', 'png', 'tif', 'bmp', 'tga']
        self.format_combo_box = QtWidgets.QComboBox()
        self.format_combo_box.addItems(format_list)  # 添加选项

        # 创建一个显示输入结果的 QLabel
        self.zoom_ratios_combo_box_label = QtWidgets.QLabel("缩放：")

        # 创建可编辑的 QComboBox
        self.zoom_ratios_combo_box = QtWidgets.QComboBox()
        self.zoom_ratios_combo_box.setEditable(True)  # 设置为可编辑状态
        self.zoom_ratios_combo_box.addItems(["10%", "25%", "33%", "50%", "75%", "85%", "100%"])  # 添加选项

        # 设置 zoom_ratios_combo_box 的参数
        self.zoom_ratios_combo_box.setFixedWidth(80)

        # 创建一个显示输入结果的 QLabel
        self.resampling_mode_combo_box_label = QtWidgets.QLabel("重新取样：")

        # 重采样的模式
        resampling_mode_list = ['最近邻插值', '双线性插值', '三次插值', 'Lanczos 插值', '区域插值', '填充插值外点', '逆映射插值']
        self.resampling_combo_box = QtWidgets.QComboBox()
        self.resampling_combo_box.addItems(resampling_mode_list)  # 添加选项


        # jpg的参数设置面板
        self.jpg_quality_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        # jpg_quality_slider控件的设置
        # 设置最小值为0，最大值为100，步长为5
        self.jpg_quality_slider.setMinimum(0)
        self.jpg_quality_slider.setMaximum(100)
        self.jpg_quality_slider.setTickInterval(5)  # 设置刻度间隔为5
        self.jpg_quality_slider.setSingleStep(5)  # 设置滑动步长为5
        self.jpg_quality_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)  # 设置刻度显示在滑杆下方



    def create_layouts(self):

        # 第一层的多选格式的控件
        combo_layout = QtWidgets.QHBoxLayout()
        combo_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        combo_layout.addWidget(self.format_combo_box_label)
        combo_layout.addWidget(self.format_combo_box)
        combo_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        combo_layout.addWidget(self.zoom_ratios_combo_box_label)
        combo_layout.addWidget(self.zoom_ratios_combo_box)
        combo_layout.addItem(
            QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred))
        combo_layout.addWidget(self.resampling_mode_combo_box_label)
        combo_layout.addWidget(self.resampling_combo_box)

        jpg_config_layout = QtWidgets.QHBoxLayout()
        jpg_config_layout.addWidget(self.jpg_quality_slider)



        Main_Layout = QtWidgets.QVBoxLayout()
        Main_Layout.addLayout(combo_layout)
        Main_Layout.addLayout(jpg_config_layout)
        # 设置窗口的主布局
        self.setLayout(Main_Layout)

    def initial_widgets_settings(self):
        pass
        # self.zoom_ratios_combo_box_label.setVisible(False)
        # self.zoom_ratios_combo_box.setVisible(False)
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
class color_space_preset_menu(object):
    def __init__(self,color_space_preset):
        self.feedback = FeedbackPrompt() # 错误提示模块

        # 如果没有选择节点会返回None，返回None会关闭函数
        if process_sl_data() == None:
            return
        else:
            sl_data = process_sl_data()

        color_space_list = load_data('TEX_PROCESSING_DATA')["ColorSpace"][0]['ColorSpaceData']

        for i in sl_data['file']:
            cmds.setAttr(i + '.colorSpace', color_space_preset, type='string')
            self.feedback.CP(f"已经把<{i}>设置成<{color_space_preset}>")

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

        node_pro.unify_uv_node(process_sl_data()['file'], uv_list)



# 渲染预设菜单设置
class rendering_preset_menu(object):

    def __init__(self,menu_sl_val):

        self.feedback = FeedbackPrompt() # 错误提示模块

        self.attribute_types = ["bool", "int", "float", "string"]
        self.rederer_attribute_types = ["bool", "float", "string"]
        self.Render_settings_Data =  load_data(f"\Datas\Render_settings\{menu_sl_val}" )

        RENDERING_WRITE_OPTION_DICT =  load_data("RENDERING_WRITE_OPTION_DATA") # 读取渲染文件

        if RENDERING_WRITE_OPTION_DICT['default_rendering_properties_write_options'] == True:
            self.set_default_rendering_properties()

        if RENDERING_WRITE_OPTION_DICT['rendering_properties_write_options'] == True:
            self.set_rendering_properties()

        if RENDERING_WRITE_OPTION_DICT['AOV_properties_properties_write_options'] == True:
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

    # 获取默认渲染节点设置
    def get_default_rendering_properties(self):

        defaultRenderGlobals_options = ["animation", "animationRange", "applyFogInPost", "binMembership", "bitDepth", "blur2DMemoryCap", "blurLength", "blurSharpness", "bottomRegion", "bufferName", "byFrameStep", "caching", "clipFinalShadedColor", "colorProfileEnabled", "comFrrt", "composite", "compositeThreshold", "createIprFile", "currentRenderer", "defaultTraversalSet", "enableDefaultLight", "enableDepthMaps", "enableStrokeRender", "evenFieldExt", "exrCompression", "exrPixelType", "extensionPadding", "fieldExtControl", "fogGeometry", "forceTileSize", "frozen", "gammaCorrection", "geometryVector", "hyperShadeBinList", "ignoreFilmGate", "imageFilePrefix", "imageFormat", "imfPluginKey", "inputColorProfile", "interruptFrequency", "iprRenderMotionBlur", "iprRenderShading", "iprRenderShadowMaps", "iprShadowPass", "isHistoricallyInteresting", "jitterFinalColor", "keepMotionVector", "leafPrimitives", "leftRegion", "logRenderPerformance", "macCodec", "macDepth", "macQual", "matteOpacityUsesTransparency", "maximumMemory", "message", "motionBlur", "motionBlurByFrame", "motionBlurShutterClose", "motionBlurShutterOpen", "motionBlurType", "motionBlurUseShutter", "multiCamNamingMode", "nodeState", "numCpusToUse", "oddFieldExt", "onlyRenderStrokes", "optimizeInstances", "outFormatControl", "outFormatExt", "outputColorProfile", "oversamplePaintEffects", "oversamplePfxPostFilter", "periodInExt", "postFogBlur", "postFurRenderMel", "postMel", "postRenderLayerMel", "postRenderMel", "preFurRenderMel", "preMel", "preRenderLayerMel", "preRenderMel", "putFrameBeforeExt", "quality", "raysSeeBackground", "recursionDepth", "renderAll", "renderLayerEnable", "renderVersion", "rendercallback", "renderedOutput", "renderingColorProfile", "resolution", "reuseTessellations", "rightRegion", "shadingVector", "shadowPass", "shadowsObeyLightLinking", "shadowsObeyShadowLinking", "skipExistingFrames", "smoothColor", "smoothValue", "strokesDepthFile", "subdivisionHashSize", "subdivisionPower", "swatchCamera", "tiffCompression", "tileHeight", "tileWidth", "topRegion", "useBlur2DMemoryCap", "useDisplacementBoundingBox", "useFileCache", "useFrameExt", "useMayaFileName", "useRenderRegion"]
        defaultRenderQuality_options = ["binMembership", "blueThreshold", "caching", "coverageThreshold", "edgeAntiAliasing", "enableRaytracing", "frozen", "greenThreshold", "isHistoricallyInteresting", "maxShadingSamples", "maxVisibilitySamples", "message", "nodeState", "particleSamples", "pixelFilterType", "pixelFilterWidthX", "pixelFilterWidthY", "plugInFilterWeight", "rayTraceBias", "redThreshold", "reflections", "refractions", "renderSample", "shadingSamples", "shadows", "useMultiPixelFilter", "visibilitySamples", "volumeSamples"]
        defaultResolution_options =  ["aspectLock", "binMembership", "caching", "deviceAspectRatio", "dotsPerInch", "fields", "frozen", "height", "imageSizeUnits", "isHistoricallyInteresting", "lockDeviceAspectRatio", "message", "nodeState", "oddFieldFirst", "pixelAspect", "pixelDensityUnits", "width", "zerothScanline"]

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
        defaultArnoldDriver = ["aiTranslator", "aiUserOptions", "alphaHalfPrecision", "alphaTolerance", "append", "autocrop", "binMembership", "caching", "colorManagement", "deepexrTiled", "depthHalfPrecision", "depthTolerance", "dither", "exrCompression", "exrTiled", "frozen", "halfPrecision", "input", "isHistoricallyInteresting", "mergeAOVs", "message", "multipart", "nodeState", "outputMode", "outputPadded", "pngFormat", "pngSkipAlpha", "pngUnpremultAlpha", "prefix", "preserveLayerName", "quality", "renderSession", "skipAlpha", "subpixelMerge", "tiffCompression", "tiffFormat", "tiffTiled", "unpremultAlpha", "useRGBOpacity"]
        defaultArnoldFilter = ["aiFilterWeights", "aiTranslator", "aiUserOptions", "aiWidth", "binMembership", "caching", "domain", "filterWeights", "frozen", "isHistoricallyInteresting", "maximum", "message", "minimum", "nodeState", "scalarMode", "width"]
        defaultArnoldRenderOptions = ["AAAdaptiveThreshold", "AASampleClamp", "AASamples", "AASamplesMax", "AA_seed", "GIDiffuseDepth", "GIDiffuseSamples", "GISpecularDepth", "GISpecularSamples", "GISssSamples", "GITotalDepth", "GITransmissionDepth", "GITransmissionSamples", "GIVolumeDepth", "GIVolumeSamples", "GI_glossy_samples", "GI_refraction_samples", "IPRRefinementFinished", "IPRRefinementStarted", "IPRStepFinished", "IPRStepStarted", "PostTranslation", "abortOnError", "abortOnLicenseFail", "absoluteProceduralPaths", "absoluteTexturePaths", "aiUserOptions", "aovMode", "atmosphere", "autoTransparencyDepth", "autotile", "autotx", "avpRegionBottom", "avpRegionLeft", "avpRegionRight", "avpRegionTop", "background", "binMembership", "binaryAss", "bucketScanning", "bucketSize", "caching", "clear_before_render", "denoiseBeauty", "dielectricPriorities", "displayAOV", "driver", "enableAdaptiveSampling", "enableProgressiveRender", "enable_swatch_render", "errorColorBadPixel", "errorColorBadPixelB", "errorColorBadPixelG", "errorColorBadPixelR", "errorColorBadTexture", "errorColorBadTextureB", "errorColorBadTextureG", "errorColorBadTextureR", "expandProcedurals", "exportAllShadingGroups", "exportDagName", "exportFullPaths", "exportMayaUsd", "exportNamespace", "exportPrefix", "exportSeparator", "exportShadingEngine", "filter", "filterType", "forceTranslateShadingEngines", "force_scene_update_before_IPR_refresh", "force_texture_cache_flush_after_render", "frozen", "globalLightSamplesEnabled", "gpuDefaultMinMemoryMB", "gpuDefaultNames", "gpu_max_texture_resolution", "ignoreAtmosphere", "ignoreBump", "ignoreDisplacement", "ignoreDof", "ignoreImagers", "ignoreLights", "ignoreMotion", "ignoreMotionBlur", "ignoreOperators", "ignoreShaders", "ignoreShadows", "ignoreSmoothing", "ignoreSss", "ignoreSubdivision", "ignoreTextures", "ignore_list", "imageFormat", "indirectSampleClamp", "indirectSpecularBlur", "isHistoricallyInteresting", "kickRenderFlags", "lightLinking", "lightSamples", "lock_sampling_noise", "log_filename", "log_max_warnings", "log_to_console", "log_to_file", "log_verbosity", "lowLightThreshold", "manual_gpu_devices", "maxSubdivisions", "mb_camera_enable", "mb_lights_enable", "mb_object_deform_enable", "mb_objects_enable", "mb_shader_enable", "message", "motion_blur_enable", "motion_end", "motion_frames", "motion_start", "motion_steps", "mtoa_translation_info", "nodeState", "offsetOrigin", "operator", "origin", "outputAssBoundingBox", "outputOverscan", "outputVarianceAOVs", "output_ass_compressed", "output_ass_filename", "output_ass_mask", "plugin_searchpath", "plugins_path", "preserve_scene_data", "procedural_searchpath", "profile_enable", "profile_file", "progressive_initial_level", "progressive_rendering", "range_type", "referenceTime", "regionMaxX", "regionMaxY", "regionMinX", "regionMinY", "renderDevice", "renderGlobals", "renderType", "renderUnit", "render_device_fallback", "sceneScale", "shadowLinking", "skipLicenseCheck", "sssUseAutobump", "standinDrawOverride", "stats_enable", "stats_file", "stats_mode", "subdivDicingCamera", "subdivFrustumCulling", "subdivFrustumPadding", "textureAcceptUnmipped", "textureAcceptUntiled", "textureAutoTxPath", "textureAutotile", "textureConservativeLookups", "textureDiffuseBlur", "textureMaxMemoryMB", "textureMaxOpenFiles", "textureSpecularBlur", "texture_searchpath", "threads", "threads_autodetect", "use_existing_tiled_textures", "use_sample_clamp", "use_sample_clamp_AOVs", "version"]

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
        aiAOV_att_list =  ["binMembership", "caching", "camera", "defaultValue", "denoise", "enabled", "filterType", "frozen", "globalAov", "imageFormat", "isHistoricallyInteresting", "lightGroups", "lightGroupsList", "lightPathExpression", "message", "name", "nodeState", "prefix", "type"]
        # 这是aiAOV中的所有属性
        aiDriver_att_list = ["aiTranslator", "aiUserOptions", "alphaHalfPrecision", "alphaTolerance", "append", "autocrop", "binMembership", "caching", "colorManagement", "deepexrTiled", "depthHalfPrecision", "depthTolerance", "dither", "exrCompression", "exrTiled", "frozen", "halfPrecision", "input", "isHistoricallyInteresting", "mergeAOVs", "message", "multipart", "nodeState", "outputMode", "outputPadded", "pngFormat", "pngSkipAlpha", "pngUnpremultAlpha", "prefix", "preserveLayerName", "quality", "renderSession", "skipAlpha", "subpixelMerge", "tiffCompression", "tiffFormat", "tiffTiled", "unpremultAlpha", "useRGBOpacity"]

        aiFilter_att_list = ["aiFilterWeights", "aiTranslator", "aiUserOptions", "aiWidth", "binMembership", "caching", "domain", "filterWeights", "frozen", "isHistoricallyInteresting", "maximum", "message", "minimum", "nodeState", "scalarMode", "width"]

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
        cmds.button(label="确定",c=lambda *args:determine())
        cmds.text(label=" | ")
        cmds.button(label="取消",c=lambda *args:cancellation())
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
            write_data_path =  Script_path + r"\Datas\Render_settings" # 路径

            # 02 把变量写入数据结构
            Render_settings = {
                'default_rendering_properties' : default_rendering_properties,
                'rendering_properties' : rendering_properties,
                'AOV_properties' : AOV_properties
            }

            # 03, 创建并写出渲染器属性
            if not os.path.exists(os.path.join(write_data_path, self.import_val+".json")):
                save_data(os.path.join(write_data_path, self.import_val+".json"), Render_settings)

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
    file_path = Script_path + '\\Datas\\Render_settings\\'
    os.remove(file_path + sl_name+ '.json')


    # # 3，重新添加控件的选项
    # renderer_data_path =  Script_path + "\\Data\\Render_settings\\renderer"

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
    # 获取连接到 AovList 端口的所有节点
    connections = cmds.listConnections("defaultArnoldRenderOptions.aovList", source=True)

    for aov in connections:
        # 获取当前属性状态
        enabled = cmds.getAttr(aov + ".enabled")

        # 如果 enabled 属性为 1，则将其设置为 0
        if enabled == 1:
            cmds.setAttr(aov + ".enabled", 0)

        # 否则，将 enabled 属性设置为 1
        else:
            cmds.setAttr(aov + ".enabled", 1)









# -----------------------自动连接的一些功能-start

# 魔法自动连接
def magic_connection_button():

    # 0.获取初始变量
    TexFirstFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][0]["TexFirstFilterData"]
    TexSoloFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][1]['TexSoloFilterData']
    FilterData = TexFirstFilterData
    FilterData.update(TexSoloFilterData)
    ProcessingNodeData = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['ProcessingNodeData'] # 相应贴图节点的参数
    ContOptions = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['TexFirstFilter_Options'] # 相应贴图是否要连接的参数
    Auto_Node_Connection_Options = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['Auto_Node_Connection_Options'] # 相应贴图是否要连接相应的节点
    MagicConnectionSetColorSpace = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['MagicConnectionSetColorSpace'] # 魔法连接启用色彩空间
    feedback = FeedbackPrompt() # 错误提示模块

    # 1.获取选择节点

    SlNode = process_sl_data()

    if SlNode == None:
        # 如果没有选择节点将会直接退出函数
        return

    if 'file' not in SlNode:
        # 检查SlNode字典中是否有file key 如果没有直接退出函数
        feedback.CP('没有<file>纹理节点，请选择纹理节点')
        return



    MatName = None
    # 2.创建材质球。
    # 1，如果点了Shift会自动创建一个材质球
    # 2，如果没有的话会自己寻找选择的节点是否有材质球属性，如果没有会直接return
    if keyboard.is_pressed('shift'):
        MatName = cmds.shadingNode('aiStandardSurface', asShader=True)
    else:
        if 'aiStandardSurface' in SlNode:
            # 检查 'aiStandardSurface' 键是否在字典中
            if SlNode['aiStandardSurface'] is not None:
                MatName = SlNode['aiStandardSurface'][0]
        else:
            feedback.CP('没有选择材质球')
            return


    # 3.重置材质球名字
    cmds.rename(MatName, SlNode['file'][0].split('_')[0])
    MatName = SlNode['file'][0].split('_')[0]

    # 4.执行匹配 连接创建处理节点并连接到材质球的操作
    NodePro = NodeProcessor()
    NodePro.AutoNodeConnect(SlNode, MatName, FilterData, ProcessingNodeData, ContOptions, Auto_Node_Connection_Options)

    # 5.设置色彩空间 如果自动色彩空间开启了就会设置
    if MagicConnectionSetColorSpace == True:
        NodePro.AutoSetTexColorSpace(SlNode['file'], FilterData)


def path_detection_connection_button():

    Path_Detection = load_data('TEX_PROCESSING_DATA')["Path_Detection"]

    matching_test_mode = True
    node_connection = False

    if keyboard.is_pressed('shift'):
        matching_test_mode = False
    if keyboard.is_pressed('alt'):
        matching_test_mode = False
        node_connection = True

    # 如果没有选择节点会返回None，返回None会关闭函数
    if process_sl_data() == None:
        return
    else:
        sl_data = process_sl_data()
        for node_name in sl_data['file']:
            # 创建 PathDetection 类的实例
            path_detection_instance = PathDetection()

            # 获取对饮节点路径下的内容并且过滤
            node_attr = path_detection_instance.get_node_path(node_name)

            # 处理数据并匹配数据
            exclude_list = Path_Detection['exclude_list']
            tex_name_list = path_detection_instance.detection_path_content(node_name, exclude_list)

            # 处理数据并匹配数据
            length_weight = Path_Detection['length_weight']
            format_list =  Path_Detection['format_list']

            TexFirstFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][0]["TexFirstFilterData"]
            TexSoloFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][1]['TexSoloFilterData']
            FilterData = TexFirstFilterData
            FilterData.update(TexSoloFilterData)
            case_sensitive = Path_Detection['case_sensitive']
            similarity_dict = path_detection_instance.process_name_data(node_name, tex_name_list, length_weight, format_list, FilterData, TexFirstFilterData, TexSoloFilterData, case_sensitive)

            # 判断数据匹配数据
            auto_max_val =  Path_Detection['auto_max_val']
            similarity_max =  Path_Detection['similarity_max']
            similarity_range = Path_Detection['similarity_range']
            near_one_value = Path_Detection['near_one_value']
            matching_list = path_detection_instance.determine_connection(similarity_dict, auto_max_val, similarity_max, similarity_range, near_one_value)

            # 删除掉选择的节点
            matching_list_pro = path_detection_instance.remove_matching_elements(os.path.basename(node_attr[node_name]['path']), matching_list)






            # 如果测试模式开启下面的节点就不会执行
            if matching_test_mode == True:
                return

            # 删除原本UV节点
            originalUvName = cmds.listConnections(node_name, source=True, destination=False)[-1]
            if originalUvName:
                if originalUvName != 'defaultColorMgtGlobals':
                    cmds.delete(originalUvName)

            # 创建节点
            node_name_list = path_detection_instance.create_node(os.path.dirname(node_attr[node_name]['path']), matching_list_pro, format_list)
            node_name_list.append(node_name)

            # 创建 NodeProcessor 类的实例
            NodePro = NodeProcessor()
            NodePro.unify_uv_node(node_name_list)

            node_name_dict = {}
            node_name_dict['file'] = node_name_list

            # 设置色彩空间 如果自动色彩空间开启了就会设置
            MagicConnectionSetColorSpace = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['PathDetectionConnectionSetColorSpace'] # 魔法连接启用色彩空间
            if MagicConnectionSetColorSpace == True:
                NodePro.AutoSetTexColorSpace(node_name_list, FilterData)






            if node_connection == False:
                return

            # 0.获取初始变量
            ProcessingNodeData = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['ProcessingNodeData'] # 相应贴图节点的参数
            ContOptions = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['TexFirstFilter_Options'] # 相应贴图是否要连接的参数
            Auto_Node_Connection_Options = load_data('TEX_PROCESSING_DATA')['ProcSet_Options']['Auto_Node_Connection_Options'] # 相应贴图是否要连接相应的节点

            # 1.获取选择节点
            SlNode = process_sl_data(node_name_list)

            # 2.创建材质球
            MatName = cmds.shadingNode('aiStandardSurface', asShader=True)

            # 3.重置材质球名字
            cmds.rename(MatName, SlNode['file'][0].split('_')[0])
            MatName = SlNode['file'][0].split('_')[0]

            # 4.执行匹配 连接创建处理节点并连接到材质球的操作
            NodePro.AutoNodeConnect(SlNode, MatName, FilterData, ProcessingNodeData, ContOptions, Auto_Node_Connection_Options)



# 自动设置颜色空间
def AutoSet_TexColorSpace():
    TexFirstFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][0]["TexFirstFilterData"]
    TexSoloFilterData = load_data('TEX_PROCESSING_DATA')["TexFirstFilter"][1]['TexSoloFilterData']
    FilterData = TexFirstFilterData
    FilterData.update(TexSoloFilterData)

    SlNode = process_sl_data()
    NodePro = NodeProcessor()
    NodePro.AutoSetTexColorSpace(SlNode['file'], FilterData)

# -----------------------自动连接的一些功能-end



def Main_program():
    # cached_device_fingerprint, public_key, public_password, remaining_time
    global LicenseV_device_fingerprint, LicenseV_public_key, LicenseV_public_password, LicenseV_remaining_time

    # # 把验证完的相关信息传回主程序，备着使用
    # LicenseV_device_fingerprint = cached_device_fingerprint
    # LicenseV_public_key = public_key
    # LicenseV_public_password = public_password
    # LicenseV_remaining_time = remaining_time



    # dataM = DataManager()   # 实例一个数据库
    #
    # # 判断脚本路径下也没有这个文件
    # if not os.path.exists(os.path.join(Script_path,'TEX_PROCESSING_DATA.json')):
    #   #创建这个文件TexFirstFilterData
    #   save_data(os.path.join(Script_path,'TEX_PROCESSING_DATA.json'),TEX_PROCESSING_DATA)
    #
    # if not os.path.exists(os.path.join(Script_path,'RENDERING_WRITE_OPTION_DATA.json')):
    #   #创建这个文件TexFirstFilterData
    #   save_data(os.path.join(Script_path,'RENDERING_WRITE_OPTION_DATA.json'),RENDERING_WRITE_OPTION_DATA)

    # 创建窗口
    indowInstance = Arnold_Magic_Node_UI()
    # TextureManagerWinInstance()
