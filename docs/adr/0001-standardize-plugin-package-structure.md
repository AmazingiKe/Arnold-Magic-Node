# ADR-0001：规范化插件包结构

- 状态：已接受
- 日期：2026-08-05
- 修订：2026-08-05，将具名 Python 包提升到仓库根目录，移除 `scripts/` 承载层
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
│
├─ arnold_magic_node/
│  ├─ __init__.py
│  ├─ bootstrap.py
│  ├─ version.py
│  │
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ constants.py
│  │  ├─ models.py
│  │  ├─ paths.py
│  │  ├─ storage.py
│  │  ├─ settings.py
│  │  ├─ i18n.py
│  │  ├─ matching.py
│  │  └─ similarity.py
│  │
│  ├─ maya/
│  │  ├─ __init__.py
│  │  ├─ environment.py
│  │  ├─ selection.py
│  │  ├─ nodes.py
│  │  ├─ textures.py
│  │  ├─ materials.py
│  │  ├─ render.py
│  │  └─ aovs.py
│  │
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ quick_connect.py
│  │  ├─ magic_connection.py
│  │  ├─ path_detection.py
│  │  ├─ material_conversion.py
│  │  ├─ material_repair.py
│  │  ├─ node_mix.py
│  │  ├─ render_presets.py
│  │  ├─ light_groups.py
│  │  └─ scene_naming.py
│  │
│  ├─ ui/
│  │  ├─ __init__.py
│  │  ├─ qt.py
│  │  ├─ workspace.py
│  │  ├─ main_window.py
│  │  ├─ settings_dialog.py
│  │  ├─ aov_dialog.py
│  │  └─ rendering_preset_dialog.py
│  │
│  └─ resources/
│     ├─ i18n/
│     ├─ defaults/
│     └─ mappings/
│
├─ tests/
│  ├─ unit/
│  └─ maya/
│
└─ docs/
   └─ adr/
