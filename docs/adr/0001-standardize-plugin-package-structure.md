# ADR-0001：规范化插件包结构

- 状态：已接受
- 日期：2026-08-05
- 修订：2026-08-05，将具名 Python 包提升到仓库根目录，移除 `scripts/` 承载层；运行时数据路径由 ADR-0002 单独决策
- 修订：2026-08-06，完成旧单体拆分，以 `tools` 作为功能编排层并固化最终依赖边界
- 修订：2026-08-06，将默认设置改为根级 `config/` 只读 JSON，并删除设置预设菜单
- 范围：Arnold Magic Node V2 结构重构

## 背景

重构前，插件采用根目录平铺脚本结构，主要入口为：

```text
installer.py
  → startup.main()
      → default_config.Main_program()
      → application.Main_program()
```

随着功能增加，现有结构出现了以下问题：

- `application.py` 同时承担界面构建、配置读写、业务编排和 Maya 场景修改。
- `arnold_magic_core.py` 同时包含纯匹配算法、文件扫描、Maya 节点操作、语言加载和消息反馈，不是真正独立的核心层。
- 通用顶级模块名容易与 Maya 长生命周期进程中的其他模块发生冲突。
- `import *` 和生产环境中的 `importlib.reload()` 隐藏了真实依赖，并可能产生新旧类引用混用。
- 静态语言资源、默认配置、用户设置、预设和缓存混合存放在安装目录中。
- 一次性全面重写会扩大回归范围，不符合逐个功能抽取的重构策略。

本次决策参考了 `forge_pipeline/forge_dcc/cinema_4d/plugins` 中 `core`、`services`、`state` 和 `ui` 的分层方式，但不会照搬其中的多顶级包、插件注册表、第三方依赖 bootstrap 或大型热重载机制。

## 决策

插件采用“仓库根目录下的单一具名 Python 包 + 稳定 Maya 入口 + 分层模块 + 渐进迁移”的结构。`arnold_magic_node/` 仍是唯一包边界，包内模块不会重新平铺到仓库根目录。

目标目录如下：

```text
Arnold-Magic-Node/
├─ ArnoldMagicNode.mod
├─ installer.py
│
├─ icons/
├─ config/
│  ├─ Arnold_Magic_Settings.json
│  └─ shader_convert_map.json
│
├─ arnold_magic_node/
│  ├─ __init__.py
│  ├─ bootstrap.py
│  ├─ version.py
│  │
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ magic_connection.py
│  │  ├─ naming.py
│  │  ├─ path_detection.py
│  │  ├─ paths.py
│  │  ├─ storage.py
│  │  ├─ matching.py
│  │  └─ similarity.py
│  │
│  ├─ maya/
│  │  ├─ __init__.py
│  │  ├─ environment.py
│  │  ├─ magic_connection.py
│  │  ├─ nodes.py
│  │  ├─ scene.py
│  │  ├─ textures.py
│  │  └─ aovs.py
│  │
│  ├─ tools/
│  │  ├─ __init__.py
│  │  ├─ aovs.py
│  │  ├─ feedback.py
│  │  ├─ magic_connection.py
│  │  ├─ materials.py
│  │  ├─ node_graph.py
│  │  ├─ path_detection.py
│  │  ├─ rendering.py
│  │  ├─ runtime.py
│  │  ├─ scene.py
│  │  ├─ selection.py
│  │  ├─ settings.py
│  │  └─ texture.py
│  │
│  ├─ ui/
│  │  ├─ __init__.py
│  │  ├─ _qt_compat.py
│  │  ├─ _workspace.py
│  │  ├─ main_window.py
│  │  ├─ settings_dialog.py
│  │  ├─ aov_light_group_dialog.py
│  │  └─ rendering_preset_dialog.py
│  │
│  └─ resources/
│     └─ i18n/
│
├─ tests/
│  └─ test_*.py
│
└─ docs/
   └─ adr/
```

该目录是最终目标结构，不要求第一阶段一次性创建全部空目录和空模块。只有开始迁移对应职责时，才创建相应文件。根级 `config/` 保存随插件发布的只读配置；用户修改后的设置仍写入 ADR-0002 定义的 Maya 用户目录。

截至 2026-08-06，本次源码分层已经完成。项目采用 `core`、`maya`、`tools`、`ui` 和 `bootstrap` 五层；`tools` 是功能编排层，替代早期草案中的 `services` 名称。`application.py`、`arnold_magic_core.py`、根级 `default_config.py` 和过渡期 `core/settings.py` 均已删除，不保留兼容转发模块。默认设置数据现位于 `config/Arnold_Magic_Settings.json`，初始化由 `tools/settings.py` 编排。

