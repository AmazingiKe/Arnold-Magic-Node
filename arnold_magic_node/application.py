##############################################################################################
# # ++ 导入所需的库和模块

# 1. Maya 库
import maya.cmds as cmds  # 导入 Maya 的 cmds 模块，用于执行 Maya 命令和操作场景

# 2. 文件与系统操作
import os  # 提供与操作系统交互的功能，如文件路径操作、目录遍历等
import importlib  # 用于动态导入和重新加载模块，支持模块的按需加载
from .core.paths import (
    ICONS_ROOT,
    LANGUAGES_ROOT,
    PROJECT_ROOT,
    user_aov_cache_path,
    user_preset_dir,
    user_settings_dir,
)
from .maya.environment import get_user_data_root
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

user_data_root = get_user_data_root()
datas_path = os.path.normpath(str(user_data_root))  # 兼容旧模块变量名，实际指向 Maya 用户目录

settings_path = os.path.normpath(str(user_settings_dir(user_data_root)))  # 用户设置目录

icon_path = os.path.normpath(str(ICONS_ROOT))  # 定义图标路径 -> 全局变量

render_preset_path = os.path.normpath(str(user_preset_dir(user_data_root, "render")))  # 渲染预设目录
settings_presets_path = os.path.normpath(str(user_preset_dir(user_data_root, "settings")))  # 设置预设目录
aov_cache_path = os.path.normpath(str(user_aov_cache_path(user_data_root)))  # AOV 单文件缓存

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

def language_loading():
    dataM = DataManager()

    # 加载语言配置文件并获取 'language_config' 键的值
    language_config = dataM.load_json(
        os.path.join(settings_path, 'language_config.json'))['language_config']

    # 动态加载相应语言的JSON文件
    language = dataM.load_json(
        os.path.join(str(LANGUAGES_ROOT), f'{language_config}.json'))

    return language


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
                os.path.join(render_preset_path, menu_sl_val + '.json')
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
    # Python 的 reload 不会清理已经从源码中移除的旧名称。
    for legacy_ui_name in (
        "MainWindow",
        "get_maya_main_window",
        "ArnoldMagicNodeSettingsPanel",
        "block_updates_and_signals",
        "AOVLightGroupTreeWidget",
        "AOVLightGroupManager",
        "delete_window_if_existe",
        "AOVLightGroupManagerInstance",
        "TextureBatchImporterWin",
        "new_rendering_preset_name",
        "rendering_preset_settings_button",
        "delete_rendering_preset_menuItem",
        "modify_rendering_preset_menuItem",
        "omui",
        "aovs",
        "shutil",
        "QtCore",
        "QtWidgets",
        "QtGui",
        "QAction",
        "wrapInstance",
        "contextmanager",
        "default_config",
        "ensure_directory",
    ):
        globals().pop(legacy_ui_name, None)

    from .ui import (
        qt,
        workspace,
        settings_dialog,
        aov_dialog,
        rendering_preset_dialog,
        main_window,
    )

    workspace.delete_window_if_existe("ArnoldMagicNodeSettingsPanel")
    workspace.delete_window_if_existe("AOVLightGroupManager")
    if cmds.window("import_name_win", exists=True):
        cmds.deleteUI("import_name_win")

    importlib.reload(qt)
    importlib.reload(workspace)
    importlib.reload(settings_dialog)
    importlib.reload(aov_dialog)
    importlib.reload(rendering_preset_dialog)
    importlib.reload(main_window)
    window_instance = main_window.MainWindow()
