"""Arnold Magic Node 的 Maya 主窗口界面。"""

import os

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from ..arnold_magic_core import DataManager, FeedbackPrompt, GetNodeData
from ..core.storage import ensure_directory

# 迁移期兼容层：主窗口仍调用 application.py 中尚未拆分的旧实现。
# application.Main_program() 会在旧模块完整加载后延迟导入并重载 UI 模块。
from ..application import (
    AMS_Config,
    AutoSet_TexColorSpace,
    SceneNameOptimization,
    SoftwareState,
    SoftwareVersion,
    ai_aov_switch_button,
    all_convert_old_materials_to_arnold_button,
    all_intelligent_material_repair_button,
    auto_set_file_node_udim,
    color_space_preset_menu,
    direct_connection_button,
    icon_path,
    intelligent_mix,
    language_loading,
    path_detection_connection_button,
    quick_connect_node_button,
    render_preset_path,
    rendering_preset_menu,
    select_convert_old_materials_to_arnold_button,
    select_intelligent_material_repair_button,
    settings_path,
    unify_uv_node_button,
    uv_preset_menu,
)
from ..tools.magic_connection import run_magic_connection
from .aov_dialog import AOVLightGroupManagerInstance
from .qt import QtGui, QtWidgets, wrapInstance
from .rendering_preset_dialog import (
    delete_rendering_preset_menuItem,
    modify_rendering_preset_menuItem,
    rendering_preset_settings_button,
)
from .settings_dialog import ArnoldMagicNodeSettingsPanel


class MainWindow(object):
    def __init__(self):

        # 初始化窗口标题，显示软件状态和版本等信息
        WIN_TITLE = f"Arnold Magic Node  {SoftwareState} : {SoftwareVersion}"

        # 检查窗口是否已存在，如果存在则删除
        if cmds.window(WIN_TITLE, exists=True):
            cmds.deleteUI(WIN_TITLE)

        # 创建主窗口
        self.window = cmds.workspaceControl(WIN_TITLE, retain=False, floating=True, w=300, h=300)

        # 拿到 Maya 内部的 Qt 窗口指针
        ptr = omui.MQtUtil.findWindow(WIN_TITLE)
        if ptr:
            # 把指针包装成 QWidget
            qt_win = wrapInstance(int(ptr), QtWidgets.QWidget)
            # 设置标题栏图标
            logo_path = os.path.join(icon_path, "Logo_B.svg")
            qt_win.setWindowIcon(QtGui.QIcon(logo_path))
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
        # # 贴图批量导入器选项
        # cmds.menuItem(
        #     label=self.language['create_widgets']['ttpldrq_menu'],
        #     c=lambda *args: TextureBatchImporterWin(),
        #     i=icon_path + "\\RenderToTextureShelf_200.png"
        # )


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


        cmds.menuItem(divider=True, label='材质修复工具')

        cmds.menuItem(label='修复选择的FBX材质',
                      c = lambda *args: select_convert_old_materials_to_arnold_button())

        # 修复所有FBX材质
        cmds.menuItem(label='修复所有FBX材质',
                      c = lambda *args: all_convert_old_materials_to_arnold_button())

        cmds.menuItem(label='智能修复选择材质贴图',
                      c = lambda *args: select_intelligent_material_repair_button())

        # 修复所有FBX材质
        cmds.menuItem(label='智能修复全部材质贴图',
                      c = lambda *args: all_intelligent_material_repair_button())

        cmds.menuItem(divider=True, label='其他工具')

        cmds.menuItem(label='优化场景名称',
                      c=lambda *args: self.scene_name_optimization_instance())

        cmds.menuItem(divider=True,)

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
            c=lambda *args: run_magic_connection()
        )

        self.path_detection_connection = cmds.button(
            label=self.language['create_widgets']['path_detection_connection'],
            c=lambda *args: path_detection_connection_button()
        )
        cmds.text(label=" " * 2)
        self.intelligent_mix = cmds.button(
            label=self.language['create_widgets']['intelligent_mix'],
            c=lambda *args: intelligent_mix()
        )

        # self.mask_node_mix = cmds.button(
        #     label=self.language['create_widgets']['mask_node_mix'],
        #     c=lambda *args: mask_node_mix()
        # )

        # 快速连接按钮
        self.quick_connect = cmds.button(
            label="快速连接",
            c = lambda *args: quick_connect_node_button())


        # 直连按钮
        self.direct_connection = cmds.button(
            label=self.language['create_widgets']['direct_connection'],
            c=lambda *args: direct_connection_button())

        cmds.text(label=" " * 1)

        # 统一UV按钮
        self.unify_uv_node = cmds.button(
            label=self.language['create_widgets']['unify_uv_node'],
            c=lambda *args: unify_uv_node_button()
        )

        cmds.text(label=" " * 2)

        # UV预设选项菜单
        self.uv_preset = cmds.optionMenu(
            mvi=8,
            cc=lambda *args: uv_preset_menu(
                cmds.optionMenu(self.uv_preset, query=True, value=True)),
            h = 27
        )

        # 添加UV模式选项
        uv_mode_list = self.language['create_widgets']['uv_preset']
        for uv_mode_name in uv_mode_list:
            cmds.menuItem(label=uv_mode_name)

        # 色彩空间预设菜单
        self.color_space_preset = cmds.optionMenu(
            mvi=16,
            cc=lambda *args: color_space_preset_menu(
                cmds.optionMenu(self.color_space_preset, query=True, value=True)),
            h=27
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
            cc=lambda *args: rendering_preset_menu(
                cmds.optionMenu(self.rendering_preset, query=True, value=True)),
            h=27
        )

        # 获取并添加渲染预设文件名
        ensure_directory(render_preset_path)
        file_names = [
            file_name
            for file_name in os.listdir(render_preset_path)
            if file_name.lower().endswith(".json")
        ]
        file_names_without_json_list = [
            os.path.splitext(file_name)[0] for file_name in file_names
        ]

        for renderer_data_mode_name in file_names_without_json_list:
            self.rendering_preset_name[renderer_data_mode_name] = cmds.menuItem(label=renderer_data_mode_name)

        cmds.text(label=" " * 2)


    #______________________________________________________________________________>>> 初始化全局数据
    def initial_global_config(self):
        # 初始化数据管理器
        self.dataM = DataManager()
        self.feedback = FeedbackPrompt()  # 错误提示模块
        self.getnodedata = GetNodeData()  # 获取节点数据模块

        # 加载语言配置
        self.language = language_loading()['ArnoldMagicNode']['AMDUI_WIN']

        # 加载设置配置
        self.config = self.dataM.load_json(os.path.normpath(os.path.join(settings_path, AMS_Config)))

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
        config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )

        # 遍历键路径，访问到目标键的上一级
        current_level = config
        for key in key_path[:-1]:  # 遍历到倒数第二个键
            current_level = current_level[key]  # 进入下一层级

        # 设置目标键的值为新值
        current_level[key_path[-1]] = cont

        # 保存修改后的配置数据
        self.dataM.save_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config)),
            config
        )

        # 重新加载配置数据以更新当前实例的配置
        self.config = self.dataM.load_json(
            os.path.normpath(os.path.join(settings_path, AMS_Config))
        )

    # ______________________________________________________________________________>>> 实例化函数
    def scene_name_optimization_instance(self):
        SNO = SceneNameOptimization()
        SNO.main()
