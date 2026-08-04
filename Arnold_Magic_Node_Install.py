"""Arnold Magic Node shelf installer for Autodesk Maya."""

import os

import maya.cmds as cmds
import maya.mel


class Installer:
    """Install a launcher button on Maya's currently selected shelf."""

    def install(self):
        script_path = os.path.normpath(os.path.dirname(__file__))

        command = f'''import importlib
import os
import sys

import maya.cmds as cmds

file_path = r"{script_path}"

if not os.path.exists(file_path):
    cmds.confirmDialog(
        message="检测到插件路径错误",
        button="确定",
        title="Arnold Magic Node",
    )
else:
    if file_path not in sys.path:
        sys.path.insert(0, file_path)

    import Arnold_Magic_Node_Start

    importlib.reload(Arnold_Magic_Node_Start)
    Arnold_Magic_Node_Start.main()
'''

        shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
        parent = cmds.tabLayout(shelf, query=True, selectTab=True)
        button_name = "Arnold_Magic_Node"

        cmds.shelfButton(
            command=command,
            annotation=button_name,
            imageOverlayLabel=button_name,
            sourceType="Python",
            image=os.path.join(script_path, "icon", "Logo_B.svg"),
            parent=parent,
            label=button_name,
        )


installer = Installer()


def onMayaDroppedPythonFile(*args, **kwargs):
    """Install the shelf button when this file is dropped into Maya."""
    installer.install()
