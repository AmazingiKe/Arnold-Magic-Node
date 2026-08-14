"""面向 Maya 用户的统一提示工具。"""

from datetime import datetime

from arnold_magic_node.maya.nodes import MayaNodeAdapter
from .runtime import load_language


class FeedbackPrompt(object):
    """统一封装面向用户的打印与警告，并集中读取语言资源。"""

    def __init__(self, adapter=None):
        self.adapter = adapter
        self.language = load_language()["ArnoldMagicNodeLibs"]["FeedbackPrompt"]
        current_time = datetime.now()
        self.default_content = "{} {} | ".format(
            self.language["01"], current_time.strftime("%Y-%m-%d %H:%M:%S")
        )

    def print_message(self, content):
        print(self.default_content + str(content))

    def warn(self, content=None, error_context=None):
        if self.adapter is None:
            self.adapter = MayaNodeAdapter()

        if error_context is None:
            self.adapter.warning(str(self.default_content) + str(content))
        else:
            print(str(self.default_content) + self.language["02"] + str(content))
            print("↓" * 65)
            self.adapter.warning(str(error_context))


__all__ = ["FeedbackPrompt"]
