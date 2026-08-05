# ADR-0002：将运行时数据迁移到 Maya 用户目录

- 状态：已采纳
- 日期：2026-08-05
- 范围：Arnold Magic Node 运行时数据与资源路径
- 关联：ADR-0001「规范化插件包结构」

## 背景

当前插件根目录下的 `Datas/` 混合了两种不同性质的内容：随插件发布的只读资源，以及运行后由用户和 Maya 生成的可写数据。

当前目录中已经出现以下内容：

- `languages/`：随插件发布的中英文语言资源，目前是 Git 跟踪文件。
- `settings/`：用户设置和语言选择，运行时会写入。
- `settings_presets/`：用户设置预设。
- `render_presets/`：用户渲染预设。
- `aov_light_group_manager/`：AOV 窗口缓存。
- `execution_logs/`、`keys/`、`logs/`：运行时日志或状态数据。
- `texture_manager/`：已删除功能遗留目录，不应在新结构中恢复。

当前代码通过项目根目录计算 `Datas/`，例如 `application.py`、`bootstrap.py`、`default_config.py` 和多个 UI 模块都直接拼接该路径。这会带来几个问题：

- 插件安装目录可能是只读目录，或由多个用户共享。
- 插件升级、替换或重新解压可能覆盖用户设置。
- 用户数据与插件版本、源代码和静态资源混在一起，不利于备份和迁移。
- 跨平台路径不应通过硬编码 Windows「文档」目录解决。

## 决策

`Datas/` 不整体迁移。将数据按“插件只读资源”和“用户可写数据”拆分：

1. 插件只读资源随插件发布，放在包内 `resources/` 或仓库根级静态资源目录。
2. 用户设置、预设、缓存、日志和运行状态迁移到 Maya 用户目录。
3. 用户目录由 Maya 提供，不硬编码操作系统的 `Documents` 路径。
4. 插件包和 `core` 不因为获取用户目录而直接修改 `sys.path`。

用户数据根目录使用 Maya 的 `cmds.internalVar(userAppDir=True)`，再追加插件专属目录名。该目录跨 Maya 版本共享，这是本项目当前明确选择；配置格式或版本不兼容时，后续另行增加版本化策略：

```text
<Maya user application directory>/arnold_magic_node/
```

该选择按 Maya 用户应用目录跨版本共享设置。配置格式或版本不兼容时，后续另行增加版本化策略；本次不混用其他 Maya 用户目录接口。

## 目录收敛规则

用户目录采用“有多个同类对象才建立分类目录”的规则，避免为单个文件或单个功能创建多层空壳：

- `settings/` 保留，因为设置文件和语言选择文件属于同一稳定类别。
- `presets/` 作为统一预设入口，当前包含 `settings/` 和 `render/` 两类预设；不再使用平级的 `settings_presets/` 与 `render_presets/`。
- 当前只有一种 AOV 缓存时，直接使用 `aov_light_group_cache.json`，不创建单独的 `cache/aov_light_group_manager/` 层级。
- `logs/` 可以作为统一日志目录，但日志类型不再继续创建 `logs/execution/` 等单一用途子目录。
- `keys` 只有在实际产生多个文件或明确需要命名空间时才创建；单个状态文件直接放在用户数据根目录。
- 已删除功能的目录不因历史文件或旧代码而恢复。

当某个分类最终只剩一个子目录时，应将文件直接提升到上一级，并同步更新迁移表和测试；目录名称不能仅为了“看起来分层”而存在。

目标用户目录示意：

```text
<Maya user application directory>/arnold_magic_node/
├─ settings/
│  ├─ Arnold_Magic_Settings.json
│  └─ language_config.json
├─ presets/
│  ├─ settings/
│  └─ render/
├─ aov_light_group_cache.json
└─ logs/
```

## 目录映射

| 当前路径 | 目标位置 | 性质 | 处理方式 |
| --- | --- | --- | --- |
| `Datas/languages/` | `arnold_magic_node/resources/i18n/` | 插件只读资源 | 已迁移到包内资源，不放入用户目录 |
| `Datas/settings/Arnold_Magic_Settings.json` | `<user-data>/settings/Arnold_Magic_Settings.json` | 用户设置 | 新版本不读取旧文件，首次运行创建默认值 |
| `Datas/settings/language_config.json` | `<user-data>/settings/language_config.json` | 用户设置 | 新版本不读取旧文件，首次运行按 Maya 语言创建 |
| `Datas/settings_presets/` | `<user-data>/presets/settings/` | 用户预设 | 收敛到统一预设目录，保留用户文件 |
| `Datas/render_presets/` | `<user-data>/presets/render/` | 用户预设 | 收敛到统一预设目录，保留用户文件 |
| `Datas/aov_light_group_manager/` | `<user-data>/aov_light_group_cache.json` | 运行时缓存 | 当前只有一种缓存，直接提升到用户数据根目录 |
| `Datas/execution_logs/` | `<user-data>/logs/` | 运行日志 | 与其他日志合并，不创建单一用途子目录 |
| `Datas/keys/` | `<user-data>/keys.json` | 运行时状态 | 仅在功能实际使用且只有单个状态文件时采用 |
| `Datas/logs/` | `<user-data>/logs/` | 运行日志 | 不作为插件资源发布 |
| `Datas/texture_manager/` | 无 | 已删除功能遗留 | 不迁移、不恢复 |
| `config/` | 仓库根级 `config/` | 插件只读配置 | 本 ADR 不迁移 |
| `icons/` | 仓库根级 `icons/` | 插件只读资源 | 本 ADR 不迁移 |

