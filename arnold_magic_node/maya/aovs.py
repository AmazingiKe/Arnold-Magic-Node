"""Arnold AOV 宿主接口适配器。"""

from .nodes import MayaNodeAdapter


def _load_aov_factory():
    try:
        import mtoa.aovs as aovs
    except ImportError:
        raise RuntimeError("Arnold AOV 适配器只能在加载 mtoa 后使用")
    return aovs.AOVInterface


class MayaAovAdapter(MayaNodeAdapter):
    def __init__(self, cmds_module=None, interface_factory=None):
        super(MayaAovAdapter, self).__init__(cmds_module)
        self.interface_factory = interface_factory or _load_aov_factory()

    def create_aov(self, aov_name):
        return self.interface_factory().addAOV(aov_name)


__all__ = ["MayaAovAdapter"]