仓库根级 `Datas/` 仅作为旧版本地数据遗留目录，不再是生产运行时路径；`config/` 与 `icons/` 仍是仓库根级只读资源。

Maya 模块描述文件或 Installer 生成的 Shelf 命令必须把仓库根目录作为唯一 Python 搜索根；不得再引用 `scripts/`，也不得把 `core/`、`ui/` 等内部目录分别加入 `sys.path`。

### 第一阶段过渡布局（历史记录）

在职责尚未完成拆分期间，混合职责代码不得仅为了符合目标目录名称而被误认为已经完成分层。第一阶段采用以下过渡布局：

```text
arnold_magic_node/
├─ __init__.py
├─ bootstrap.py
├─ application.py          # 未拆分的业务与 Maya 操作单体，仍被迁移期 UI 调用
├─ arnold_magic_core.py    # 未拆分的算法与 Maya 操作单体
├─ default_config.py       # 未拆分的默认数据与初始化逻辑
├─ ui/
│  ├─ __init__.py
│  ├─ _qt_compat.py        # PySide/shiboken 兼容导入
│  ├─ _workspace.py        # Maya 主窗口获取和窗口清理辅助
│  ├─ main_window.py       # 主窗口，暂时调用 application
│  ├─ settings_dialog.py   # 设置窗口，类体原样迁移
│  ├─ aov_light_group_dialog.py
│  │                         # AOV 灯光组窗口、树组件和启动函数
│  ├─ rendering_preset_dialog.py
│  │                       # 渲染预设输入窗口及其迁移期共享状态
│  └─ texture_batch_importer_dialog.py
│                          # 休眠的批量导入窗口，不恢复入口
└─ core/
   ├─ __init__.py
   ├─ paths.py
   ├─ storage.py
   └─ matching.py
```

对应的整文件迁移关系为：

| 原文件 | 第一阶段位置 |
| --- | --- |
| `application.py` | `arnold_magic_node/application.py` |
| `arnold_magic_core.py` | `arnold_magic_node/arnold_magic_core.py` |
| `default_config.py` | `arnold_magic_node/default_config.py` |
| 原 `startup.py` 的启动实现 | `arnold_magic_node/bootstrap.py` |
| `storage.py` | `arnold_magic_node/core/storage.py` |
| `arnold_magic_matching.py` | `arnold_magic_node/core/matching.py` |
| `application.py` 中的 `MainWindow` | `arnold_magic_node/ui/main_window.py` |
| `application.py` 中的 Qt/shiboken 兼容导入 | `arnold_magic_node/ui/_qt_compat.py` |
| `application.py` 中的窗口辅助函数 | `arnold_magic_node/ui/_workspace.py` |
| `application.py` 中的设置窗口 | `arnold_magic_node/ui/settings_dialog.py` |
| `application.py` 中的 AOV 窗口组 | `arnold_magic_node/ui/aov_light_group_dialog.py` |
| `application.py` 中的渲染预设输入窗口组 | `arnold_magic_node/ui/rendering_preset_dialog.py` |
| `application.py` 中的休眠批量导入窗口 | `arnold_magic_node/ui/texture_batch_importer_dialog.py` |

旧版根级 `startup.py` 兼容入口已经删除，唯一公开入口为 `arnold_magic_node.show()`。已安装的旧 Shelf 命令不会自动更新；升级包位置后必须重新运行 Installer 并重启 Maya，避免旧命令或 `sys.modules` 缓存继续指向已删除的 `scripts/` 路径。

本 ADR 中的“整文件迁移”是指保持可观察行为不变，允许且仅允许修改包内导入、公共入口委托、Python 搜索根、因包深度减少而变化的项目资源根路径计算，将根级静态图标目录由 `icon/` 规范为 `icons/` 所需的路径引用，以及将窗口类、紧密关联的窗口辅助函数和共享 UI 状态按 AST 定义体不变地物理迁入 `ui/`。它不要求搬迁前后的源文件逐字节相同，也不代表窗口内部混合的业务职责已经完成分层。

`storage.py` 和 `arnold_magic_matching.py` 在进入 `core` 前必须确认不依赖 Maya、Arnold 或 Qt，不在导入时执行文件读写，并可由普通 Python 直接导入；当前两个文件已经满足这些条件。若其他旧文件不满足，不得仅凭名称将其放入 `core`。

## 分层职责

### `core`

`core` 保存与 Maya、Arnold 和 Qt 无关的稳定能力，包括：