```

该目录是最终目标结构，不要求第一阶段一次性创建全部空目录和空模块。只有开始迁移对应职责时，才创建相应文件。目标树没有列出现阶段仍位于仓库根目录的 `Datas/` 和 `config/`；它们与最终 `resources/`、用户配置目录之间的映射尚未决定，不得根据目录名称直接搬迁。

截至本次修订，项目处于下述“第一阶段过渡布局”：具名包和 UI 已完成物理迁移，`Datas/`、`config/`、`icons/` 仍在仓库根目录，`maya/`、`services/` 和 `resources/` 等最终层尚未全部建立。

Maya 模块描述文件或 Installer 生成的 Shelf 命令必须把仓库根目录作为唯一 Python 搜索根；不得再引用 `scripts/`，也不得把 `core/`、`ui/` 等内部目录分别加入 `sys.path`。

### 第一阶段过渡布局

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
│  ├─ qt.py                # PySide/shiboken 兼容导入
│  ├─ workspace.py         # Maya 主窗口获取和窗口清理辅助
│  ├─ main_window.py       # 主窗口，暂时调用 application
│  ├─ settings_dialog.py   # 设置窗口，类体原样迁移
│  ├─ aov_dialog.py        # AOV 窗口、树组件和启动函数
│  ├─ rendering_preset_dialog.py
│  │                       # 渲染预设输入窗口及其迁移期共享状态
│  └─ texture_batch_importer.py
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
| `application.py` 中的 Qt/shiboken 兼容导入 | `arnold_magic_node/ui/qt.py` |
| `application.py` 中的窗口辅助函数 | `arnold_magic_node/ui/workspace.py` |
| `application.py` 中的设置窗口 | `arnold_magic_node/ui/settings_dialog.py` |
| `application.py` 中的 AOV 窗口组 | `arnold_magic_node/ui/aov_dialog.py` |
| `application.py` 中的渲染预设输入窗口组 | `arnold_magic_node/ui/rendering_preset_dialog.py` |
| `application.py` 中的休眠批量导入窗口 | `arnold_magic_node/ui/texture_batch_importer.py` |

旧版根级 `startup.py` 兼容入口已经删除，唯一公开入口为 `arnold_magic_node.show()`。已安装的旧 Shelf 命令不会自动更新；升级包位置后必须重新运行 Installer 并重启 Maya，避免旧命令或 `sys.modules` 缓存继续指向已删除的 `scripts/` 路径。

本 ADR 中的“整文件迁移”是指保持可观察行为不变，允许且仅允许修改包内导入、公共入口委托、Python 搜索根、因包深度减少而变化的项目资源根路径计算，将根级静态图标目录由 `icon/` 规范为 `icons/` 所需的路径引用，以及将窗口类、紧密关联的窗口辅助函数和共享 UI 状态按 AST 定义体不变地物理迁入 `ui/`。它不要求搬迁前后的源文件逐字节相同，也不代表窗口内部混合的业务职责已经完成分层。

`storage.py` 和 `arnold_magic_matching.py` 在进入 `core` 前必须确认不依赖 Maya、Arnold 或 Qt，不在导入时执行文件读写，并可由普通 Python 直接导入；当前两个文件已经满足这些条件。若其他旧文件不满足，不得仅凭名称将其放入 `core`。

## 分层职责

### `core`

`core` 保存与 Maya、Arnold 和 Qt 无关的稳定能力，包括：

- 常量和纯数据模型。
- 路径计算规则。
- 标准库 JSON 存储。
- 设置读取、默认值合并和配置迁移。
- 国际化资源选择和读取。
- 贴图名称标准化、关键词匹配和编辑距离。
- 名称、分辨率、格式及创建时间的加权相似度计算。

`core` 必须满足以下约束：

- 只能依赖 Python 标准库和同层模块。
- 不得导入 `maya`、`mtoa`、PySide 或 shiboken。
- 导入模块时不得读写用户文件或修改全局环境。
- `paths.py` 只负责计算路径，不负责启动时批量创建目录。
- 所有核心逻辑必须能在普通 Python 进程中测试。

当前 `arnold_magic_core.py` 不得整体移动到 `core/`。其中的纯算法进入 `core`，Maya 操作和业务流程分别进入 `maya` 与 `services`。

### `maya`

`maya` 封装所有宿主相关能力，包括：

- Maya 环境和用户目录查询。
- 当前选择和场景节点查询。
- 节点创建、属性修改和连接。
- 贴图尺寸、UDIM 和颜色空间操作。
- 材质、渲染设置及 AOV 操作。

该层可以依赖 `core`，但不能导入 `services`、`ui` 或 `bootstrap`。

### `services`

`services` 表达用户能够直接执行的插件功能，并组合 `core` 与 `maya`：

- 快速连接。
- 魔法连接。
- 路径检测连接。
- 材质转换与修复。
- 节点混合。
- 渲染预设和灯光组。
- 场景名称优化。

服务层不负责创建窗口，不保存 Qt 控件引用。一个服务应对应一个明确的用户功能。

### `ui`

`ui` 只负责：

- 构建 Maya Workspace Control 和 Qt 窗口。
- 收集用户输入。
- 调用服务层。
- 展示结果、警告和错误。

完成对应模块拆分后，业务判断、文件扫描和 Maya 节点网络创建不得直接实现于 UI 类中。PySide2、PySide6 和 shiboken 的兼容导入统一放在 `ui/qt.py`。第一阶段过渡 `application.py` 不受此最终状态约束，但不得继续增加混合职责。

当前 `settings_dialog.py`、`aov_dialog.py` 和 `rendering_preset_dialog.py` 只完成物理迁移，其中仍保留原窗口类内部已有的配置读写、Maya 操作和渲染数据采集。这些内容属于迁移期债务，后续仍须分别下沉到 `core`、`maya` 或 `services`；不得因为文件已经位于 `ui/` 就将其视为最终职责边界已经达成。`texture_batch_importer.py` 仅保存无活动入口的遗留窗口，不得由本阶段重新接入菜单。

### `bootstrap`

最终状态下，`bootstrap.py` 是唯一的应用组装入口，只负责：

- 初始化缺失的用户配置。
- 关闭、复用或创建插件窗口。
- 组装 UI 与服务。
- 保存必要的窗口引用，防止 Qt 对象被回收。

包外只使用以下公共入口：

```python
import arnold_magic_node
arnold_magic_node.show()
```

`arnold_magic_node/__init__.py` 必须保持轻量、无副作用，并通过延迟导入暴露 `show()`。

当前迁移期以 `arnold_magic_node.show()` 作为唯一包外公开 API，以 `bootstrap.main()` 作为包内启动实现。`bootstrap.main()` 会把旧应用组装临时委托给 `application.Main_program()`；后者负责清理旧绑定、按顺序重载 UI 模块并创建主窗口。这是待删除的兼容职责，不代表 `bootstrap` 的最终组装边界已经实现。

## 依赖方向

最终依赖必须保持单向：

```text
bootstrap ──> ui / services / maya / core
ui        ──> services / core
services  ──> maya / core
maya      ──> core
core      ──> Python 标准库
```

`bootstrap` 是组合根，可以导入所有下层实现并负责传递依赖。UI 可以读取 `core` 中的只读模型、翻译结果和设置值，但不能绕过服务层直接修改 Maya 场景。

Maya 用户目录由 `maya/environment.py` 查询，再由 `bootstrap` 传给设置仓库。`core` 不得为了获取用户路径而直接导入 `maya.cmds`。

禁止事项：

- `core` 反向导入其他层。
- `maya` 导入服务层或界面层。
- `services` 导入具体 Qt 窗口。
- 使用 `from ... import *`。
- 使用通用顶级模块名，例如重新建立根级 `core.py`。
- 在生产入口中执行 `importlib.reload()`。

开发热重载如有需要，应独立放置，只处理 `arnold_magic_node.*` 模块，并在重载前关闭现有窗口和回调。

第一阶段为了保证物理移动不改变行为，可以暂时保留旧单体文件中已经存在的通配导入和 `importlib.reload()`，并允许为重新绑定已迁移窗口而增加下述固定 UI 重载序列。它们属于明确的迁移期例外；除此之外不得新增重载，并必须在对应单体拆分完成时删除。因此第一阶段不视为已经达到最终依赖验收标准。

窗口物理迁移期间，允许以下临时反向依赖，用于调用尚未抽取的旧配置、业务和 Maya 实现：

- `ui.main_window → application`
- `ui.settings_dialog → application`
- `ui.aov_dialog → application`
- `ui.rendering_preset_dialog → application`

窗口模块还暂时直接使用尚未拆分的 `arnold_magic_core`，`settings_dialog` 另需调用旧 `default_config`。它们不是额外的 `ui → application` 桥接，但同样属于明确记录的遗留依赖；只允许复用当前所需符号，不得继续扩大，并须在职责迁入 `core`、`maya` 和 `services` 后删除。

`ui.qt`、`ui.workspace` 和休眠的 `ui.texture_batch_importer` 不得依赖 `application`。`application` 不得在模块初始化阶段导入任何具体 UI 模块，只能在 `Main_program()` 中等待旧模块完整加载后延迟导入。为使各窗口在现有 `application` 热重载后重新绑定最新对象，允许该入口按 `qt → workspace → settings_dialog → aov_dialog → rendering_preset_dialog → main_window` 的顺序同步重载活动 UI 模块；`texture_batch_importer` 保持休眠且不由入口加载。入口还应清理 Python `reload()` 遗留在 `application` 模块字典中的旧 UI 定义和已迁走的导入绑定。这些重载和反向依赖必须与 `application` 的生产热重载一起删除，不得扩展到其他模块。

UI 模块重载前，`Main_program()` 必须先关闭已有的设置窗口、AOV 窗口和渲染预设输入窗口；主窗口继续由 `MainWindow` 构造过程替换，休眠的批量导入窗口不参与活动入口。这样可避免旧类实例跨过模块重载继续存活。若后续增加其他独立窗口或回调，也必须纳入统一生命周期管理，并最终由 `bootstrap` 接管。

## 资源与用户数据

Maya、Shelf 和插件界面可直接访问的公共静态图标放在仓库根目录（同时也是 Maya 模块根目录）的 `icons/`。该目录只包含随插件发布的只读图标，不存放运行时生成的数据。

最终状态下，其余随插件发布且只读的内容放入 `arnold_magic_node/resources/`：

- `i18n/`：语言文件。
- `defaults/`：默认设置。
- `mappings/`：材质和节点映射。

最终状态下，运行时可写数据不得写入插件安装目录。用户配置目录使用：

```python
Path(cmds.internalVar(userPrefDir=True)) / "arnold_magic_node"
```

建议按以下方式划分：

```text
arnold_magic_node/
├─ settings/
├─ presets/
│  ├─ settings/
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

