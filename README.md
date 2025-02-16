# Arnold Magic Node Tool

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## 简介
在Maya的资产制作还有渲染中，会总因为PBR，BRDF等等的材质工作流程繁琐连接工作所消耗大量的时间。
Arnold_Magic_Node_Tools这个工具可以让你快速的去处理你的材质，并且可以批量的去制作材质球，
这个工具不仅可以处理节点，也会包含Arnold渲染器中其他的一些AOV等处理工具，让你在制作中无需花
太多的精力和时间去处理繁琐的工作！

## 目录
1. [插件主页](https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69&embed=true)
2. [反馈主页](https://flowus.cn/form/7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69)
3. [安装](https://flowus.cn/amazingike/share/9f52d05f-b9af-40dd-b167-bd21e6bf9ec3?code=LZVF69)
3. [使用方法](https://flowus.cn/amazingike/share/6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69)
5. [购买](https://flowus.cn/amazingike/share/dc7217e0-b244-48ab-b2fe-9fda45052fbf?code=LZVF69)

## 特性
- 功能 1
- 功能 2
- 功能 3

## 安装
**一些小问题**
1，在第一次安装**对应Maya版本的时候会安装对应Maya相应版本的库**，所以会**需要一点时间下载**（需要联网下载）。
2，安装完成在**工具架上会有对应的图标**。
3，**插件需要购买**，购买完成后需要**提供设备识别码给作者**，然后输入作者返回的序列号，输入序列号即可使用。
4，插件必须要**联网使用。**



## 支持版本

    注意：

        - 目前主要维护的两个版本是 Maya 2022 & Maya 2025

        - 不支持2022.3以下的子版本，如果是2022.0，需要更新到2022.5.1

        - 不支持py2的版本Maya

    MAYA 2022 （3.7.7）[已测试]

    MAYA 2023 （3.9.7）[已测试]

    MAYA 2024 （3.10.8）[已测试]

    MAYA 2025 （3.11.4）[已测试]



## 自动安装插件：

    **注意：**

        1，插件在第一次打开的时候是需要下载必要运行库的，当然可以手动安装，可以参考下面的**库的下载并安装**的内容

        2，插件不要放在中文路径，不然会无法下载运行库










把"Arnold_Magic_Node_Install.py"文件拖入到Maya中即可安装





## 手动安装插件：

    **注意：**

        1，输入的路径是你放这个脚本文件夹外的路径。不是脚本文件夹里面的路径

        2，非必要手动安装



```Python
import sys
import os

File_Path = r"D:\\Maya Script\\Maya_arnold_tool"   #  <需要修改>输入你脚本文件夹放置的路径

if not os.path.exists(File_Path):
    cmds.confirmDialog(message="检测到你的路径是错误的", button="确定", title="报错提醒，滴滴滴", )
else:
    sys.path.append(File_Path)
    import Arnold_Magic_Node_Start

Arnold_Magic_Node_Start.main()
```



## 手动必要运行库的下载并安装：

只需要下载解压在插件目录下即可，注意需要在这里下载对应**插件版本**的库进行安装

[库下载连接](https://flowus.cn/amazingike/share/f3d10a03-3c65-4413-831c-e5796cb5889a?code=LZVF69)




