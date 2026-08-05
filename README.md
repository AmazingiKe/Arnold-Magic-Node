# Arnold Magic Node Tool
!
![Maya Version](https://img.shields.io/badge/Maya-2022%20|%202023%20|%202024%20|%202025-orange)
![Arnold Version](https://img.shields.io/badge/Arnold-5.0+-blueviolet)
## 🌟 项目亮点
- **一键式PBR工作流**：自动构建符合行业标准的材质网络
- **批量处理**：支持同时处理多个材质球和对象
- **智能AOV管理**：自动化AOV通道配置与验证
- **节点优化**：自动清理冗余节点，提升场景性能
- **跨版本兼容**：全面支持Maya 2022至2025最新版本
## 📦 快速安装
### 自动安装（推荐）

将 `installer.py` 拖入 Maya 视窗，在当前 Shelf 创建启动按钮。
### 手动安装
1. 下载[最新发行包](https://example.com/download)
2. 解压到Maya模块目录：
   - **Windows**: `C:\Users\<用户>\Documents\maya\modules`
   - **macOS**: `~/Library/Preferences/Autodesk/maya/modules`
3. 创建模块描述文件 `arnoldMagic.mod`：
```
+ ArnoldMagic 1.0 <模块路径>
PYTHONPATH += <模块路径>
```
## 🛠️ 核心功能
### 材质工作流
- 自动创建PBR材质网络（金属/非金属工作流）
- 智能贴图连接（支持UDIM纹理识别）
- 一键材质转换（Standard Surface ↔ aiSurface）
- 批量重命名与材质替换
### AOV管理
- 自动配置Cryptomatte通道
- AOV预设管理系统
- 通道验证与错误检查
- 深度合成模板生成
### 渲染优化
- 自动代理生成器
- 灯光组管理系统
- 渲染统计报告
- 内存优化工具
## 📖 使用指南
### 基础工作流
```python
# 示例：批量创建金属材质
from arnold_magic import material_builder
builder = material_builder.MaterialFactory()
builder.create_batch(
    preset='metallic',
    textures={
        'base_color': 'textures/*_albedo.exr',
        'roughness': 'textures/*_roughness.exr'
    },
    assignment=['pSphere1', 'pCube1']
)
```
### 快捷键配置
| 功能                | 快捷键   |
|---------------------|----------|
| 材质创建            | Ctrl+M   |
| AOV管理面板         | Ctrl+A   |
| 节点优化            | Ctrl+O   |
| 渲染诊断            | Ctrl+D   |
## 🌐 支持与社区
### 系统要求
| 组件            | 最低要求               |
|-----------------|------------------------|
| Maya            | 2022.5+               |
| Arnold          | 5.3.1+                |
| Python          | 3.7+                  |
| 操作系统         | Windows 10/11, macOS 12+ |
### 常见问题
❓ **安装失败怎么办？**
- 确保Maya模块目录有写入权限
- 检查路径是否包含中文或特殊字符
- 验证Python环境是否配置正确
💡 **材质显示异常？**
- 检查文件纹理的color space设置
- 验证Arnold渲染器版本兼容性
- 使用`Render Diagnostics`工具进行自动检测
## 🤝 参与贡献
欢迎通过以下方式参与项目：
1. 提交Issue报告问题
2. 发起Pull Request改进代码
3. 参与文档翻译
4. 分享使用案例
贡献指南请见 [CONTRIBUTING.md](https://example.com/contributing)
## 📞 联系我们
- 技术支持：support@arnoldmagic.com
- 商务合作：biz@arnoldmagic.com
- 社区论坛：[forum.arnoldmagic.com](https://forum.arnoldmagic.com)
- Twitter: [@ArnoldMagicTool](https://twitter.com/ArnoldMagicTool)
---
[【立即下载】](https://example.com/download) | [【观看演示视频】](https://youtube.com/demo) | [【查看完整文档】](https://docs.arnoldmagic.com)

**Last Updated: March 24, 2025**
