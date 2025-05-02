# ______________________________________________________________________________>>> 导入必要库
import os # 操作系统文件路径相关操作
import msgpack # 高效二进制序列化工具




# ______________________________________________________________________________>>> 配置项定义
Arnold_Magic_Settings = {
    # 纹理过滤参数配置
    "texture_filter_params": {
        'base': ['BASE_MASK'],  # 基础遮罩纹理的别名
        'baseColor': ["ALBEDO", "BASE_COLOR", "BASECOLOR", "DIFFUSE"],  # 基础颜色纹理的别名
        'diffuseRoughness': ['DIFFUSEROUGHNESS'],  # 漫反射粗糙度纹理的别名
        'metalness': ["METALNESS", "METALLIC", "METALIC", "METAL", "DIFFUSE"],  # 金属度纹理的别名
        'specular': ["SPECULAR", "SPEC"],  # 镜面反射纹理的别名
        'specularColor': ["SPECULARCOLOR"],  # 镜面反射颜色纹理的别名
        'specularRoughness': ["ROUGHNESS", "ROUGH", "REFL"],  # 镜面反射粗糙度纹理的别名
        'specularAnisotropy': ["SPECULARANISOTROPY"],  # 镜面反射各向异性纹理的别名
        'specularRotation': ["SPECULARROTATION"],  # 镜面反射旋转纹理的别名
        'subsurface': ['SUBSURFACE', 'SSS'],  # 次表面散射纹理的别名
        'subsurfaceColor': ["TRANSLUCENCY", "SUBSURFACECOLOR"],  # 次表面散射颜色纹理的别名
        'subsurfaceRadius': ["SUBSURFACERADIUS", "SUBSURFACE-RADIUS", "SUBSURFACE-RAD"],  # 次表面散射半径纹理的别名
        'emission': ["EMISSION", "ILLUMINATION", "GLOW", "SELF_ILLUMINATION"],  # 发射纹理的别名
        'emissionColor': ["EMISSIONCOLOR", "GLOW_COLOR"],  # 发射颜色纹理的别名
        'opacity': ["ALPHA", "ALPHAMASKED", "MASK", "OPACITY", "TRANSPARENCY", "ALPHA_MASK"],  # 不透明度纹理的别名
        'normalCamera': ["NORMAL", "NORMALMAP", "NRM",  "NORMALMAP_BUMP"],  # 法线纹理的别名
        "ao": ["AO", "AMBIENT_OCCLUSION", "OCC", "AMBIENT", "OCCLUSION"],  # 环境遮蔽纹理的别名
        "bump": ["BUMP", "BMP"],  # 凹凸纹理的别名
        "displacement": ["HEIGHT", "DISPLACEMENT", "DISP", "DEPTH", "HEIGHTMAP"]  # 位移纹理的别名
    },

    # 颜色空间参数配置
    "color_space_params": {
        "config": [
            'sRGB', 'Gamma 2.2 / Rec.709', 'Rec.1886 / Rec.709 video', 'AdobeRGB',
            'PCI-P3 D65', 'ACEScg', 'ACES2065-1', 'scene-linear Rec.709-sRGB',
            'scene-linear DCI-P3 D65', 'scene-linear Rec.2020', 'Raw', 'ACEScct',
            'Utility - Raw', 'Utility - linear - sRGB', 'Utility - sRGB - Texture'
        ],  # 支持的颜色空间配置列表
        "params": {
            'base': 'Raw',  # 基础纹理使用原始颜色空间
            'baseColor': 'sRGB',  # 基础颜色纹理使用 sRGB 颜色空间
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
            "ao": 'Raw',
            "bump": 'Raw',
            "displacement": 'Raw'
        }  # 各纹理参数对应的颜色空间
    },

    # 魔法连接配置
    "magic_conn_config": {
        "conn_params": {
            'base': False,  # 不自动连接基础纹理
            'baseColor': True,  # 自动连接基础颜色纹理
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
            "ao": True,
            "bump": False,
            "displacement": False
        },  # 各纹理参数是否自动连接
        'set_color_space': True,  # 是否设置颜色空间
        'set_material_name': True,  # 是否设置材质名称
        'set_udim': True  # 是否设置 UDIM
    },

    # 连接处理节点参数
    "proc_node_config": {
        "conn_params": {
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
            'opacity': False,
            'normalCamera': False,
            "ao": False,
            "bump": False,
            "displacement": True
        }, # 自动处理节点连接参数
        "params": {
            'base': {
                "NodeList": ["aiRampRgb", "aiRange"],  # 处理基础纹理的节点列表
                "InputPort": "input",  # 输入端口名称
                "OutputPort": "outColorR"  # 输出端口名称
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
            "ao": {
                "NodeList": ["aiRampRgb", "aiRange"],
                "InputPort": "input",
                "OutputPort": "outColorR"
            },
            "bump": {
                "NodeList": ["aiRampRgb", "aiRange"],
                "InputPort": "input",
                "OutputPort": "outColorR"
            },
            "displacement": {
                "NodeList": ["aiRampRgb", "aiRange"],
                "InputPort": "input",
                "OutputPort": "outColorR"
            }
        },  # 各纹理参数对应的处理节点配置
        "first_node_input": ["input", "passthrough"],  # 第一个节点的输入选项
        "last_node_output": [
            "outColor", "outAlpha", "outValue", "outTransparency",
            "outColorR", "outColorG", "outColorB"
        ]  # 最后一个节点的输出选项
    },

    # 路径检测参数配置
    "path_detection_params": {
        'exclude': ['.tx', '_PREVIEW', '_preview', 'LOD1', 'LOD2', 'LOD3', 'LOD4', 'LOD5', 'LOD6', 'LOD7', 'LOD8',
                    'LOD9', 'LOD10'],  # 排除的文件后缀和名称
        'detection_excluded': ['Texture', 'sRGB', 'Raw'],  # 排除的检测类别
        'similarity_range': 0.1,  # 相似度范围
        'similarity_max': 1,  # 相似度最大值
        'name_weight': 0.55,  # 名称权重
        'resolution_weight': 0.15,  # 分辨率权重
        'format_weight': 0.05,  # 格式权重
        'creation_time_weight': 0.15,  # 创建时间权重
        'creation_day_range_tolerance': 30,  # 创建日期范围容忍度（天）
        'auto_max_val': True,  # 是否自动设置最大值
        'disable_feedback': False,  # 是否禁用反馈
        'set_material_name': True,  # 是否设置材质名称
        'set_color_space': True,  # 是否设置颜色空间
        'set_udim': True  # 是否设置 UDIM
    },

    # 渲染预设参数配置
    "render_preset_params": {
        'default_rendering_properties_write_options': True,  # 是否写入默认渲染属性选项
        'rendering_properties_write_options': True,  # 是否写入渲染属性选项
        'AOV_properties_properties_write_options': True  # 是否写入 AOV 属性选项
    },

    # 快速连接混合器节点参数配置
    "node_connection_mixer_config" : {
        "quick_connect_node_parms" : {
            # 输出的端口
            "out_port" : ['outColor', 'outValue', 'outAlpha', 'outColorR',
                                'outColorG', 'outColorB', 'outTransparency', ],
            # 输入的端口
            "input_port" : ['input', 'input1' , 'inputR', 'inputG', 'inputB', 'inputA',
                                     'scale','slidemap', 'density', 'beauty', 'x', 'y', 'z' ,'A', 'B',
                                    'C', 'bumpMap', 'temperature',  'surfaceShader'],
            # 优先级组合
            "priority_order" : {'outColor': 'input' , 'outColor': 'input1'}
        }
    },
    # 优化场景节点名称参数配置
    "optimized_scene_node_name": {

        "replace_param": [
            {
                "case_sensitive": False,
                "switch_checkbox" : True,
                "target_cont": "prefix_",
                "replace_cont": ""
            },
            {
                "case_sensitive": False,
                "switch_checkbox" : True,
                "target_cont": "pasted__",
                "replace_cont": ""
            }
        ]
    },

    # 通用配置
    "general_config": {
        'GrayScaleTextures': [
            "base", 'diffuseRoughness', 'metalness', 'specularRoughness',
            'subsurface', 'emission', 'ao', 'bump', 'displacement'
        ],  # 灰度纹理列表
        'ColorTextures': [
            'baseColor', 'specularColor', 'subsurfaceColor', 'subsurfaceRadius',
            'emissionColor', 'opacity', 'normalCamera'
        ],  # 颜色纹理列表
    },
}

# 当前脚本路径
script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))

# ______________________________________________________________________________>>> 数据保存函数
def bin_save_data(file_path, data):
    """
    保存数据为二进制格式。

    :param file_path: 文件保存路径
    :param data: 要保存的数据
    """
    with open(file_path, 'wb') as file:
        packed_data = msgpack.packb(data)
        file.write(packed_data)

# ______________________________________________________________________________>>> 配置文件检测函数
def detecting_initial_config_files(path, filename, data):
    """
    检查并初始化配置文件。

    :param path: 配置文件存放路径
    :param filename: 配置文件名称
    :param data: 配置文件数据
    """
    abs_path = os.path.join(path, filename + '.bin')

    if not os.path.exists(abs_path) or os.path.getsize(abs_path) == 0:
        bin_save_data(abs_path, data)

# ______________________________________________________________________________>>> 主程序入口
def Main_program():
    """
    主程序，负责初始化配置文件。
    """
    settings_data = os.path.join(script_path, 'Datas', 'settings')
    detecting_initial_config_files(settings_data, 'Arnold_Magic_Settings', Arnold_Magic_Settings)