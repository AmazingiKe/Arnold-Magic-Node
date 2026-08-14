"""面向 Maya 用户的统一提示工具。"""

from datetime import datetime

from arnold_magic_node.maya.nodes import MayaNodeAdapter
from arnold_magic_node._qt_compat import QCoreApplication


class FeedbackPrompt(object):
    """统一封装面向用户的打印与警告，文案按当前语言即时翻译。"""

    def __init__(self, adapter=None):
        self.adapter = adapter
        current_time = datetime.now()
        self.default_content = "{} {} | ".format(
            QCoreApplication.translate("FeedbackPrompt", "@Arnold Tool Plugin Alert"),
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def print_message(self, content):
        print(self.default_content + str(content))

    def warn(self, content=None, error_context=None):
        if self.adapter is None:
            self.adapter = MayaNodeAdapter()

        if error_context is None:
            self.adapter.warning(str(self.default_content) + str(content))
        else:
            print(
                str(self.default_content)
                + QCoreApplication.translate("FeedbackPrompt", "Warning – see error below")
                + str(content)
            )
            print("↓" * 65)
            self.adapter.warning(str(error_context))


__all__ = ["FeedbackPrompt"]
