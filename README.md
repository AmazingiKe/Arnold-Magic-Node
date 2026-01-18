# Arnold Magic Node Tool

![Maya Version](https://img.shields.io/badge/Maya-2022%20|%202023%20|%202024%20|%202025-orange)
![Arnold Version](https://img.shields.io/badge/Arnold-5.0+-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.7+-blue)

## 🌟 项目亮点

### 核心优势

- **🎯 智能贴图匹配引擎**：基于多维度相似度算法（文件名、分辨率、格式、创建时间），自动识别并匹配贴图到正确的材质通道
- **⚡ 一键式PBR工作流**：自动构建符合行业标准的材质网络，支持金属/非金属工作流
- **🔧 强大的贴图管理器**：可视化界面批量管理场景中的所有贴图，实时显示状态、大小、分辨率等信息
- **🤖 智能UDIM检测**：自动识别UDIM格式贴图并正确设置UV平铺模式
- **🎨 自动色彩空间管理**：根据贴图类型智能设置色彩空间，确保渲染准确性
- **📦 批量图像处理**：支持批量转换格式、缩放贴图，多种重采样算法可选
- **🌍 多语言支持**：内置中英文双语界面，可扩展更多语言
- **🔗 灵活的节点连接**：自动创建处理节点（aiMultiply、aiNormalMap等），智能连接材质通道
- **💾 渲染预设系统**：保存、加载、管理渲染设置，快速切换不同渲染配置
- **🔄 路径智能修复**：批量修复缺失的贴图路径，支持子文件夹搜索和智能匹配

### 技术特色

- **高性能算法**：使用Aho-Corasick自动机进行高效的多模式匹配
- **模糊匹配技术**：集成Levenshtein距离算法，支持拼写容错
- **模块化架构**：清晰的代码结构，易于扩展和维护
- **跨版本兼容**：全面支持Maya 2022至2025最新版本

## 📦 快速安装

### 自动安装（推荐）

```python
# 将下方脚本拖入Maya视窗即可启动安装向导
from arnold_magic import installer
installer.auto_setup()
```

### 手动安装

1. 下载[最新发行包](https://example.com/download)
2. 解压到Maya模块目录：
   - **Windows**: `C:\Users\<用户>\Documents\maya\modules`
   - **macOS**: `~/Library/Preferences/Autodesk/maya/modules`
3. 创建模块描述文件 `arnoldMagic.mod`：

```
+ ArnoldMagic 1.0 <模块路径>
PATH += <模块路径>/bin
PYTHONPATH += <模块路径>/scripts
```

## 🛠️ 核心功能

### 1. 贴图管理器（Texture Manager）

**功能强大的贴图管理工具，让场景资产管理变得前所未有的简单**

- **📊 可视化管理界面**
  - 表格化展示所有贴图节点信息：节点名称、材质球、文件大小、像素分辨率、格式、引用次数、加载状态、完整路径
  - 支持搜索过滤材质球和贴图节点
  - 全选/取消全选/反选操作
  - 一键筛选缺失贴图、大尺寸贴图

- **🔍 智能路径修复**
  - 自动搜索并修复缺失的贴图路径
  - 支持子文件夹递归搜索
  - 智能匹配算法，基于文件名、分辨率、格式、创建时间多维度匹配
  - 支持缓存机制，提升搜索效率

- **🖼️ 批量图像处理**
  - 格式转换：支持JPG、PNG等主流格式互转
  - 贴图缩放：按百分比调整分辨率
  - 多种重采样算法：最近邻、双线性、三次插值、Lanczos等
  - 可配置JPG质量、PNG压缩等级
  - 自动备份原图，安全可靠

- **📦 贴图打包工具**
  - 一键打包场景中使用的所有贴图
  - 自动修改节点路径指向新位置
  - 可选删除源文件或复制TX文件
  - 支持选择性打包（全部/表格内/选中项）

### 2. 魔法连接系统（Magic Connection）

**革命性的自动连接系统，让材质搭建变得轻松高效**

- **🎯 智能贴图识别**
  - 基于关键词库自动识别贴图类型（baseColor、normal、roughness等）
  - 支持模糊匹配，容错能力强
  - 可自定义关键词映射规则

- **🔗 自动节点连接**
  - 自动创建并连接处理节点（aiMultiply、aiNormalMap、aiBump2d等）
  - 智能处理AO通道与baseColor的混合
  - 自动处理normalCamera通道的转换
  - 支持bump和displacement的智能连接

- **🤖 智能UDIM管理**
  - 自动检测UDIM格式贴图（1001-1999范围）
  - 一键设置UV平铺模式
  - 支持多种UDIM类型（ZBrush、Mudbox、Mari）

- **🎨 自动色彩空间设置**
  - 根据贴图类型自动设置正确的色彩空间
  - 支持自定义色彩空间映射规则
  - 自动设置alphaIsLuminance和ignoreColorSpaceFileRules

- **📝 智能材质命名**
  - 自动清理材质名称，移除专业术语和数字前缀
  - 保持材质命名规范统一

### 3. 渲染预设系统（Render Presets）

**专业的渲染配置管理工具**

- **💾 预设保存与加载**
  - 保存默认渲染属性
  - 保存Arnold渲染器参数
  - 保存AOV通道配置
  - 支持自定义预设名称

- **📋 预设管理**
  - 添加、修改、删除渲染预设
  - 快速切换不同渲染配置
  - 直接打开预设文件夹进行管理

- **⚙️ AOV管理**
  - 自动配置Cryptomatte通道
  - AOV预设管理系统
  - 通道验证与错误检查

### 4. 路径匹配与替换（Path Matching）

**强大的路径处理工具**

- **🔍 智能搜索与替换**
  - 支持材质、贴图、贴图路径的批量修改
  - 支持正则表达式和大小写忽略
  - 可选择修改范围（全部/表格内/选中项）

- **📊 批量路径修复**
  - 智能搜索模式：基于相似度算法自动匹配
  - 支持子文件夹递归搜索
  - 支持多层子文件夹搜索
  - 强制路径覆盖选项

### 5. 灯光管理（Light Manager）

**专业的灯光组织工具**

- **💡 灯光分类**
  - 自动识别场景中所有Arnold灯光
  - 按light group分类管理
  - 支持多种灯光类型（aiAreaLight、aiSkyDomeLight、aiPhotometricLight等）

- **🎯 AOV集成**
  - 自动设置灯光的AOV light group属性
  - 便于后期合成和灯光分层渲染

## 📖 使用指南

### 快速开始

#### 1. 启动插件

```python
# 在Maya脚本编辑器中运行
import Arnold_Magic_Node
Arnold_Magic_Node.Arnold_Magic_Node_UI()
```

#### 2. 使用贴图管理器

1. 打开插件后，右键点击窗口选择"贴图管理器"
2. 在表格中查看所有贴图信息
3. 使用搜索框快速定位材质或贴图
4. 选择需要处理的贴图，点击相应功能按钮

#### 3. 魔法连接贴图

1. 选择材质球和贴图节点
2. 右键菜单选择"魔法连接"
3. 插件会自动识别贴图类型并连接到正确通道
4. 可在设置中调整连接参数

#### 4. 修复缺失贴图

1. 在贴图管理器中点击"选出缺失"
2. 点击"自动修复路径"
3. 选择贴图所在的文件夹
4. 等待智能匹配完成

### 高级功能示例

#### 批量处理贴图

```python
# 示例：批量转换贴图格式
from Arnold_Magic_Node_lib import ImageProcessor

processor = ImageProcessor()
processor.convert_image_format(
    input_path='D:/textures/old_format.exr',
    output_path='D:/textures/new_format.jpg',
    output_format='jpg',
    jpg_quality=95
)
```

#### 自定义贴图匹配规则

插件支持自定义关键词映射，可在设置中修改：

- baseColor: base, diffuse, albedo, color
- normal: normal, nrm, nor
- roughness: rough, rgh, roughness
- metallic: metal, mtl, metallic
- 等等...

#### 智能路径匹配算法

插件使用多维度相似度算法进行贴图匹配：

```python
# 相似度计算权重（可调整）
weights = {
    'name_weight': 0.4,        # 文件名相似度权重
    'resolution_weight': 0.3,  # 分辨率相似度权重
    'format_weight': 0.1,       # 格式相似度权重
    'creation_time_weight': 0.2   # 创建时间相似度权重
}
```

### 快捷键配置

| 功能        | 快捷键 |
| ----------- | ------ |
| 材质创建    | Ctrl+M |
| AOV管理面板 | Ctrl+A |
| 节点优化    | Ctrl+O |
| 渲染诊断    | Ctrl+D |

## 🌐 支持与社区

### 系统要求

| 组件     | 最低要求                 |
| -------- | ------------------------ |
| Maya     | 2022.5+                  |
| Arnold   | 5.3.1+                   |
| Python   | 3.7+                     |
| 操作系统 | Windows 10/11, macOS 12+ |

### 依赖库

插件会自动安装以下依赖：

- PySide2/PySide6：Qt界面框架
- Pillow：图像处理
- pyexr：EXR格式支持
- msgpack：高效数据序列化
- ahocorapy：Aho-Corasick自动机算法
- python-Levenshtein：模糊匹配算法
- numpy：数值计算

### 常见问题

❓ **安装失败怎么办？**

- 确保Maya模块目录有写入权限
- 检查路径是否包含中文或特殊字符
- 验证Python环境是否配置正确
- 插件会自动检测并安装缺失的依赖库

💡 **材质显示异常？**

- 检查文件纹理的color space设置
- 验证Arnold渲染器版本兼容性
- 使用贴图管理器检查贴图加载状态
- 尝试使用"自动色彩空间"功能

🔍 **贴图路径丢失？**

- 使用贴图管理器的"选出缺失"功能
- 点击"自动修复路径"进行智能匹配
- 支持子文件夹搜索和缓存机制
- 可手动指定搜索范围

📦 **如何打包贴图？**

- 在贴图管理器中选择需要打包的贴图
- 点击"贴图打包器"
- 选择输出路径
- 可选是否删除源文件或复制TX文件

⚙️ **如何自定义设置？**

- 右键菜单选择"设置"
- 可调整语言、连接参数、色彩空间等
- 支持自定义贴图匹配关键词
- 可调整相似度计算权重

## 📜 许可证协议

本项目采用 **MIT License** 开源许可证，允许自由使用、修改和分发。

### 许可证条款

```
MIT License

Copyright (c) 2025 Arnold Magic Node Tools

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in Software without restriction, including without limitation rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of Software, and to permit persons to whom Software is
furnished to do so, subject to following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 使用须知

✅ **您可以：**

- 自由使用本插件用于个人或商业项目
- 修改源代码以适应您的需求
- 分发本插件（需保留版权声明）
- 将本插件集成到其他项目中

❌ **您需要：**

- 在所有副本或实质性部分中保留版权声明
- 在分发时包含完整的许可证文本

⚠️ **免责声明：**

- 本软件按"原样"提供，不提供任何明示或暗示的担保
- 作者不对使用本软件造成的任何损失负责
- 使用本软件即表示您同意上述条款

## 🤝 参与贡献

欢迎通过以下方式参与项目：

### 贡献代码

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 报告问题

- 在 Issues 中提交 Bug 报告
- 详细描述问题复现步骤
- 附上截图或错误日志

### 功能建议

- 在 Issues 中提出新功能建议
- 说明使用场景和预期效果
- 与社区讨论实现方案

### 文档改进

- 完善使用文档
- 翻译多语言版本
- 分享使用案例和教程

## 📞 联系我们

- **技术支持**：1925250542@qq.com
- **项目主页**：https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69
- **问题反馈**：https://flowus.cn/form/7b125d97-3971-40ee-ac8b-c338e4a91909?code=LZVF69
- **帮助文档**：https://flowus.cn/amazingike/share/6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！⭐**

Made with ❤️ by AmazingIke

[【立即下载】](https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69) | [【查看完整文档】](https://flowus.cn/amazingike/share/6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69)

</div>

**Last Updated: January 19, 2026**
