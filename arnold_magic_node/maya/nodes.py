"""可注入的 Maya 节点命令适配器。"""


def _load_cmds():
    try:
        import maya.cmds as cmds
    except ImportError:
        raise RuntimeError("Maya 节点适配器只能在 Maya 中使用")
    return cmds


class MayaNodeAdapter(object):
    """封装 tools 所需的通用 ``maya.cmds`` 节点操作。"""

    def __init__(self, cmds_module=None):
        self.cmds = cmds_module or _load_cmds()

    def list_nodes(self, *args, **kwargs):
        return self.cmds.ls(*args, **kwargs) or []

    def node_type(self, node_name):
        return self.cmds.nodeType(node_name)

    def list_connections(self, item, **kwargs):
        return self.cmds.listConnections(item, **kwargs) or []

    def list_relatives(self, node_name, **kwargs):
        return self.cmds.listRelatives(node_name, **kwargs) or []

    def attribute_exists(self, node_name, attribute):
        return bool(
            self.cmds.attributeQuery(attribute, node=node_name, exists=True)
        )

    def object_exists(self, item):
        return bool(self.cmds.objExists(item))

    def get_attr(self, attribute):
        return self.cmds.getAttr(attribute)

    def set_attr(self, attribute, *values, **kwargs):
        value_type = kwargs.pop("value_type", None)
        if value_type is not None:
            kwargs["type"] = value_type
        return self.cmds.setAttr(attribute, *values, **kwargs)

    def create_node(self, node_type, **kwargs):
        return self.cmds.createNode(node_type, **kwargs)

    def create_shading_node(self, node_type, **kwargs):
        return self.cmds.shadingNode(node_type, **kwargs)

    def connect_attr(self, source, target, force=True):
        return self.cmds.connectAttr(source, target, force=force)

    def delete(self, *nodes):
        return self.cmds.delete(*nodes)

    def rename(self, old_name, new_name):
        return self.cmds.rename(old_name, new_name)

    def warning(self, message):
        return self.cmds.warning(message)

    def modifiers(self):
        return self.cmds.getModifiers()


__all__ = ["MayaNodeAdapter"]
