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
3. [安装](#安装)
3. [使用方法](#使用方法)
4. [贡献](#贡献)
5. [许可证](#许可证)

## 特性
- 功能 1
- 功能 2
- 功能 3

## 安装
[插件安装](https://flowus.cn/amazingike/share/9f52d05f-b9af-40dd-b167-bd21e6bf9ec3?code=LZVF69)
**一些小问题**
1，在第一次安装**对应Maya版本的时候会安装对应Maya相应版本的库**，所以会**需要一点时间下载**（需要联网下载）。
2，安装完成在**工具架上会有对应的图标**。
3，**插件需要购买**，购买完成后需要**提供设备识别码给作者**，然后输入作者返回的序列号，输入序列号即可使用。
4，插件必须要**联网使用。**



### 支持版本

    - 目前主要维护的两个版本式Maya 2024和Maya 2025

    MAYA 2022 （3.7.7）

    MAYA 2023 （3.9.7）

    MAYA 2024 （3.10.8）

    MAYA 2025 （3.11.4）



### 自动安装：




把"Arnold_Magic_Node_Install.py"文件拖入到Maya中即可安装

### 手动安装：

- 注意！输入的路径是你放这个脚本文件夹外的路径。不是脚本文件夹里面的路径

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