- 常量和纯数据模型。
- 路径计算规则。
- 标准库 JSON 存储。
- 设置路径与标准库 JSON 存储。
- 国际化资源选择和读取。
- 贴图名称标准化、关键词匹配和编辑距离。
- 名称、分辨率、格式及创建时间的加权相似度计算。

`core` 必须满足以下约束：

- 只能依赖 Python 标准库和同层模块。
- 不得导入 `maya`、`mtoa`、PySide 或 shiboken。
- 导入模块时不得读写用户文件或修改全局环境。
- `paths.py` 只负责计算路径，不负责启动时批量创建目录。
- 所有核心逻辑必须能在普通 Python 进程中测试。

拆分期间，`arnold_magic_core.py` 没有整体移动到 `core/`。其中的纯算法已进入 `core`，Maya 操作和业务流程已分别进入 `maya` 与 `tools`，旧文件现已删除。

### `maya`

`maya` 封装所有宿主相关能力，包括：

- Maya 环境和用户目录查询。
- 当前选择和场景节点查询。
- 节点创建、属性修改和连接。
- 贴图尺寸、UDIM 和颜色空间操作。
- 材质、渲染设置及 AOV 操作。

该层可以依赖 `core`，但不能导入 `tools`、`ui` 或 `bootstrap`。

### `tools`

`tools` 表达用户能够直接执行的插件功能，并组合 `core` 与 `maya`：

- 快速连接。
- 魔法连接。
- 路径检测连接。
- 材质转换与修复。
- 节点混合。
- 渲染预设和灯光组。
- 场景名称优化。

工具编排层不负责创建窗口，不保存 Qt 控件引用。一个工具应对应一个明确的用户功能，并通过 `maya` 适配器访问宿主能力。

### `ui`

`ui` 只负责：

- 构建 Maya Workspace Control 和 Qt 窗口。
- 收集用户输入。
- 调用工具编排层。
- 展示结果、警告和错误。

业务判断、文件扫描和 Maya 节点网络创建不得直接实现于 UI 类中。PySide2、PySide6 和 shiboken 的兼容导入统一放在 `ui/_qt_compat.py`。旧 `application.py` 的过渡例外已经取消。

`settings_dialog.py`、`aov_light_group_dialog.py` 和 `rendering_preset_dialog.py` 已将配置、AOV 与渲染场景操作委托给 `tools`；UI 只保留窗口构建、输入采集和结果展示。`texture_batch_importer_dialog.py` 仅保存无活动入口的遗留窗口，不得重新接入菜单。

### `bootstrap`

最终状态下，`bootstrap.py` 是唯一的应用组装入口，只负责：

- 初始化缺失的用户配置。
- 关闭、复用或创建插件窗口。
- 组装 UI 与工具。
- 保存必要的窗口引用，防止 Qt 对象被回收。

包外只使用以下公共入口：

```python
import arnold_magic_node
arnold_magic_node.show()
```

`arnold_magic_node/__init__.py` 必须保持轻量、无副作用，并通过延迟导入暴露 `show()`。

`arnold_magic_node.show()` 是唯一包外公开 API，`bootstrap.main()` 是包内启动实现。`bootstrap` 直接初始化工具层并创建主窗口，不再经过旧应用单体或生产热重载。

## 依赖方向

最终依赖必须保持单向：

```text
bootstrap ──> ui / tools
ui        ──> tools
tools     ──> maya / core
maya      ──> core
core      ──> Python 标准库
```

`bootstrap` 是组合根。UI 不得绕过 `tools` 直接修改 Maya 场景；`tools` 不得直接导入 `maya.cmds` 或 `mtoa`，所有宿主访问通过 `maya` 适配器完成。

Maya 用户目录由 `maya/environment.py` 查询，再由 `bootstrap` 传给设置仓库。`core` 不得为了获取用户路径而直接导入 `maya.cmds`。

禁止事项：

- `core` 反向导入其他层。
- `maya` 导入工具层或界面层。
- `tools` 导入具体 Qt 窗口。
- 使用 `from ... import *`。
- 使用通用顶级模块名，例如重新建立根级 `core.py`。
- 在生产入口中执行 `importlib.reload()`。

开发热重载如有需要，应独立放置，只处理 `arnold_magic_node.*` 模块，并在重载前关闭现有窗口和回调。

### 历史过渡例外（已取消）

第一阶段为了保证物理移动不改变行为，曾暂时保留旧单体中的通配导入、`importlib.reload()` 和下述 UI 反向依赖：

窗口物理迁移期间曾允许以下临时反向依赖，用于调用尚未抽取的旧配置、业务和 Maya 实现：

