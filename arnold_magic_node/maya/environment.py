"""Maya-specific environment paths.

Only this adapter knows how to ask Maya for the per-user application
directory. It intentionally does not create directories while being imported.
"""

from arnold_magic_node.core.paths import user_data_root


def _load_cmds():
    try:
        import maya.cmds as cmds
    except ImportError:
        raise RuntimeError("Maya 环境适配器只能在 Maya 中使用")
    return cmds


class MayaEnvironmentAdapter(object):
    def __init__(self, cmds_module=None):
        self.cmds = cmds_module or _load_cmds()

    def user_data_root(self):
        return user_data_root(self.cmds.internalVar(userAppDir=True))

    def ui_language(self):
        return self.cmds.about(uil=True)

    def modifiers(self):
        return self.cmds.getModifiers()


__all__ = ["MayaEnvironmentAdapter"]
