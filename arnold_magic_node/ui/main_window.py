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
    uv_preset_mode_map,
)
from .aov_light_group_dialog import show_aov_light_group_dialog
from .i18n import register_retranslate_callback
from arnold_magic_node._qt_compat import (
    QCoreApplication,
    QtCore,
    QtGui,
    QtWidgets,
    wrapInstance,
)
from .rendering_preset_dialog import (
    delete_rendering_preset_menuItem,
    modify_rendering_preset_menuItem,
    RenderingPresetDialog,
)
from .settings_dialog import SettingsDialog


_runtime_paths = get_runtime_paths()


class MainWindow(QtCore.QObject):
    def __init__(self):
        super(MainWindow, self).__init__()
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

        # Maya cmds 界面收不到 Qt LanguageChange，由翻译模块回调驱动重译
        register_retranslate_callback(self.retranslate_ui)

    def retranslate_ui(self):
        """语言切换后重设全部 Maya 原生界面文案。"""

        if not cmds.workspaceControl(self.window, exists=True):
            return

        cmds.menuItem(self.aov_manager_divider, edit=True, label=self.tr("AOV Manager"))
        cmds.menuItem(self.aov_light_group_manager_item, edit=True, label=self.tr("AOV Light Group Manager"))
        cmds.menuItem(self.render_preset_settings_divider, edit=True, label=self.tr("Render Preset Settings"))
        cmds.menuItem(self.add_render_preset_item, edit=True, label=self.tr("Add Render Preset"))
        cmds.menuItem(self.edit_render_preset_item, edit=True, label=self.tr("Edit Render Preset"))
        cmds.menuItem(self.delete_render_preset_item, edit=True, label=self.tr("Delete Render Preset"))
        cmds.menuItem(self.open_render_preset_folder_item, edit=True, label=self.tr("Open Render Preset Folder"))
        cmds.menuItem(self.render_preset_output_divider, edit=True, label=self.tr("Render Preset Output Settings"))
        cmds.menuItem(self.default_rendering_properties_options, edit=True, label=self.tr("Export Default Parameters"))
        cmds.menuItem(self.rendering_properties_options, edit=True, label=self.tr("Export Arnold Parameters"))
        cmds.menuItem(self.aov_properties_properties_options, edit=True, label=self.tr("Export AOV Parameters"))
        cmds.menuItem(self.material_repair_divider, edit=True, label=self.tr("Material Repair Tools"))
        cmds.menuItem(self.repair_selected_fbx_item, edit=True, label=self.tr("Repair Selected FBX Materials"))
        cmds.menuItem(self.repair_all_fbx_item, edit=True, label=self.tr("Repair All FBX Materials"))
        cmds.menuItem(self.intelligent_selected_item, edit=True, label=self.tr("Intelligently Repair Selected Material Textures"))
        cmds.menuItem(self.intelligent_all_item, edit=True, label=self.tr("Intelligently Repair All Material Textures"))
        cmds.menuItem(self.other_tools_divider, edit=True, label=self.tr("Other Tools"))
        cmds.menuItem(self.optimize_scene_names_item, edit=True, label=self.tr("Optimize Scene Names"))
        cmds.menuItem(self.settings_item, edit=True, label=self.tr("Settings"))

        cmds.button(self.magic_connection, edit=True, label=self.tr("Magic Connection"))
        cmds.button(self.path_detection_connection, edit=True, label=self.tr("Path Detection Connection"))
        cmds.button(self.intelligent_mix, edit=True, label=self.tr("Intelligent Blend"))
        cmds.button(self.quick_connect, edit=True, label=self.tr("Quick Connect"))
        cmds.button(self.direct_connection, edit=True, label=self.tr("Direct Connection"))
        cmds.button(self.unify_uv_node, edit=True, label=self.tr("Unify UV"))
        cmds.button(self.auto_color_space_button, edit=True, label=self.tr("Auto Color Space"))
        cmds.button(self.auto_udim_button, edit=True, label=self.tr("Auto UDIM"))
        cmds.button(self.ai_aov_switch, edit=True, label=self.tr("AOV Toggle"))

        for item, name in zip(self.uv_preset_items, uv_preset_mode_map()):
            cmds.menuItem(item, edit=True, label=name)

    def create_widgets(self):
        cmds.rowLayout(numberOfColumns=30)
        cmds.popupMenu(button=3)

        self.aov_manager_divider = cmds.menuItem(label=self.tr("AOV Manager"), divider=True)

        self.aov_light_group_manager_item = cmds.menuItem(
            label=self.tr("AOV Light Group Manager"),
            c=lambda *args: show_aov_light_group_dialog(),
            i=os.path.join(_runtime_paths.icon_path, "LightManagerShelf_200.png"),
        )

        self.render_preset_settings_divider = cmds.menuItem(
            label=self.tr("Render Preset Settings"),
            divider=True,
        )

        self.add_render_preset_item = cmds.menuItem(
            label=self.tr("Add Render Preset"),
            c=lambda *args: RenderingPresetDialog(self.rendering_preset),
        )

        self.edit_render_preset_item = cmds.menuItem(
            label=self.tr("Edit Render Preset"),
            c=lambda *args: modify_rendering_preset_menuItem(
                cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                cmds.optionMenu(self.rendering_preset, query=True, value=True),
                self.rendering_preset_name,
                self.rendering_preset,
            ),
        )

        self.delete_render_preset_item = cmds.menuItem(
            label=self.tr("Delete Render Preset"),
            c=lambda *args: delete_rendering_preset_menuItem(
                cmds.optionMenu(self.rendering_preset, query=True, fullPathName=True),
                cmds.optionMenu(self.rendering_preset, query=True, value=True),
                self.rendering_preset_name,
            ),
        )

        self.open_render_preset_folder_item = cmds.menuItem(
            label=self.tr("Open Render Preset Folder"),
            c=lambda *args: os.startfile(_runtime_paths.render_preset_path),
        )

        self.render_preset_output_divider = cmds.menuItem(divider=True, label=self.tr("Render Preset Output Settings"))

        self.default_rendering_properties_options = cmds.menuItem(
            label=self.tr("Export Default Parameters"),
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=["render_preset_params", "default_rendering_properties_write_options"],
                cont=cmds.menuItem(self.default_rendering_properties_options, query=True, checkBox=True),
            ),
        )

        self.rendering_properties_options = cmds.menuItem(
            label=self.tr("Export Arnold Parameters"),
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=["render_preset_params", "rendering_properties_write_options"],
                cont=cmds.menuItem(self.rendering_properties_options, query=True, checkBox=True),
            ),
        )

        self.aov_properties_properties_options = cmds.menuItem(
            label=self.tr("Export AOV Parameters"),
            cb=True,
            c=lambda *args: self.modify_nested_config(
                key_path=["render_preset_params", "AOV_properties_properties_write_options"],
                cont=cmds.menuItem(self.aov_properties_properties_options, query=True, checkBox=True),
            ),
        )

        cmds.menuItem(
            self.default_rendering_properties_options,
            edit=True,
            checkBox=self.config["render_preset_params"]["default_rendering_properties_write_options"],
        )
        cmds.menuItem(
            self.rendering_properties_options,
            edit=True,
            checkBox=self.config["render_preset_params"]["rendering_properties_write_options"],
        )
        cmds.menuItem(
            self.aov_properties_properties_options,
            edit=True,
            checkBox=self.config["render_preset_params"]["AOV_properties_properties_write_options"],
        )

        self.material_repair_divider = cmds.menuItem(divider=True, label=self.tr("Material Repair Tools"))

        self.repair_selected_fbx_item = cmds.menuItem(
            label=self.tr("Repair Selected FBX Materials"),
            c=lambda *args: MaterialConversionTool(select_all=False).run(),
        )

        self.repair_all_fbx_item = cmds.menuItem(
            label=self.tr("Repair All FBX Materials"),
            c=lambda *args: MaterialConversionTool(select_all=True).run(),
        )

        self.intelligent_selected_item = cmds.menuItem(
            label=self.tr("Intelligently Repair Selected Material Textures"),
            c=lambda *args: IntelligentMaterialRepairTool(select_all=False).run(),
        )

        self.intelligent_all_item = cmds.menuItem(
            label=self.tr("Intelligently Repair All Material Textures"),
            c=lambda *args: IntelligentMaterialRepairTool(select_all=True).run(),
        )

        self.other_tools_divider = cmds.menuItem(divider=True, label=self.tr("Other Tools"))

        self.optimize_scene_names_item = cmds.menuItem(
            label=self.tr("Optimize Scene Names"),
            c=lambda *args: self.scene_name_optimization_instance(),
        )

        cmds.menuItem(divider=True)

        self.settings_item = cmds.menuItem(
            label=self.tr("Settings"),
            c=lambda *args: SettingsDialog(),
        )

        cmds.text(label=" " * 1)

        self.magic_connection = cmds.button(
            label=self.tr("Magic Connection"),
            c=lambda *args: MagicConnectionTool().run(),
        )

        self.path_detection_connection = cmds.button(
            label=self.tr("Path Detection Connection"),
            c=lambda *args: PathDetectionConnectionTool().run(),
        )

        cmds.text(label=" " * 2)

        self.intelligent_mix = cmds.button(
            label=self.tr("Intelligent Blend"),
            c=lambda *args: NodeMixTool().run(),
        )

        self.quick_connect = cmds.button(
            label=self.tr("Quick Connect"),
            c=lambda *args: QuickConnectTool().run(),
        )

        self.direct_connection = cmds.button(
            label=self.tr("Direct Connection"),
            c=lambda *args: connect_directly(),
        )

        cmds.text(label=" " * 1)

        self.unify_uv_node = cmds.button(
            label=self.tr("Unify UV"),
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

        self.uv_preset_items = [
            cmds.menuItem(label=name) for name in uv_preset_mode_map()
        ]

        self.color_space_preset = cmds.optionMenu(
            mvi=16,
            cc=lambda *args: set_color_space_preset(
                cmds.optionMenu(self.color_space_preset, query=True, value=True)
            ),
            h=27,
        )

        for color_space_name in self.config["color_space_params"]["config"]:
            cmds.menuItem(label=color_space_name)

        self.auto_color_space_button = cmds.button(
            label=self.tr("Auto Color Space"),
            c=lambda *args: auto_set_texture_color_space(),
        )

        self.auto_udim_button = cmds.button(
            label=self.tr("Auto UDIM"),
            c=lambda *args: auto_set_file_node_udim(),
        )

        cmds.text(label=" " * 2)

        self.ai_aov_switch = cmds.button(
            label=self.tr("AOV Toggle"),
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
