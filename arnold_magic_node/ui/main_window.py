"""Arnold Magic Node 的 Maya 主窗口界面。"""

import os

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from arnold_magic_node.tools.magic_connection import MagicConnectionTool
from arnold_magic_node.tools.materials import (
    IntelligentMaterialRepairTool,
    MaterialConversionTool,
)
from arnold_magic_node.tools.node_graph import (
    NodeMixTool,
    QuickConnectTool,
)
from arnold_magic_node.tools.path_detection import PathDetectionConnectionTool
from arnold_magic_node.tools.rendering import RenderingPresetTool, toggle_aovs
from arnold_magic_node.tools.runtime import (
    AMS_CONFIG,
    SOFTWARE_STATE,
    SOFTWARE_VERSION,
    ensure_directory,
    get_runtime_paths,
    load_json,
    load_language,
    save_json,
)
from arnold_magic_node.tools.scene import SceneNameOptimizationTool
from arnold_magic_node.tools.texture import (
    auto_set_file_node_udim,
    auto_set_texture_color_space,
    connect_directly,
    set_color_space_preset,
    set_uv_preset,
    unify_uv_nodes,
)
from .aov_light_group_dialog import show_aov_light_group_dialog
from ._qt_compat import QtGui, QtWidgets, wrapInstance
from .rendering_preset_dialog import (
    delete_rendering_preset_menuItem,
    modify_rendering_preset_menuItem,
    RenderingPresetDialog,
)
from .settings_dialog import SettingsDialog


_runtime_paths = get_runtime_paths()


