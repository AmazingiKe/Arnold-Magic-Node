###########################
#                           
#   2024年9月19日修改安装器
#   
#
#
###########################

import os, sys, maya.mel, json
import maya.cmds as cmds



def onMayaDroppedPythonFile(*args, **kwargs):
    pass

# 安装到工具架函数
def INSTALL():
    Script_path = os.path.join(os.path.dirname(__file__)).replace('/', '\\').replace("\\", "\\\\")

    command = f'''import sys
import importlib
import os

File_Path = r"{Script_path}" # 输入你脚本的路径

if not os.path.exists(File_Path):
    cmds.confirmDialog(message="检测到你的路径是错误的", button="确定", title="报错提醒，滴滴滴", )
else:
    sys.path.append(File_Path)
    import Arnold_Magic_Node_Start

importlib.reload(Arnold_Magic_Node_Start)
Arnold_Magic_Node_Start.main()
'''

    # 获取当前选定的工具架
    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)

    button_name = 'Arnold_Magic_Node'


    # 将按钮添加到选定的工具架中
    cmds.shelfButton(
        command = command,
        annotation = button_name,
        imageOverlayLabel = button_name,  # 设置按钮的图标
        sourceType = 'Python',
        image ='alignSurface.png',
        parent = parent,
        label = button_name,
    )



INSTALL()
