import os
import msgpack





new_texture_processing_data_dict = {
    "TexFirstFilter": {
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
        'normalCamera': ["NORMAL","NORMALMAP","NRM"],
        "ao": ["AO", "AMBIENT_OCCLUSION", "OCC", "AMBIENT", "OCCLUSION"],
        "bump": ["BUMP", "BMP"],
        "displacement": ["HEIGHT","DISPLACEMENT", "DISP", "DEPTH", "HEIGHTMAP"]
        },
    "ColorSpace": {
        "ColorSpaceData": ['sRGB', 'Gamma 2.2 / Rec.709', 'Rec.1886 / Rec.709 video', 'AdobeRGB',
                            'PCI-P3 D65', 'ACEScg', 'ACES2065-1', 'scene-linear Rec.709-sRGB',
                            'scene-linear DCI-P3 D65', 'scene-linear Rec.2020', 'Raw', 'ACEScct',
                            'Utility-Raw', 'Utility - linear - sRGB', 'Utility - sRGB - Texture'],
        "AutoSetColorSpaceConfig":{
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
            "ao": 'Raw',
            "bump": 'Raw',
            "displacement": 'Raw'
        }},

    "ProcSet_Options":{
        'Magic_Connection_Options': {
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
            "ao": True,
            "bump": False,
            "displacement": False
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
            "ao": False,
            "bump": False,
            "displacement": True
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
    },
        'InputPortList': ["input", "passthrough"],
        'OutputPortList': ["outColor", "outAlpha", "outValue", "outTransparency", "outColorR", "outColorG", "outColorB"],
        'GraysList' : ["base", 'diffuseRoughness', 'metalness', 'specularRoughness', 'subsurface', 'emission', 'ao', 'bump', 'displacement'],
        'ColorList' : ['baseColor', 'specularColor', 'subsurfaceColor', 'subsurfaceRadius', 'emissionColor', 'opacity', 'normalCamera'],
        'MagicConnectionSetColorSpace' : True,
    },
}

path_detection_config_dict =  {
    'PathDetectionConnectionSetColorSpace': True,
    'exclude_list': ['.tx', '_PREVIEW', '_preview', 'LOD1', 'LOD2', 'LOD3', 'LOD4', 'LOD5', 'LOD6', 'LOD7', 'LOD8',
                     'LOD9', 'LOD10'],
    'format_list': ['jpg', 'png', 'tiff', 'exr', 'tif', 'ex', "psd", "raw"],
    'similarity_range': 0.1,
    'similarity_max': 1,
    'length_weight': 0.3,
    'auto_max_val': True,
    'near_one_value': False,
    'case_sensitive': True
}


render_preset_config_dict = {
    'default_rendering_properties_write_options' : True,
    'rendering_properties_write_options' : True,
    'AOV_properties_properties_write_options' : True
                                }

Script_path = os.path.join(os.path.dirname(__file__))

# 保存数据为二进制格式
def bin_save_data(file_path, data):
    with open(file_path, 'wb') as file:  # 'wb' 表示写入二进制文件
        packed_data = msgpack.packb(data)  # 将数据序列化为 MessagePack 格式
        file.write(packed_data)

def detecting_initial_config_files(path, filename, data):

    # 使用path和filename创建绝对路径
    abs_path = os.path.join(path, filename+'.bin')

    # 检查文件是否存在，或者文件大小是否为0KB
    if not os.path.exists(abs_path) or os.path.getsize(abs_path) == 0:
        # 如果文件不存在或者文件大小为0KB，重新保存数据
        bin_save_data(abs_path, data)


def Main_program():
    settings_data = os.path.join(Script_path, 'Datas', 'settings')

    # 检测texture_processing_data_dict配置是否存在，不存在将会创建一个
    detecting_initial_config_files(settings_data, 'texture_processing_data', new_texture_processing_data_dict)

    # 检测render_preset_config_dict配置是否存在，不存在将会创建一个
    detecting_initial_config_files(settings_data, 'render_preset_config', render_preset_config_dict)

    # 检测path_detection_config_dict配置是否存在，不存在将会创建一个
    detecting_initial_config_files(settings_data, 'path_detection_config', path_detection_config_dict)