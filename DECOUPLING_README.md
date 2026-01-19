# Arnold Magic Node 解耦架构说明

## 概述

本文档说明了Arnold Magic Node项目的解耦架构实现。该架构遵循依赖倒置原则(DIP)、单一职责原则(SRP)和开闭原则(OCP),实现了清晰的分层架构。

## 架构分层

```
┌─────────────────────────────────────────────────────────┐
│                   表现层（UI Layer）                     │
│  职责：用户界面展示和交互                                 │
│  依赖：业务逻辑层接口                                    │
└─────────────────────────────────────────────────────────┘
                          ↓ 依赖接口
┌─────────────────────────────────────────────────────────┐
│                 业务逻辑层（Service Layer）               │
│  职责：业务规则和流程控制                                 │
│  依赖：数据访问层接口                                    │
└─────────────────────────────────────────────────────────┘
                          ↓ 依赖接口
┌─────────────────────────────────────────────────────────┐
│                 数据访问层（Repository Layer）            │
│  职责：数据持久化和Maya API封装                          │
│  依赖：基础设施层                                        │
└─────────────────────────────────────────────────────────┘
                          ↓ 依赖接口
┌─────────────────────────────────────────────────────────┐
│               基础设施层（Infrastructure Layer）           │
│  职责：提供基础服务和工具                                   │
│  依赖：无                                              │
└─────────────────────────────────────────────────────────┘
```

## 模块结构

### 核心模块（core/）

提供基础服务和工具：

- **i_config_manager.py** - 配置管理器接口
- **i_logger.py** - 日志接口
- **i_event_bus.py** - 事件总线接口
- **config_manager.py** - 配置管理器实现
- **logger.py** - 日志器实现
- **event_bus.py** - 事件总线实现
- **di_container.py** - 依赖注入容器

### 配置模块（config/）

统一管理所有配置：

- **i_config_repository.py** - 配置仓储接口
- **config_repository.py** - 配置仓储实现（基于msgpack）

### 数据访问模块（data/）

封装数据访问逻辑：

- **i_config_repository.py** - 配置仓储接口
- **i_node_data_repository.py** - 节点数据仓储接口
- **i_file_system_repository.py** - 文件系统仓储接口
- **config_repository.py** - 配置仓储实现
- **node_data_repository.py** - 节点数据仓储实现（封装Maya cmds）
- **file_system_repository.py** - 文件系统仓储实现

### 服务模块（services/）

提供业务逻辑：

#### 贴图管理模块（services/texture_manager/）

- **i_texture_manager_service.py** - 贴图管理服务接口
- **texture_manager_service.py** - 贴图管理服务实现

#### 节点连接模块（services/node_connection/）

- **i_node_connection_service.py** - 节点连接服务接口
- **node_connection_service.py** - 节点连接服务实现

### 测试模块（tests/）

包含所有测试：

- **tests/core/** - 核心模块测试（37个测试用例）
- **tests/data/** - 数据访问层测试（17个测试用例）
- **tests/services/** - 服务层测试（12个测试用例）
- **tests/test_integration.py** - 集成测试（11个测试用例）

## 依赖注入

### 服务配置

所有服务通过`service_config.py`中的`configure_services()`函数配置：

```python
from service_config import get_container

container = get_container()

texture_service = container.resolve(ITextureManagerService)
node_service = container.resolve(INodeConnectionService)
```

### 服务生命周期

- **单例服务（Singleton）**：整个应用生命周期内只创建一次实例
  - ILogger
  - IEventBus
  - IConfigManager
  - IConfigRepository
  - INodeDataRepository
  - IFileSystemRepository

- **瞬态服务（Transient）**：每次解析都创建新实例
  - ITextureManagerService
  - INodeConnectionService

## 事件驱动

### 事件发布

服务层通过事件总线发布事件：

```python
self._event_bus.publish('textures.fixed', {
    'fixed_count': fixed_count,
    'failed_count': failed_count
})
```

### 事件订阅

UI层订阅事件以响应状态变化：

```python
self._event_bus.subscribe('textures.fixed', self._on_textures_fixed)

def _on_textures_fixed(self, data):
    self.update_ui(data)
```

## 测试

### 运行所有测试

```bash
python -m pytest tests/ -v
```

### 运行特定模块测试

```bash
# 核心模块测试
python -m pytest tests/core/ -v

# 数据访问层测试
python -m pytest tests/data/ -v

# 服务层测试
python -m pytest tests/services/ -v

# 集成测试
python -m pytest tests/test_integration.py -v
```

### 测试覆盖率

当前测试统计：
- 核心模块：37个测试用例
- 数据访问层：17个测试用例
- 服务层：12个测试用例
- 集成测试：11个测试用例
- **总计：77个测试用例，全部通过**

## 使用示例

### 基本使用

```python
from service_config import get_container

# 获取容器
container = get_container()

# 解析服务
texture_service = container.resolve(ITextureManagerService)

# 使用服务
all_textures = texture_service.get_all_textures()
```

### 事件订阅

```python
from service_config import get_container

container = get_container()
event_bus = container.resolve(IEventBus)

# 订阅事件
def on_textures_fixed(data):
    print(f"修复了 {data['fixed_count']} 个贴图")

event_bus.subscribe('textures.fixed', on_textures_fixed)
```

### 服务组合

```python
from service_config import get_container

container = get_container()

# 多个服务协作
texture_service = container.resolve(ITextureManagerService)
node_service = container.resolve(INodeConnectionService)

# 获取贴图
textures = texture_service.get_all_textures()

# 连接节点
for material, texture_data in textures.items():
    texture_nodes = list(texture_data.keys())
    node_service.auto_connect_nodes(material, texture_nodes, {})
```

## 优势

### 可维护性

- 清晰的模块边界
- 单一职责原则
- 易于定位和修复问题

### 可测试性

- 依赖注入便于mock
- 接口隔离便于单元测试
- 77个测试用例覆盖核心功能

### 可扩展性

- 通过接口扩展功能
- 事件驱动解耦模块间通信
- 依赖注入支持依赖替换

### 可复用性

- 服务独立，可在不同上下文中复用
- 接口定义清晰，易于理解和使用

## 后续工作

### UI层重构

将现有UI代码重构为使用新的服务层：

1. 使用依赖注入替代直接实例化
2. 通过事件总线更新UI
3. 移除UI层中的业务逻辑

### 更多服务

根据需要添加更多服务：

- 路径检测服务（PathDetectionService）
- 渲染预设服务（RenderPresetService）
- 材质修复服务（MaterialRepairService）

### 性能优化

- 优化关键路径
- 添加缓存机制
- 异步处理长时间操作

## 文档

- [解耦执行文档](./docs/decoupling_execution_guide.md) - 详细的解耦方案和实施步骤

## 联系

如有问题或建议，请联系项目维护者。