class MainWindow(object):
    def __init__(self):
        win_title = f"Arnold Magic Node  {SOFTWARE_STATE} : {SOFTWARE_VERSION}"

        if cmds.window(win_title, exists=True):
            cmds.deleteUI(win_title)

        self.window = cmds.workspaceControl(
            win_title, retain=False, floating=True, w=300, h=300
        )

        ptr = omui.MQtUtil.findWindow(win_title)
        if ptr:
            qt_win = wrapInstance(int(ptr), QtWidgets.QWidget)
            qt_win.setWindowIcon(
                QtGui.QIcon(os.path.join(_runtime_paths.icon_path, "Logo_B.svg"))
            )

        self.initial_global_config()
        self.create_widgets()
        cmds.showWindow(self.window)

    def create_widgets(self):
        cmds.rowLayout(numberOfColumns=30)
        cmds.popupMenu(button=3)

        cmds.menuItem(label="AOV管理器", divider=True)

        cmds.menuItem(
            label="AOV灯光组管理器",
            c=lambda *args: show_aov_light_group_dialog(),
            i=os.path.join(_runtime_paths.icon_path, "LightManagerShelf_200.png"),
        )

        cmds.menuItem(
            label=self.language["create_widgets"]["render_preset_settings_menu"],
            divider=True,
        )

        cmds.menuItem(
            label=self.language["create_widgets"]["add_render_preset_menu"],
            c=lambda *args: RenderingPresetDialog(self.rendering_preset),
        )

        cmds.menuItem(
            label=self.language["create_widgets"]["edit_render_preset_menu"],
            c=lambda *args: modify_rendering_preset_menuItem(
                cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                cmds.optionMenu(self.rendering_preset, query=True, value=True),
                self.rendering_preset_name,
                self.rendering_preset,
            ),
        )

        cmds.menuItem(
            label=self.language["create_widgets"]["delete_render_preset_menu"],
            c=lambda *args: delete_rendering_preset_menuItem(
                cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                cmds.optionMenu(self.rendering_preset, query=True, value=True),
                self.rendering_preset_name,
            ),
        )

        cmds.menuItem(
            label=self.language["create_widgets"]["open_render_preset_folder_menu"],
            c=lambda *args: os.startfile(_runtime_paths.render_preset_path),
        )

        cmds.menuItem(divider=True, label="渲染预设输出设置")

        default_rendering_properties_options = cmds.menuItem(
            label=self.language["create_widgets"]["default_rendering_properties_options"],
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=["render_preset_params", "default_rendering_properties_write_options"],
                cont=cmds.menuItem(default_rendering_properties_options, query=True, checkBox=True),
            ),
        )

        rendering_properties_options = cmds.menuItem(
            label=self.language["create_widgets"]["rendering_properties_options"],
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=["render_preset_params", "rendering_properties_write_options"],
                cont=cmds.menuItem(rendering_properties_options, query=True, checkBox=True),
            ),
        )

        aov_properties_properties_options = cmds.menuItem(
            label=self.language["create_widgets"]["aov_properties_properties_options"],
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=["render_preset_params", "AOV_properties_properties_write_options"],
                cont=cmds.menuItem(aov_properties_properties_options, query=True, checkBox=True),
            ),
        )

        cmds.menuItem(
            default_rendering_properties_options,
            edit=True,
            checkBox=self.config["render_preset_params"]["default_rendering_properties_write_options"],
        )
        cmds.menuItem(
            rendering_properties_options,
            edit=True,
            checkBox=self.config["render_preset_params"]["rendering_properties_write_options"],
        )
        cmds.menuItem(
            aov_properties_properties_options,
            edit=True,
            checkBox=self.config["render_preset_params"]["AOV_properties_properties_write_options"],
        )

        cmds.menuItem(divider=True, label="材质修复工具")

        cmds.menuItem(
            label="修复选择的FBX材质",
            c=lambda *args: MaterialConversionTool(select_all=False).run(),
        )

        cmds.menuItem(
            label="修复所有FBX材质",
            c=lambda *args: MaterialConversionTool(select_all=True).run(),
        )

        cmds.menuItem(
            label="智能修复选择材质贴图",
            c=lambda *args: IntelligentMaterialRepairTool(select_all=False).run(),
        )

        cmds.menuItem(
            label="智能修复全部材质贴图",
            c=lambda *args: IntelligentMaterialRepairTool(select_all=True).run(),
        )

        cmds.menuItem(divider=True, label="其他工具")

        cmds.menuItem(
            label="优化场景名称",
            c=lambda *args: self.scene_name_optimization_instance(),
        )

        cmds.menuItem(divider=True)

        cmds.menuItem(
            label=self.language["create_widgets"]["settings_menu"],
            c=lambda *args: SettingsDialog(),
        )

        cmds.text(label=" " * 1)

        self.magic_connection = cmds.button(
            label=self.language["create_widgets"]["magic_connection"],
            c=lambda *args: MagicConnectionTool().run(),
        )

        self.path_detection_connection = cmds.button(
            label=self.language["create_widgets"]["path_detection_connection"],
            c=lambda *args: PathDetectionConnectionTool().run(),
        )

        cmds.text(label=" " * 2)

        self.intelligent_mix = cmds.button(
            label=self.language["create_widgets"]["intelligent_mix"],
            c=lambda *args: NodeMixTool().run(),
        )

        self.quick_connect = cmds.button(
            label="快速连接",
            c=lambda *args: QuickConnectTool().run(),
        )

        self.direct_connection = cmds.button(
            label=self.language["create_widgets"]["direct_connection"],
            c=lambda *args: connect_directly(),
        )

        cmds.text(label=" " * 1)

        self.unify_uv_node = cmds.button(
            label=self.language["create_widgets"]["unify_uv_node"],
            c=lambda *args: unify_uv_nodes(),
        )

        cmds.text(label=" " * 2)

        self.uv_preset = cmds.optionMenu(
            mvi=8,
            cc=lambda *args: set_uv_preset(
                cmds.optionMenu(self.uv_preset, query=True, value=True)
            ),
            h=27,
        )

        uv_mode_list = self.language["create_widgets"]["uv_preset"]
        for uv_mode_name in uv_mode_list:
            cmds.menuItem(label=uv_mode_name)

        self.color_space_preset = cmds.optionMenu(
            mvi=16,
            cc=lambda *args: set_color_space_preset(
                cmds.optionMenu(self.color_space_preset, query=True, value=True)
            ),
            h=27,
        )

        for color_space_name in self.config["color_space_params"]["config"]:
            cmds.menuItem(label=color_space_name)

        cmds.button(
            label=self.language["create_widgets"]["auto_color_space_button"],
            c=lambda *args: auto_set_texture_color_space(),
        )

        cmds.button(
            label=self.language["create_widgets"]["auto_udim_button"],
            c=lambda *args: auto_set_file_node_udim(),
        )

        cmds.text(label=" " * 2)

        self.ai_aov_switch = cmds.button(
            label=self.language["create_widgets"]["ai_aov_switch"],
            c=lambda *args: toggle_aovs(),
        )

        self.rendering_preset_name = {}
        self.rendering_preset = cmds.optionMenu(
            mvi=8,
            cc=lambda *args: RenderingPresetTool(
                cmds.optionMenu(self.rendering_preset, query=True, value=True)
            ).run(),
            h=27,
        )

        ensure_directory(_runtime_paths.render_preset_path)
        file_names = [
            file_name
            for file_name in os.listdir(_runtime_paths.render_preset_path)
            if file_name.lower().endswith(".json")
        ]
        for renderer_data_mode_name in file_names:
            preset_name = os.path.splitext(renderer_data_mode_name)[0]
            self.rendering_preset_name[preset_name] = cmds.menuItem(label=preset_name)

        cmds.text(label=" " * 2)

    def initial_global_config(self):
        self.language = load_language()["ArnoldMagicNode"]["AMDUI_WIN"]

        self.config = load_json(
            os.path.normpath(os.path.join(_runtime_paths.settings_path, AMS_CONFIG))
        )

    def modify_nested_config(self, key_path, cont):
        """按键路径修改配置并写回用户设置文件。"""

        config = load_json(
            os.path.normpath(os.path.join(_runtime_paths.settings_path, AMS_CONFIG))
        )

        current_level = config
        for key in key_path[:-1]:
            current_level = current_level[key]

        current_level[key_path[-1]] = cont

        save_json(
            os.path.normpath(os.path.join(_runtime_paths.settings_path, AMS_CONFIG)),
            config,
        )

        self.config = load_json(
            os.path.normpath(os.path.join(_runtime_paths.settings_path, AMS_CONFIG))
        )

    def scene_name_optimization_instance(self):
        SceneNameOptimizationTool().run()
