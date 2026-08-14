"""渲染预设名称输入窗口及其迁移期状态。"""

import os

import maya.cmds as cmds

from arnold_magic_node.tools.feedback import FeedbackPrompt
from arnold_magic_node.tools.rendering import RenderingCaptureTool
from arnold_magic_node.tools.runtime import get_runtime_paths, save_json
from arnold_magic_node._qt_compat import QCoreApplication


_runtime_paths = get_runtime_paths()


new_rendering_preset_name = {}

class RenderingPresetDialog:

    def __init__(self, menu_name, capture_tool=None):

        self.import_val = None

        self.import_name_win(menu_name)

        self.feedback = FeedbackPrompt()
        self.capture_tool = capture_tool or RenderingCaptureTool(
            feedback=self.feedback
        )



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

        return self.capture_tool.capture_node_groups({
            'defaultRenderGlobals': defaultRenderGlobals_options,
            'defaultRenderQuality': defaultRenderQuality_options,
            'defaultResolution': defaultResolution_options,
        })

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

        return self.capture_tool.capture_node_groups({
            'defaultArnoldDriver': defaultArnoldDriver,
            'defaultArnoldFilter': defaultArnoldFilter,
            'defaultArnoldRenderOptions': defaultArnoldRenderOptions,
        })

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

        return self.capture_tool.capture_aovs(
            aiAOV_att_list,
            aiDriver_att_list,
            aiFilter_att_list,
        )

    # 获取driver_and_filter的名字
    def get_driver_and_filter_nodes(self, node_name):
        """返回指定节点的 driver 与 filter 节点名。"""

        return self.capture_tool.driver_and_filter_nodes(node_name)

    # _______________________________________________________________________>>> 导入名称窗口函数
    def import_name_win(self, menu_name):
        """
        创建一个窗口用于输入预设名称，并将其添加到指定的菜单中。
        """
        win_name = "import_name_win"
        # 检查窗口是否存在，如果存在则删除
        if cmds.window(win_name, exists=True):
            cmds.deleteUI(win_name)

        # 创建窗口
        cmds.window(
            win_name,
            title=QCoreApplication.translate("RenderPresetDialog", "Enter your preset name"),
            sizeable=False,
            mbr=True,
            tlb=False,
            w=300,
            h=40,
        )

        # 创建布局
        layout = cmds.rowLayout(numberOfColumns=50)

        # 创建输入控件
        cmds.text(label=" " * 2)
        text_field = cmds.textField(w=300)

        # 创建按钮布局
        cmds.text(label=" " * 3)
        cmds.button(
            label=QCoreApplication.translate("RenderPresetDialog", "OK"),
            c=lambda *args: determine(),
        )
        cmds.text(label=" | ")
        cmds.button(
            label=QCoreApplication.translate("RenderPresetDialog", "Cancel"),
            c=lambda *args: cancellation(),
        )
        cmds.text(label=" " * 3)

        # 设置父级布局
        cmds.setParent(layout)

        # 显示窗口
        cmds.showWindow(win_name)

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
            aov_properties = self.get_AOV_properties()

            write_data_path = _runtime_paths.render_preset_path

            render_settings = {
                'default_rendering_properties': default_rendering_properties,
                'rendering_properties': rendering_properties,
                'AOV_properties': aov_properties
            }

            if not os.path.exists(os.path.join(write_data_path, self.import_val + ".json")):
                save_json(os.path.join(write_data_path, self.import_val + ".json"), render_settings)



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
            cmds.deleteUI(win_name)
            return

        # _______________________________________________________________________>>> 取消操作函数
        def cancellation():
            """
            取消按钮的回调函数，关闭窗口。
            """
            cmds.deleteUI(win_name)
            return

def delete_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name):
    global new_rendering_preset_name

    for i in rendering_preset_name:
        if sl_name == i:
            cmds.deleteUI(rendering_preset_name[i], menuItem=True)

    for i in new_rendering_preset_name:
        if sl_name == i:
            cmds.deleteUI(new_rendering_preset_name[i], menuItem=True)

    os.remove(os.path.normpath(os.path.join(
                _runtime_paths.render_preset_path,  sl_name+ '.json'
            )))

def modify_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name, menu_name):
    RenderingPresetDialog(menu_name)
    delete_rendering_preset_menuItem(rendering_preset_path, sl_name, rendering_preset_name)