- `ui.main_window → application`
- `ui.settings_dialog → application`
- `ui.aov_light_group_dialog → application`
- `ui.rendering_preset_dialog → application`

窗口模块还曾直接使用 `arnold_magic_core`，`settings_dialog` 也调用过旧 `default_config`。上述反向依赖、通配导入和生产热重载已经随职责迁入 `core`、`maya` 和 `tools` 全部删除。窗口生命周期现由 `bootstrap` 统一组装和清理。

## 资源与用户数据

Maya、Shelf 和插件界面可直接访问的公共静态图标放在仓库根目录（同时也是 Maya 模块根目录）的 `icons/`。该目录只包含随插件发布的只读图标，不存放运行时生成的数据。

随插件发布且只读的内容按访问方式存放：

- `i18n/`：Qt 翻译资源（`*.ts` 翻译源与 `*.qm` 编译产物，英文为源码语言不生成 `.qm`）。
- 根级 `config/`：默认设置与材质转换映射。

最终状态下，运行时可写数据不得写入插件安装目录。用户配置目录使用：

```python
Path(cmds.internalVar(userPrefDir=True)) / "arnold_magic_node"
```

建议按以下方式划分：

```text
arnold_magic_node/
├─ settings/
├─ presets/
│  └─ render/
├─ cache/
└─ logs/
```

继续采用“写入文件时按需创建父目录”的方式，不恢复启动时全量创建运行目录的模块。

第一阶段不移动现有 `Datas` 和 `config`，只通过 `core/paths.py` 让搬迁后的代码继续引用仓库根目录。根级 `icon/` 在本阶段规范为仓库根级 `icons/`，并同步更新 Installer 与应用内的图标路径引用。源码包提升不得改变 `Datas/`、`config/` 和 `icons/` 的实际位置。该阶段允许既有可写路径继续工作，但不得新增新的安装目录写入点。用户数据迁移、默认资源覆盖顺序和旧设置兼容需要在后续单独决策，不能与源码整文件移动同时进行。

## 命名与兼容性

- 新建以及完成拆分的 Python 包、目录、模块、函数和变量使用小写英文 `snake_case`。
- 新建以及完成拆分的类使用 `PascalCase`。
- 新建以及完成拆分的常量使用 `UPPER_SNAKE_CASE`。
- 包内使用明确的相对导入，不依赖 `sys.path` 中多个内部目录的顺序。
- 包内运行时代码不得动态修改 `sys.path` 来修补包定位；包发现只由 Maya 模块配置或外部 Installer 入口负责。
- 保持 Maya 2022 所需的 Python 3.7 语法兼容。
- 不使用 `list[str]`、`dict[str, ...]`、`X | None`、`match/case` 等较新语法。
- 不增加第三方运行时依赖，不在启动阶段下载或安装库。

## 渐进迁移

迁移按下列顺序分批完成：

1. 建立可重复运行的本地回归测试基线，并将 `tests/` 纳入版本控制。
2. 在仓库根目录建立 `arnold_magic_node` 包壳和稳定的 `show()` 入口；旧版根级 `startup.py` 兼容入口已在后续清理中删除。
3. 原样迁移 `storage.py` 与 `arnold_magic_matching.py` 到 `core`。
4. 在特征测试保护下，将 `MainWindow` 类体不变地物理迁入 `ui/main_window.py`，暂时保留对旧 `application` 的兼容调用。
5. 将 Qt 兼容层、窗口辅助、设置窗口、AOV 窗口、渲染预设输入窗口和休眠批量导入窗口按定义体不变的方式迁入 `ui/`，并保持休眠入口关闭。
6. 将纯加权相似度算法迁移到 `core/similarity.py`。
7. 以 Quick Connect 作为第一个完整功能，验证 `旧入口 → tools → maya` 的迁移方式。
8. 依次迁移小型节点工具、Magic Connection、Path Detection、材质转换与修复，并将渲染预设、AOV 和设置窗口中的非 UI 逻辑下沉到对应层。
9. 清除所有 UI 模块对 `application` 的过渡依赖，并完成主窗口与各子窗口的职责拆分。
10. 删除 `application.py`、`arnold_magic_core.py` 和根级 `default_config.py`，增加自动化分层依赖检查。
11. Texture Manager 在基础结构稳定后单独重新设计；休眠的 `TextureBatchImporterDialog` 是否保留另行决策。

每个功能分为两个步骤：

1. 先为旧实现增加特征测试，记录可观察行为。
2. 再迁移实现，并保持同一组测试通过。