迁移不得采用一次性重写。顺序如下：

1. 建立可重复运行的本地回归测试基线；当前 `tests/` 按仓库策略保持忽略。
2. 在仓库根目录建立 `arnold_magic_node` 包壳和稳定的 `show()` 入口；旧版根级 `startup.py` 兼容入口已在后续清理中删除。
3. 原样迁移 `storage.py` 与 `arnold_magic_matching.py` 到 `core`。
4. 在特征测试保护下，将 `MainWindow` 类体不变地物理迁入 `ui/main_window.py`，暂时保留对旧 `application` 的兼容调用。
5. 将 Qt 兼容层、窗口辅助、设置窗口、AOV 窗口、渲染预设输入窗口和休眠批量导入窗口按定义体不变的方式迁入 `ui/`，并保持休眠入口关闭。
6. 将纯加权相似度算法迁移到 `core/similarity.py`。
7. 以 Quick Connect 作为第一个完整功能，验证 `旧入口 → service → maya` 的迁移方式。
8. 依次迁移小型节点工具、Magic Connection、Path Detection、材质转换与修复，并将渲染预设、AOV 和设置窗口中的非 UI 逻辑下沉到对应层。
9. 最后清除所有 UI 模块对 `application` 的过渡依赖，并完成主窗口与各子窗口的职责拆分。
10. Texture Manager 在基础结构稳定后单独重新设计；休眠的 `TextureBatchImporterWin` 是否保留另行决策。

