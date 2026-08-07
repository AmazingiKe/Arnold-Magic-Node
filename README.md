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

在启动 Maya 前给当前进程配置密钥，密钥不会写入插件设置：

```powershell
$env:OPENAI_API_KEY = "你的 API Key"
```

在 Maya Python 中调用：

```python
from arnold_magic_node.core.ai_protocol import AiError
from arnold_magic_node.tools.ai_client import create_openai_client

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
    client = create_openai_client()
    result = client.generate_json(
        instructions="提取节点网络特征，只返回约定结构。",
        input_data={"nodes": [], "connections": []},
        response_schema=node_feature_schema,
        schema_name="node_features",
    )
    print(result.data)
except AiError as error:
    print("AI 调用失败：{}".format(error))
```

第一次实际创建客户端时，会按需生成用户配置：

```text
<Maya userAppDir>/arnold_magic_node/settings/AI_Settings.json
```

连接其他兼容服务时修改 `base_url`、`model` 和 `api_style`。远程服务必须使用 HTTPS，并建议把专用密钥放入自定义的 `api_key_env`；本地服务可使用 `http://127.0.0.1:<端口>/v1`。客户端不会自动重试或在两种协议间自动降级，以免一次操作被重复计费。接口为同步调用，接入 UI 时应放到工作线程，避免阻塞 Maya 主线程。

欢迎通过以下方式参与项目：
1. 提交Issue报告问题
2. 发起Pull Request改进代码
3. 参与文档翻译
4. 分享使用案例
