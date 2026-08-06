"""Maya 贴图节点与图像尺寸适配器。"""

import os

from .nodes import MayaNodeAdapter


class MayaTextureAdapter(MayaNodeAdapter):
    def __init__(self, cmds_module=None, open_maya_module=None):
        super(MayaTextureAdapter, self).__init__(cmds_module)
        self._open_maya = open_maya_module

    def _open_maya_module(self):
        if self._open_maya is None:
            try:
                import maya.api.OpenMaya as open_maya
            except ImportError:
                raise RuntimeError("贴图尺寸读取只能在 Maya 中使用")
            self._open_maya = open_maya
        return self._open_maya

    def image_dimensions(self, file_path):
        try:
            open_maya = self._open_maya_module()
            image = open_maya.MImage()
            image.readFromFile(
                os.path.normpath(str(file_path)), open_maya.MImage.kUnknown
            )
            return tuple(image.getSize())
        except Exception:
            return (0, 0)

    def file_texture_path(self, node_name):
        return self.get_attr(node_name + ".fileTextureName")

    def set_udim(self, node_name, enabled):
        self.set_attr(node_name + ".uvTilingMode", 3 if enabled else 0)

    def set_color_space(self, node_name, color_space):
        self.set_attr(
            node_name + ".colorSpace", color_space, value_type="string"
        )
        self.set_attr(node_name + ".alphaIsLuminance", 1)
        self.set_attr(node_name + ".ignoreColorSpaceFileRules", 1)

    def create_file_texture(self, filename, directory):
        node_name = os.path.splitext(filename)[0]
        created = self.create_shading_node(
            "file", asTexture=True, name=node_name
        )
        file_path = os.path.normpath(os.path.join(str(directory), filename))
        self.set_attr(
            created + ".fileTextureName", file_path, value_type="string"
        )
        return created


__all__ = ["MayaTextureAdapter"]