每个功能分为两个步骤：

1. 先为旧实现增加特征测试，记录可观察行为。
2. 再迁移实现，并保持同一组测试通过。

结构移动与行为修复不得混在同一个提交中。新抽取的纯核心模块应达到至少 80% 的测试覆盖率。当前本地测试目录由 `.gitignore` 排除；若后续纳入版本控制，应继续在发布包中单独排除 `tests/`。

第一阶段的普通 Python 基线命令为：

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
- 除第一阶段明确列出的遗留通配导入、热重载和四条 `ui → application` 过渡桥接外，不得新增通配导入、跨层反向依赖或生产热重载；对应单体拆分完成后必须清除这些遗留。

第一阶段还必须满足：

- 只修改内部导入、入口委托与重载顺序、包搜索路径、项目根路径引用、`icon/` 到 `icons/` 的静态资源路径引用，以及已记录窗口定义、窗口辅助和 UI 共享状态的物理位置与必要导入。
- `storage.py` 与匹配算法文件保持原内容迁移。
- `MainWindow`、设置窗口、AOV 窗口组、渲染预设输入窗口组和休眠批量导入窗口的定义体保持不变，旧位置不保留第二套实现。
- `application.py` 不再包含 Qt/shiboken、OpenMayaUI、mtoa AOV 界面依赖或顶层窗口构建代码；未迁移的业务类、函数、默认配置和可观察执行顺序保持不变。
- UI 对 `application` 的反向依赖严格限制在已记录的四条白名单；`application` 仅在 `Main_program()` 中延迟加载并按记录顺序重载活动 UI 模块。
- 入口会清理 `reload(application)` 遗留的旧 UI 名称，活动调用只指向新模块。
- `TextureBatchImporterWin` 只移动且保持无活动入口，不得恢复已删除的 Texture Manager。
- Maya 冒烟测试必须分别连续打开主窗口、设置窗口和 AOV 窗口两次，并验证渲染预设的新增、修改和删除入口；普通 Python 测试不能替代该项。
- `Datas` 和 `config` 的实际路径保持不变。
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

- 迁移期间需要保留 `bootstrap.main() → application.Main_program()` 等少量包内过渡委托，但不恢复已删除的根级 `startup.py`。
- 功能移动前必须先补充特征测试。
- UI、服务和 Maya 操作之间需要显式传递依赖，初期代码量会略有增加。
- 目录结构本身不能代替边界约束，代码审查必须持续检查依赖方向。