默认设置模板目前由 `default_config.py` 内置并在首次运行时写入用户目录；后续若模板需要独立维护，再迁入 `resources/defaults/`，不能把插件目录中的文件当作用户可写文件。

## 路径职责

路径职责分为三层：

- `arnold_magic_node/resources/` 和仓库根级 `config/`、`icons/`：只读插件资源。
- Maya 宿主适配层：调用 `cmds.internalVar(userAppDir=True)`，提供用户数据根目录。
- `core`：只接收已经解析好的路径并执行纯路径拼接和 JSON 存储，不直接导入 `maya` 或调用 `cmds`。

建议后续在 Maya 适配层提供类似以下语义的接口，而不是让每个功能自行拼接路径：

```text
get_user_data_root() -> <Maya user application directory>/arnold_magic_node
get_user_settings_path(name)
get_user_preset_path(kind, name)
get_user_cache_path(name)
get_user_log_path(name)
```

所有目录都采用“写入文件时创建父目录”的方式，不在插件导入或 Maya 启动时全量创建空目录；不存在实际文件时不创建对应分类目录。

## 旧数据处理策略

本次不自动迁移旧 `Datas/`。旧目录中的设置、预设和缓存保持原样，不读取、不复制、不删除；新版本从 Maya 用户目录开始使用默认设置。这样可以避免在没有用户确认的情况下改变旧文件，也让新路径的边界一次性明确。

如果未来需要帮助用户搬运旧设置，另行设计显式的“导入旧数据”功能和 ADR；该功能不属于本次路径切换。

## 实施顺序

本 ADR 的实现已按以下顺序完成路径切换；后续验证与显式旧数据导入仍保持独立：

1. 为用户根目录解析、目录映射和“不自动迁移”行为补充普通 Python 测试。
2. 在 Maya 适配层接入 `internalVar(userAppDir=True)`，并保持 `core` 不依赖 Maya。
3. 将设置、预设、AOV 缓存和日志调用点切换到统一路径接口。
4. 将 `languages/` 迁移到包内只读资源位置，并更新加载引用。
5. 在全新 Maya 环境和已有旧 `Datas/` 环境分别验证启动、设置保存、预设读写和窗口功能；确认旧目录未被访问或修改。
6. 经用户确认后，再单独处理仓库中遗留的旧 `Datas/` 空目录或本地文件。

## 验收标准

- 插件安装目录不再写入用户设置、预设、缓存或日志。
- 全新用户首次启动可以按需创建用户数据父目录。
- 用户目录不出现只有一层子目录的冗余包装，预设、缓存和日志路径符合收敛规则。
- 已有旧 `Datas/` 数据不会被覆盖、读取或删除；新版本从用户目录默认值启动。
- 用户目录路径不依赖硬编码的 Windows 文档路径，并能在支持的 Maya 平台工作。
- `core` 可以在普通 Python 环境中测试，不导入 Maya、Arnold、Qt 或 shiboken。
- 语言资源、图标和只读配置仍随插件发布，用户目录不承担插件资源分发职责。
- 删除或重新安装插件不会删除用户目录中的设置和预设。
- 用户目录初始化失败有明确错误，并且不会让插件导入直接崩溃。
- Maya 冒烟测试覆盖全新用户目录、已有旧 `Datas/` 数据保持不变、重复启动和重复打开设置窗口。

## 不在本次决策范围内

- 不重写设置数据格式，不把 JSON 改成其他序列化格式。
- 不重新实现 Texture Manager。
- 不同时拆分 `application.py` 的业务职责。
- 不在插件目录中保留第二份可写用户配置作为长期同步副本。
- 不在本 ADR 中设计跨版本配置格式升级或旧数据导入功能。

## 被否决的方案

### 继续把全部 `Datas/` 放在插件目录

会继续混合静态资源和用户数据，并保留安装目录权限、升级覆盖和多用户共享问题。

### 硬编码 Windows `Documents`

无法正确覆盖 Maya 版本目录、系统语言、目录重定向和其他操作系统；应使用 Maya 提供的用户目录接口。

### 自动迁移旧数据

会在用户未确认的情况下复制或改变旧文件，并把历史数据格式兼容问题隐含在启动流程中；本次选择保持旧数据原样，后续如有需要再提供显式导入。

## 影响

正面影响：

- 插件安装目录可以保持只读。
- 用户设置和预设独立于插件升级和重新安装。
- 静态资源、配置和运行时状态边界清晰。
- 未来可以独立备份、迁移和清理用户数据。

代价与约束：

- 旧用户需要手动重新设置，或未来使用显式导入功能。
- 需要为路径解析、按需初始化和失败恢复补充测试。
- Maya 宿主路径接口必须与纯核心逻辑保持边界。