结构移动与行为修复不得混在同一个提交中。新抽取的纯核心模块应达到至少 80% 的测试覆盖率。测试源码纳入版本控制，但发布包应单独排除 `tests/`。

普通 Python 回归命令为：

```text
python -m unittest discover -s tests -v
```

Maya 集成行为必须在支持的 Maya 环境中另行执行冒烟测试，普通 Python 测试不能替代宿主验证。

## 验收标准

每个迁移阶段必须满足：

- 重新运行 Installer 后生成的 Shelf 入口可以使用，且不引用旧 `scripts/` 路径。
- Maya 中连续打开两次不会产生重复窗口、旧实例或重复回调。
- 普通 Python 环境可以导入并测试 `arnold_magic_node.core`。
- Python 3.7 语法检查通过。
- 重构前后的节点类型、关键属性和连接关系保持一致；行为变化必须单独记录。
- 对应旧实现已删除或缩减为兼容委托，不长期保留两套实现。
- 不得存在通配导入、跨层反向依赖、生产热重载或 `ui → application` 过渡桥接。
- `core`、`maya` 和 `tools` 的依赖方向由普通 Python 架构测试持续检查。

第一阶段的历史验收项如下，保留用于追溯：

- 只修改内部导入、入口委托与重载顺序、包搜索路径、项目根路径引用、`icon/` 到 `icons/` 的静态资源路径引用，以及已记录窗口定义、窗口辅助和 UI 共享状态的物理位置与必要导入。
- `storage.py` 与匹配算法文件保持原内容迁移。
- `MainWindow`、设置窗口、AOV 窗口组、渲染预设输入窗口组和休眠批量导入窗口的定义体保持不变，旧位置不保留第二套实现。
- `application.py` 不再包含 Qt/shiboken、OpenMayaUI、mtoa AOV 界面依赖或顶层窗口构建代码；未迁移的业务类、函数、默认配置和可观察执行顺序保持不变。
- UI 对 `application` 的反向依赖严格限制在已记录的四条白名单；`application` 仅在 `Main_program()` 中延迟加载并按记录顺序重载活动 UI 模块。
- 入口会清理 `reload(application)` 遗留的旧 UI 名称，活动调用只指向新模块。
- `TextureBatchImporterDialog` 只移动且保持无活动入口，不得恢复已删除的 Texture Manager。
- Maya 冒烟测试必须分别连续打开主窗口、设置窗口和 AOV 窗口两次，并验证渲染预设的新增、修改和删除入口；普通 Python 测试不能替代该项。
- 根级 `config/` 和 `icons/` 的实际路径保持不变；旧 `Datas/` 不自动迁移、不读取、不写入，用户数据改由 ADR-0002 定义的 Maya 用户目录承载。
- 根级 `icon/` 已规范为仓库根级 `icons/`，所有活动图标引用均指向新目录。
- 不再存在承载源码的 `scripts/`，生产代码、Installer 和模块配置均不再把旧路径作为有效运行路径；文档只可在历史或禁止性说明中提及它。
- `import arnold_magic_node` 在仓库根目录作为唯一搜索根时可解析，并保持无 Maya/Qt 的急切导入。
- 新 Shelf 入口与 `arnold_magic_node.show()` 都能到达同一个 `arnold_magic_node.bootstrap.main()`。

## 被否决的方案

### 将 Python 模块直接平铺于仓库根目录

无法建立可靠依赖边界，并继续增加 Maya 模块名冲突和单体文件膨胀的风险。仓库根级的单一具名包 `arnold_magic_node/` 不属于该方案。

### 完整复制 C4D 插件结构

C4D 参考目录服务于多工具流水线，包含插件 ID 注册、解释器解析、第三方依赖和复杂热重载。本插件不需要这些能力，完整复制会违背轻量化目标。

### 一次性拆分全部代码

同时移动数千行代码会使功能回归难以定位，也无法判断问题来自目录迁移还是行为修改。

## 影响

正面影响：

- 模块职责和依赖方向明确。
- 核心算法可以脱离 Maya 快速测试。
- 每个功能可以独立迁移、维护和重写。
- 插件启动不再依赖通用模块名和不完整热重载。
- 静态资源与用户数据分离，安装目录可以保持只读。

代价与约束：

- 分批迁移需要维护特征测试和清晰的依赖注入边界。
- 功能移动前必须先补充特征测试。
- UI、工具和 Maya 操作之间需要显式传递依赖，初期代码量会略有增加。
- 目录结构本身不能代替边界约束，代码审查必须持续检查依赖方向。
