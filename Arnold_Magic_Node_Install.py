###########################
#
#   Arnold_Magic_Node_安装器
#   Arnold_Magic_Node_Plugin Installer
#
#   2024年12月12日修改安装器
#   Modified installer on December 12, 2024
#
###########################

# ______________________________________________________________________________>>> 导入必要库
import os  # 文件路径和操作相关
import maya.mel  # Maya MEL脚本接口
import maya.cmds as cmds  # Maya命令接口


# ______________________________________________________________________________>>> 定义事件处理函数（占位符）
def onMayaDroppedPythonFile(*args, **kwargs):
    pass


# ______________________________________________________________________________>>> 安装到工具架函数
def INSTALL():
    """
    将自定义工具安装到 Maya 的工具架中
    """
    # 获取当前脚本路径
    script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))

    # 需要执行的 Python 脚本命令
    command = f'''import sys
import importlib
import os

File_Path = r"{script_path}"

if not os.path.exists(File_Path):
    cmds.confirmDialog(message="检测到你的路径是错误的", button="确定", title="报错提醒，滴滴滴")
else:
    sys.path.append(File_Path)
    import Arnold_Magic_Node_Start

    importlib.reload(Arnold_Magic_Node_Start)
    Arnold_Magic_Node_Start.main()
'''

    # 获取当前选中的工具架
    shelf = maya.mel.eval('$gShelfTopLevel=$gShelfTopLevel')  # 全局工具架顶层变量
    parent = maya.cmds.tabLayout(shelf, query=True, selectTab=True)  # 查询当前活动的工具架

    # 定义按钮名称
    button_name = 'Arnold_Magic_Node'

    # 将按钮添加到当前工具架中
    cmds.shelfButton(
        command=command,  # 按钮触发的脚本命令
        annotation=button_name,  # 提示文字
        imageOverlayLabel=button_name,  # 按钮图标上的文字
        sourceType='Python',  # 脚本类型
        image='alignSurface.png',  # 按钮图标
        parent=parent,  # 工具架
        label=button_name  # 按钮标签
    )


# ______________________________________________________________________________>>> 执行安装函数
INSTALL()
