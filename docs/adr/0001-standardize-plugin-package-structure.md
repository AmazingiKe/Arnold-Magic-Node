# ADR-0001：规范化插件包结构

- 状态：已接受
- 日期：2026-08-05
- 范围：Arnold Magic Node V2 结构重构

## 背景

当前插件采用根目录平铺脚本结构，主要入口为：

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

插件采用“单一 Python 包 + 稳定 Maya 入口 + 分层模块 + 渐进迁移”的结构。

目标目录如下：

```text
Arnold-Magic-Node/
├─ ArnoldMagicNode.mod
├─ installer.py
│
├─ icons/
│
├─ scripts/
│  └─ arnold_magic_node/
│     ├─ __init__.py
│     ├─ bootstrap.py
│     ├─ version.py
│     │
│     ├─ core/
│     │  ├─ __init__.py
│     │  ├─ constants.py
│     │  ├─ models.py
│     │  ├─ paths.py
│     │  ├─ storage.py
│     │  ├─ settings.py
│     │  ├─ i18n.py
│     │  ├─ matching.py
│     │  └─ similarity.py
│     │
│     ├─ maya/
│     │  ├─ __init__.py
│     │  ├─ environment.py
│     │  ├─ selection.py
│     │  ├─ nodes.py
│     │  ├─ textures.py
│     │  ├─ materials.py
│     │  ├─ render.py
│     │  └─ aovs.py
│     │
│     ├─ services/
│     │  ├─ __init__.py
│     │  ├─ quick_connect.py
│     │  ├─ magic_connection.py
│     │  ├─ path_detection.py
│     │  ├─ material_conversion.py
│     │  ├─ material_repair.py
│     │  ├─ node_mix.py
│     │  ├─ render_presets.py
│     │  ├─ light_groups.py
│     │  └─ scene_naming.py
│     │
│     ├─ ui/
│     │  ├─ __init__.py
│     │  ├─ qt.py
│     │  ├─ workspace.py
│     │  ├─ main_window.py
│     │  ├─ settings_dialog.py
│     │  └─ aov_dialog.py
│     │
│     └─ resources/
│        ├─ i18n/
│        ├─ defaults/
│        └─ mappings/
│
├─ tests/
│  ├─ unit/
│  └─ maya/
│
└─ docs/
   └─ adr/
```

该目录是目标结构，不要求第一阶段一次性创建全部空目录和空模块。只有开始迁移对应职责时，才创建相应文件。

### 第一阶段过渡布局

在尚未拆分类和函数之前，混合职责文件不得为了符合目标目录名称而被错误归层。第一阶段采用以下过渡布局：

```text
scripts/arnold_magic_node/
├─ __init__.py
├─ bootstrap.py
├─ application.py          # 未拆分的 UI、业务与 Maya 操作单体
├─ arnold_magic_core.py    # 未拆分的算法与 Maya 操作单体
├─ default_config.py       # 未拆分的默认数据与初始化逻辑
└─ core/
   ├─ __init__.py
   ├─ paths.py
   ├─ storage.py
   └─ matching.py
```

对应的整文件迁移关系为：

| 原文件 | 第一阶段位置 |
| --- | --- |
| `application.py` | `scripts/arnold_magic_node/application.py` |
| `arnold_magic_core.py` | `scripts/arnold_magic_node/arnold_magic_core.py` |
| `default_config.py` | `scripts/arnold_magic_node/default_config.py` |
| `startup.py` | `scripts/arnold_magic_node/bootstrap.py` |
| `storage.py` | `scripts/arnold_magic_node/core/storage.py` |
| `arnold_magic_matching.py` | `scripts/arnold_magic_node/core/matching.py` |

根目录暂时保留薄层 `startup.py`，只用于兼容已经安装的旧 Shelf 命令。新入口使用 `arnold_magic_node.show()`。过渡模块不得新增业务功能；后续必须在特征测试保护下逐步拆除。

本 ADR 中的“整文件迁移”是指保持可观察行为不变，允许且仅允许修改包内导入、公共入口委托、项目资源根路径计算，以及将根级静态图标目录由 `icon/` 规范为 `icons/` 所需的路径引用。它不要求搬迁前后的源文件逐字节相同。

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

### `bootstrap`

`bootstrap.py` 是唯一的应用组装入口，只负责：

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

第一阶段为了保证整文件移动不改变行为，可以暂时保留旧单体文件中已经存在的通配导入和 `importlib.reload()`。它们属于明确的迁移期例外，不得新增，并必须在对应单体拆分完成时删除。因此第一阶段不视为已经达到最终依赖验收标准。

## 资源与用户数据

