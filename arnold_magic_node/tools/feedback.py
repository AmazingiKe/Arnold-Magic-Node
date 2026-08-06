"""面向 Maya 用户的统一提示工具。"""

from datetime import datetime

from .runtime import load_language


class FeedbackPrompt(object):
    """保留旧反馈接口，并将语言读取收敛到运行时工具。"""

    def __init__(self):
        self.language = load_language()["ArnoldMagicNodeLibs"]["FeedbackPrompt"]
        current_time = datetime.now()
        self.primary_contact = "\nmail:1925250542@qq.com\nWeChat:13549971630"
        self.DefContent = "{} {} | ".format(
            self.language["01"], current_time.strftime("%Y-%m-%d %H:%M:%S")
        )

    def CP(self, content):
        print(self.DefContent + str(content))

    def CPW(self, content=None, EC=None):
        import maya.cmds as cmds

        if EC is None:
            cmds.warning(str(self.DefContent) + str(content))
        else:
            print(str(self.DefContent) + self.language["02"] + str(content))
            print("↓" * 65)
            cmds.warning(str(EC))

    def CPE(self, content=None, EC=None):
        error_message = "{}{}: {}".format(
            self.DefContent, self.language["03"], self.primary_contact
        )
        if EC:
            error_message += "\n" + str(EC)
        if content:
            error_message += "\n" + str(content)
        raise ValueError(error_message)


__all__ = ["FeedbackPrompt"]
