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

## 🤖 AI 接入层（开发接口）

项目已内置一个不依赖 `openai`、`requests` 或 `httpx` 的轻量客户端，直接使用 Python 标准库 `urllib` 调用 JSON HTTP 接口。当前支持：

- OpenAI Responses API（默认）
- OpenAI-compatible Chat Completions API
- JSON Schema 结构化输出与本地基础结构校验
- OpenAI、远程 HTTPS 兼容服务，以及无鉴权的本机回环服务

可以在插件的“设置 → AI 设置”中维护一个全局有序的模型列表。每个模型分别保存模型名称、Base URL、OpenAI API 协议、API Key、超时和请求大小限制；列表顺序只用于管理和显示，调用失败时不会自动切换到其他模型。“快速模式”和“复杂模式”各自单选一个模型，也可以选择同一个模型。

“测试当前模型”会在后台只向当前模型发送字符串 `"1"`，不会调用列表中的其他模型，也不会阻塞 Maya 界面。该操作会真实访问服务，可能产生极少量调用费用。

> [!WARNING]
> 每个模型的 API Key 会以明文保存到 Maya 用户目录下的 `arnold_magic_node/settings/AI_Settings.json`。请保护该文件和用户目录，不要提交、同步或分享配置文件。插件不会在界面状态、日志或错误消息中显示完整密钥。

在 Maya Python 中调用：

```python
from arnold_magic_node.core.ai_protocol import AiError
from arnold_magic_node.tools.ai_routing import create_ai_service

node_feature_schema = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "node_types": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["summary", "node_types"],
    "additionalProperties": False,
}

try:
    ai = create_ai_service()  # 固定使用设置中选定的快速模式模型

    # tools 端只提交输入，不选择具体模型；网络层按 SSE 流式接收内容。
    for delta in ai.stream(
        {"nodes": [], "connections": []},
        instructions="提取节点网络特征。",
    ):
        print(delta, end="")

    # 结构化结果同样通过流式接口接收，结束后再做本地 schema 校验。
    data = ai.generate_json(
        {"nodes": [], "connections": []},
        node_feature_schema,
        instructions="提取节点网络特征，只返回约定结构。",
        schema_name="node_features",
    )
    print(data)
except AiError as error:
    print("AI 调用失败：{}".format(error))
```

第一次实际创建客户端时，会按需生成用户配置：

```text
<Maya userAppDir>/arnold_magic_node/settings/AI_Settings.json
```

`AI_Settings.json` 使用 schema v3：`models` 是有序且相互独立的模型配置，`fast_model_id` 和 `complex_model_id` 分别引用快速、复杂模式使用的模型。远程服务必须使用 HTTPS；本地服务可使用 `http://127.0.0.1:<端口>/v1`，但不会接收 API Key。请求超时、连接失败或服务端报错都会直接返回给 tools 端，不会尝试列表中的下一个模型。

`create_ai_service()` 使用快速模式模型；需要复杂模式的内部工具可使用 `create_ai_service(mode="complex")`。服务创建后，tools 端调用 `stream()` 时只需提供输入和提示信息，不需要选择模型、接口或协议。旧版 schema v1/v2 配置会先在内存中迁移，用户下次保存 AI 设置时才写回 schema v3；旧配置中的备用模型会保留为独立条目，但不会继续执行错误轮换。

欢迎通过以下方式参与项目：
1. 提交Issue报告问题
2. 发起Pull Request改进代码
3. 参与文档翻译
4. 分享使用案例