Maya、Shelf 和插件界面可直接访问的公共静态图标放在模块根目录 `icons/`。该目录只包含随插件发布的只读图标，不存放运行时生成的数据。

最终状态下，其余随插件发布且只读的内容放入包内 `resources/`：

- `i18n/`：语言文件。
- `defaults/`：默认设置。
- `mappings/`：材质和节点映射。

最终状态下，运行时可写数据不得写入插件安装目录。用户数据根目录使用：

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

第一阶段不移动现有 `Datas` 和 `config`，只通过 `core/paths.py` 让搬迁后的代码继续引用原项目根目录。根级 `icon/` 在本阶段规范为模块级 `icons/`，并同步更新 Installer 与应用内的图标路径引用。该阶段允许既有可写路径继续工作，但不得新增新的安装目录写入点。用户数据迁移、默认资源覆盖顺序和旧设置兼容需要在后续单独决策，不能与源码整文件移动同时进行。

## 命名与兼容性

- 新建以及完成拆分的 Python 包、目录、模块、函数和变量使用小写英文 `snake_case`。
- 新建以及完成拆分的类使用 `PascalCase`。
- 新建以及完成拆分的常量使用 `UPPER_SNAKE_CASE`。
- 包内使用明确的相对导入，不依赖 `sys.path` 中多个内部目录的顺序。
- 保持 Maya 2022 所需的 Python 3.7 语法兼容。
- 不使用 `list[str]`、`dict[str, ...]`、`X | None`、`match/case` 等较新语法。
- 不增加第三方运行时依赖，不在启动阶段下载或安装库。

## 渐进迁移

迁移不得采用一次性重写。顺序如下：

1. 将现有回归测试纳入版本控制，建立可重复运行的行为基线。
2. 建立 `scripts/arnold_magic_node` 包壳和稳定的 `show()` 入口，同时保留旧 Shelf 入口兼容。
3. 原样迁移 `storage.py` 与 `arnold_magic_matching.py` 到 `core`。
4. 将纯加权相似度算法迁移到 `core/similarity.py`。
5. 以 Quick Connect 作为第一个完整功能，验证 `旧入口 → service → maya` 的迁移方式。
6. 依次迁移小型节点工具、Magic Connection、Path Detection、材质转换与修复、渲染预设和 AOV。
7. 最后拆分设置窗口和主窗口。
8. Texture Manager 在基础结构稳定后单独重新设计。

每个功能分为两个步骤：

1. 先为旧实现增加特征测试，记录可观察行为。
2. 再迁移实现，并保持同一组测试通过。

结构移动与行为修复不得混在同一个提交中。新抽取的纯核心模块应达到至少 80% 的测试覆盖率。测试保留在源码仓库中，发布包可以单独排除 `tests/`。

第一阶段的普通 Python 基线命令为：

```text
python -m unittest discover -s tests -v
```

Maya 集成行为必须在支持的 Maya 环境中另行执行冒烟测试，普通 Python 测试不能替代宿主验证。

## 验收标准

每个迁移阶段必须满足：

- 原有 Shelf 入口仍可使用。
- Maya 中连续打开两次不会产生重复窗口、旧实例或重复回调。
- 普通 Python 环境可以导入并测试 `core`。
- Python 3.7 语法检查通过。
- 重构前后的节点类型、关键属性和连接关系保持一致；行为变化必须单独记录。
- 对应旧实现已删除或缩减为兼容委托，不长期保留两套实现。
- 除第一阶段明确列出的遗留通配导入和热重载外，不得新增通配导入、跨层反向依赖或生产热重载；对应单体拆分完成后必须清除这些遗留。

第一阶段还必须满足：

- 只修改内部导入、入口委托、项目根路径引用和 `icon/` 到 `icons/` 的静态资源路径引用。
- `storage.py` 与匹配算法文件保持原内容迁移。
- 大型单体中的类、函数、默认配置和可观察执行顺序保持不变。
- `Datas` 和 `config` 的实际路径保持不变。
- 根级 `icon/` 已规范为 `icons/`，所有活动图标引用均指向新目录。
- 旧 Shelf 与新包入口都能到达同一个 `bootstrap.main()`。

## 被否决的方案

### 保持根目录平铺

无法建立可靠依赖边界，并继续增加 Maya 模块名冲突和单体文件膨胀的风险。

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

- 迁移期间需要保留少量旧入口兼容代码。
- 功能移动前必须先补充特征测试。
- UI、服务和 Maya 操作之间需要显式传递依赖，初期代码量会略有增加。
- 目录结构本身不能代替边界约束，代码审查必须持续检查依赖方向。
