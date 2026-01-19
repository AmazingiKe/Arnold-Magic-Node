# Arnold Magic Node 项目解耦执行文档

**文档版本：** v1.0  
**创建日期：** 2026-01-19  
**作者：** Arnold Magic Node Team  
**状态：** 待实施

---

## 文档目录

1. [概述](#1-概述)
2. [技术选型依据](#2-技术选型依据)
3. [解耦方案设计](#3-解耦方案设计)
4. [实施步骤](#4-实施步骤)
5. [关键代码变更说明](#5-关键代码变更说明)
6. [测试策略及验证方法](#6-测试策略及验证方法)
7. [解耦前后代码对比分析](#7-解耦前后代码对比分析)
8. [维护注意事项](#8-维护注意事项)
9. [风险评估与应对](#9-风险评估与应对)
10. [附录](#10-附录)

---

## 1. 概述

### 1.1 项目背景

Arnold Magic Node 是一个功能强大的 Maya Arnold 渲染插件，提供贴图管理、节点连接、路径检测、渲染预设等功能。随着项目的发展，代码库中出现了严重的耦合问题，导致：

- **可维护性差**：全局变量污染、UI与业务逻辑混合
- **扩展性受限**：难以添加新功能，修改影响范围大
- **测试困难**：模块间依赖复杂，难以进行单元测试
- **协作困难**：代码职责不清，多人协作容易冲突

### 1.2 解耦目标

**核心目标：**
1. **保持用户体验不变** - UI界面、交互逻辑完全保持原有体验
2. **适度解耦** - 避免过度拆分，平衡解耦度与复杂度
3. **提升可维护性** - 清晰的模块边界，明确的职责划分
4. **增强可测试性** - 支持单元测试、集成测试、端到端测试
5. **支持独立开发** - 各模块可独立开发、测试、部署

**非目标：**
- 不追求完美的架构设计
- 不引入不必要的抽象层
- 不改变用户可见的功能行为

### 1.3 解耦原则

**核心原则：**

1. **单一职责原则（SRP）**
   - 每个模块只负责一个功能领域
   - UI层只负责用户交互
   - 业务逻辑层只负责业务规则
   - 数据访问层只负责数据持久化

2. **依赖倒置原则（DIP）**
   - 高层模块不依赖低层模块
   - 两者都依赖抽象接口
   - 接口不依赖实现细节

3. **开闭原则（OCP）**
   - 对扩展开放，对修改关闭
   - 通过配置和插件机制支持扩展

4. **适度原则**
   - 避免过度抽象
   - 避免不必要的接口
   - 保持代码简洁易懂

5. **渐进式重构**
   - 分阶段实施
   - 每阶段充分测试
   - 保持向后兼容

### 1.4 解耦范围

**包含范围：**
- 核心基础设施（配置管理、日志、事件总线）
- 数据访问层（节点数据、文件系统）
- 业务逻辑层（贴图管理、节点连接、路径检测等）
- UI层（所有UI窗口和对话框）

**不包含范围：**
- Maya API封装（保持现有方式）
- 第三方库集成（保持现有方式）
- 文件格式处理（保持现有方式）

---

## 2. 技术选型依据

### 2.1 依赖注入框架

**选择：** 自定义轻量级DI容器

**选择理由：**

| 方案 | 优势 | 劣势 | 评分 |
|-----|------|------|------|
| **自定义DI容器** | 轻量级、无额外依赖、完全可控 | 需要自行实现 | ⭐⭐⭐⭐⭐ |
| dependency-injector | 功能丰富、社区活跃 | 额外依赖、学习成本 | ⭐⭐⭐ |
| pinject | 简单易用 | 功能有限、维护不活跃 | ⭐⭐⭐ |
| injector | 性能好 | API复杂、文档不足 | ⭐⭐ |

**决策依据：**
- 项目规模适中，不需要复杂的DI功能
- 避免引入额外依赖，减少维护成本
- 完全可控，可以根据项目需求定制

### 2.2 测试框架

**选择：** pytest + pytest-mock + pytest-cov

**选择理由：**

| 框架 | 优势 | 劣势 | 评分 |
|-----|------|------|------|
| **pytest** | 简洁易用、插件丰富、社区活跃 | 无明显劣势 | ⭐⭐⭐⭐⭐ |
| unittest | 标准库、无需安装 | 冗长、不够灵活 | ⭐⭐⭐ |
| nose2 | 功能丰富 | 维护不活跃 | ⭐⭐ |

**决策依据：**
- pytest 是Python社区主流测试框架
- 插件生态丰富（pytest-mock、pytest-cov等）
- 简洁的语法，易于编写和维护

### 2.3 事件总线

**选择：** 自定义轻量级事件总线

**选择理由：**

| 方案 | 优势 | 劣势 | 评分 |
|-----|------|------|------|
| **自定义事件总线** | 轻量级、无额外依赖、完全可控 | 需要自行实现 | ⭐⭐⭐⭐⭐ |
| PyPubSub | 功能丰富、成熟稳定 | 额外依赖、功能过重 | ⭐⭐⭐ |
| RxPY | 功能强大、响应式编程 | 学习成本高、功能过重 | ⭐⭐ |

**决策依据：**
- 项目需求简单，不需要复杂的消息传递机制
- 避免引入额外依赖
- 完全可控，可以根据项目需求定制

### 2.4 配置管理

**选择：** 基于现有msgpack的配置管理器

**选择理由：**

| 方案 | 优势 | 劣势 | 评分 |
|-----|------|------|------|
| **msgpack + 自定义管理器** | 高性能、二进制格式、现有基础 | 需要自行实现管理器 | ⭐⭐⭐⭐⭐ |
| JSON | 可读性好、标准格式 | 性能较差、文件较大 | ⭐⭐⭐ |
| YAML | 可读性好、支持注释 | 额外依赖、性能较差 | ⭐⭐⭐ |
| TOML | 简洁易读 | 额外依赖、生态较小 | ⭐⭐ |

**决策依据：**
- 项目已使用msgpack，保持一致性
- 二进制格式性能好，适合大量配置数据
- 避免引入额外依赖

### 2.5 日志框架

**选择：** Python标准库logging + 自定义封装

**选择理由：**

| 方案 | 优势 | 劣势 | 评分 |
|-----|------|------|------|
| **logging + 自定义封装** | 标准库、无需安装、功能强大 | 需要自行封装 | ⭐⭐⭐⭐⭐ |
| loguru | 简洁易用、功能丰富 | 额外依赖、性能略差 | ⭐⭐⭐⭐ |
| structlog | 结构化日志、可配置性强 | 学习成本高、额外依赖 | ⭐⭐⭐ |

**决策依据：**
- logging是Python标准库，无需额外依赖
- 功能强大，满足项目需求
- 通过自定义封装提供更友好的API

---

## 3. 解耦方案设计

### 3.1 架构设计

#### 3.1.1 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                   表现层（UI Layer）                     │
│  职责：用户界面展示和交互                                 │
│  包含：Arnold_Magic_Node_UI, TextureManagerWin等        │
│  依赖：业务逻辑层接口                                    │
└─────────────────────────────────────────────────────────┘
                          ↓ 依赖接口
┌─────────────────────────────────────────────────────────┐
│                 业务逻辑层（Service Layer）               │
│  职责：业务规则和流程控制                                 │
│  包含：TextureManagerService, NodeConnectionService等     │
│  依赖：数据访问层接口                                    │
└─────────────────────────────────────────────────────────┘
                          ↓ 依赖接口
┌─────────────────────────────────────────────────────────┐
│                 数据访问层（Repository Layer）            │
│  职责：数据持久化和Maya API封装                          │
│  包含：NodeDataRepository, FileSystemRepository等        │
│  依赖：基础设施层                                        │
└─────────────────────────────────────────────────────────┘
                          ↓ 依赖接口
┌─────────────────────────────────────────────────────────┐
│               基础设施层（Infrastructure Layer）           │
│  职责：提供基础服务和工具                                   │
│  包含：ConfigManager, Logger, EventBus, DIContainer     │
│  依赖：无                                              │
└─────────────────────────────────────────────────────────┘
```

#### 3.1.2 模块划分

**核心模块（Core）**
- 路径：`core/`
- 职责：提供基础服务和工具
- 包含：
  - `config_manager.py` - 配置管理器
  - `logger.py` - 日志器
  - `event_bus.py` - 事件总线
  - `di_container.py` - 依赖注入容器
- 依赖：无
- 被依赖：所有其他模块

**配置模块（Config）**
- 路径：`config/`
- 职责：统一管理所有配置
- 包含：
  - `config_repository.py` - 配置仓储
  - `config_validator.py` - 配置验证器
- 依赖：Core
- 被依赖：Service, UI

**数据访问模块（Data）**
- 路径：`data/`
- 职责：封装数据访问逻辑
- 包含：
  - `node_data_repository.py` - 节点数据仓储
  - `file_system_repository.py` - 文件系统仓储
- 依赖：Core
- 被依赖：Service

**贴图管理模块（TextureManager）**
- 路径：`services/texture_manager/`
- 职责：贴图管理相关业务逻辑
- 包含：
  - `texture_manager_service.py` - 贴图管理服务
  - `texture_path_service.py` - 贴图路径服务
  - `texture_image_service.py` - 贴图图像服务
- 依赖：Core, Config, Data
- 被依赖：UI

**节点连接模块（NodeConnection）**
- 路径：`services/node_connection/`
- 职责：节点连接和材质处理
- 包含：
  - `node_connection_service.py` - 节点连接服务
  - `material_service.py` - 材质服务
  - `udim_service.py` - UDIM服务
- 依赖：Core, Config, Data
- 被依赖：UI

**路径检测模块（PathDetection）**
- 路径：`services/path_detection/`
- 职责：路径匹配和智能搜索
- 包含：
  - `path_detection_service.py` - 路径检测服务
  - `similarity_calculator.py` - 相似度计算器
- 依赖：Core, Config, Data
- 被依赖：TextureManager, NodeConnection

**渲染预设模块（RenderPreset）**
- 路径：`services/render_preset/`
- 职责：渲染预设和AOV管理
- 包含：
  - `render_preset_service.py` - 渲染预设服务
  - `aov_service.py` - AOV服务
  - `light_group_service.py` - 灯光组服务
- 依赖：Core, Config, Data
- 被依赖：UI

**材质修复模块（MaterialRepair）**
- 路径：`services/material_repair/`
- 职责：材质转换和智能修复
- 包含：
  - `material_repair_service.py` - 材质修复服务
  - `material_converter.py` - 材质转换器
- 依赖：Core, Config, Data, NodeConnection
- 被依赖：UI

**UI模块（UI）**
- 路径：`ui/`
- 职责：用户界面和交互
- 包含：
  - `main_window.py` - 主窗口
  - `texture_manager_window.py` - 贴图管理器窗口
  - `settings_panel.py` - 设置面板
  - `aov_manager_window.py` - AOV管理器窗口
- 依赖：所有Service
- 被依赖：无

### 3.2 接口设计

#### 3.2.1 核心接口

**IConfigManager - 配置管理器接口**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

class IConfigManager(ABC):
    """
    配置管理器接口
    
    职责：
    - 提供统一的配置访问接口
    - 支持嵌套配置的读写
    - 支持配置的重新加载和保存
    """
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        参数:
            key: 配置键
            default: 默认值
            
        返回:
            配置值
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        参数:
            key: 配置键
            value: 配置值
        """
        pass
    
    @abstractmethod
    def get_nested(self, key_path: List[str], default: Any = None) -> Any:
        """
        获取嵌套配置值
        
        参数:
            key_path: 配置键路径，如 ['level1', 'level2', 'key']
            default: 默认值
            
        返回:
            配置值
        """
        pass
    
    @abstractmethod
    def set_nested(self, key_path: List[str], value: Any) -> None:
        """
        设置嵌套配置值
        
        参数:
            key_path: 配置键路径，如 ['level1', 'level2', 'key']
            value: 配置值
        """
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """
        重新加载配置
        """
        pass
    
    @abstractmethod
    def save(self) -> None:
        """
        保存配置
        """
        pass
```

**ILogger - 日志接口**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
from enum import Enum

class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ILogger(ABC):
    """
    日志接口
    
    职责：
    - 提供统一的日志记录接口
    - 支持不同级别的日志记录
    - 支持结构化日志
    """
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """
        记录调试信息
        
        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """
        记录信息
        
        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """
        记录警告
        
        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """
        记录错误
        
        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """
        记录严重错误
        
        参数:
            message: 日志消息
            **kwargs: 额外的日志上下文信息
        """
        pass
```

**IEventBus - 事件总线接口**

```python
from abc import ABC, abstractmethod
from typing import Callable, Any, Optional

class IEventBus(ABC):
    """
    事件总线接口
    
    职责：
    - 提供事件发布订阅机制
    - 支持事件的异步处理
    - 解耦模块间的通信
    """
    
    @abstractmethod
    def subscribe(self, event_name: str, callback: Callable) -> str:
        """
        订阅事件
        
        参数:
            event_name: 事件名称
            callback: 回调函数
            
        返回:
            订阅ID，用于取消订阅
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, event_name: str, callback_id: str) -> bool:
        """
        取消订阅
        
        参数:
            event_name: 事件名称
            callback_id: 订阅ID
            
        返回:
            是否成功取消订阅
        """
        pass
    
    @abstractmethod
    def publish(self, event_name: str, data: Any = None) -> None:
        """
        发布事件
        
        参数:
            event_name: 事件名称
            data: 事件数据
        """
        pass
    
    @abstractmethod
    def clear(self, event_name: Optional[str] = None) -> None:
        """
        清除事件订阅
        
        参数:
            event_name: 事件名称，如果为None则清除所有订阅
        """
        pass
```

#### 3.2.2 数据访问接口

**IConfigRepository - 配置仓储接口**

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class IConfigRepository(ABC):
    """
    配置仓储接口
    
    职责：
    - 封装配置文件的读写操作
    - 提供配置验证功能
    """
    
    @abstractmethod
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        参数:
            config_path: 配置文件路径
            
        返回:
            配置字典
        """
        pass
    
    @abstractmethod
    def save_config(self, config_path: str, config: Dict[str, Any]) -> None:
        """
        保存配置文件
        
        参数:
            config_path: 配置文件路径
            config: 配置字典
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置
        
        参数:
            config: 配置字典
            
        返回:
            是否有效
        """
        pass
```

**INodeDataRepository - 节点数据仓储接口**

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class INodeDataRepository(ABC):
    """
    节点数据仓储接口
    
    职责：
    - 封装Maya节点数据的访问
    - 提供节点查询和操作接口
    """
    
    @abstractmethod
    def get_all_nodes(self, node_types: List[str]) -> List[str]:
        """
        获取指定类型的所有节点
        
        参数:
            node_types: 节点类型列表
            
        返回:
            节点名称列表
        """
        pass
    
    @abstractmethod
    def get_node_attribute(self, node_name: str, attribute: str) -> Any:
        """
        获取节点属性
        
        参数:
            node_name: 节点名称
            attribute: 属性名称
            
        返回:
            属性值
        """
        pass
    
    @abstractmethod
    def set_node_attribute(self, node_name: str, attribute: str, value: Any) -> None:
        """
        设置节点属性
        
        参数:
            node_name: 节点名称
            attribute: 属性名称
            value: 属性值
        """
        pass
    
    @abstractmethod
    def get_upstream_nodes(self, node_name: str, node_types: List[str]) -> List[str]:
        """
        获取上游节点
        
        参数:
            node_name: 节点名称
            node_types: 节点类型列表
            
        返回:
            上游节点名称列表
        """
        pass
```

#### 3.2.3 业务逻辑接口

**ITextureManagerService - 贴图管理服务接口**

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ITextureManagerService(ABC):
    """
    贴图管理服务接口
    
    职责：
    - 提供贴图管理相关业务逻辑
    - 包括贴图查询、过滤、修复、处理等功能
    """
    
    @abstractmethod
    def get_all_textures(self) -> Dict[str, Any]:
        """
        获取所有贴图信息
        
        返回:
            贴图信息字典，格式为 {材质名: {贴图名: 贴图信息}}
        """
        pass
    
    @abstractmethod
    def filter_textures(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        过滤贴图
        
        参数:
            filters: 过滤条件，如 {'isLoaded': False, 'minSize': 10}
            
        返回:
            过滤后的贴图信息
        """
        pass
    
    @abstractmethod
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复缺失贴图
        
        参数:
            search_path: 搜索路径
            options: 修复选项
            
        返回:
            修复结果，包含修复数量、失败列表等
        """
        pass
    
    @abstractmethod
    def process_images(self, texture_list: List[str], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        批量处理图像
        
        参数:
            texture_list: 贴图节点列表
            options: 处理选项，如格式、缩放比例等
            
        返回:
            处理结果
        """
        pass
    
    @abstractmethod
    def pack_textures(self, texture_list: List[str], output_path: str, options: Dict[str, Any]) -> bool:
        """
        打包贴图
        
        参数:
            texture_list: 贴图节点列表
            output_path: 输出路径
            options: 打包选项
            
        返回:
            是否成功
        """
        pass
```

**INodeConnectionService - 节点连接服务接口**

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class INodeConnectionService(ABC):
    """
    节点连接服务接口
    
    职责：
    - 提供节点连接相关业务逻辑
    - 包括自动连接、直接连接、UV统一等功能
    """
    
    @abstractmethod
    def auto_connect_nodes(self, material_name: str, texture_nodes: List[str], 
                          options: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动连接节点
        
        参数:
            material_name: 材质名称
            texture_nodes: 贴图节点列表
            options: 连接选项
            
        返回:
            连接结果
        """
        pass
    
    @abstractmethod
    def direct_connect_nodes(self, material_name: str, texture_nodes: List[str], 
                            channel_map: Dict[str, str]) -> bool:
        """
        直接连接节点
        
        参数:
            material_name: 材质名称
            texture_nodes: 贴图节点列表
            channel_map: 通道映射
            
        返回:
            是否成功
        """
        pass
    
    @abstractmethod
    def unify_uv_nodes(self, texture_nodes: List[str]) -> bool:
        """
        统一UV节点
        
        参数:
            texture_nodes: 贴图节点列表
            
        返回:
            是否成功
        """
        pass
    
    @abstractmethod
    def set_color_space(self, texture_nodes: List[str], color_space: str) -> bool:
        """
        设置色彩空间
        
        参数:
            texture_nodes: 贴图节点列表
            color_space: 色彩空间
            
        返回:
            是否成功
        """
        pass
    
    @abstractmethod
    def set_udim_mode(self, texture_nodes: List[str]) -> bool:
        """
        设置UDIM模式
        
        参数:
            texture_nodes: 贴图节点列表
            
        返回:
            是否成功
        """
        pass
```

### 3.3 模块通信方式

#### 3.3.1 依赖注入

**构造函数注入（推荐）：**

```python
class TextureManagerService(ITextureManagerService):
    """贴图管理服务实现"""
    
    def __init__(
        self,
        config_manager: IConfigManager,
        logger: ILogger,
        node_data_repo: INodeDataRepository,
        file_system_repo: IFileSystemRepository,
        event_bus: IEventBus
    ):
        """
        初始化服务
        
        参数:
            config_manager: 配置管理器
            logger: 日志器
            node_data_repo: 节点数据仓储
            file_system_repo: 文件系统仓储
            event_bus: 事件总线
        """
        self._config = config_manager
        self._logger = logger
        self._node_repo = node_data_repo
        self._file_repo = file_system_repo
        self._event_bus = event_bus
```

**属性注入（用于可选依赖）：**

```python
class TextureManagerService(ITextureManagerService):
    def __init__(self, config_manager: IConfigManager):
        self._config = config_manager
        self._logger: Optional[ILogger] = None
    
    def set_logger(self, logger: ILogger) -> None:
        """设置日志器"""
        self._logger = logger
```

#### 3.3.2 事件驱动

**事件发布：**

```python
class TextureManagerService(ITextureManagerService):
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失贴图"""
        # 执行修复逻辑
        result = self._do_fix(search_path, options)
        
        # 发布事件
        self._event_bus.publish('textures.fixed', {
            'fixed_count': result['fixed_count'],
            'failed_count': result['failed_count']
        })
        
        return result
```

**事件订阅：**

```python
class TextureManagerWindow:
    def __init__(self, texture_service: ITextureManagerService, event_bus: IEventBus):
        self._texture_service = texture_service
        self._event_bus = event_bus
        
        # 订阅事件
        self._event_bus.subscribe('textures.fixed', self._on_textures_fixed)
    
    def _on_textures_fixed(self, data: Dict[str, Any]) -> None:
        """贴图修复完成回调"""
        self.update_ui(data)
```

#### 3.3.3 回调函数

**同步回调：**

```python
class TextureManagerService(ITextureManagerService):
    def process_images(self, texture_list: List[str], options: Dict[str, Any], 
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> Dict[str, Any]:
        """批量处理图像"""
        total = len(texture_list)
        for i, texture in enumerate(texture_list):
            # 处理图像
            self._process_single_image(texture, options)
            
            # 调用进度回调
            if progress_callback:
                progress_callback(i + 1, total)
        
        return {'success': True}
```

**异步回调：**

```python
class TextureManagerService(ITextureManagerService):
    def fix_missing_textures_async(self, search_path: str, options: Dict[str, Any],
                                  completion_callback: Callable[[Dict[str, Any]], None]) -> None:
        """异步修复缺失贴图"""
        def _do_fix():
            result = self._do_fix(search_path, options)
            completion_callback(result)
        
        # 在后台线程执行
        import threading
        thread = threading.Thread(target=_do_fix)
        thread.start()
```

### 3.4 解耦边界定义

#### 3.4.1 UI层边界

**职责：**
- 用户界面展示
- 用户交互处理
- 界面状态管理

**不应包含：**
- 业务逻辑
- 数据访问
- 配置管理

**依赖：**
- 业务逻辑层接口（Service）
- 基础设施层接口（Logger, EventBus）

**示例：**

```python
# ✅ 正确：UI层只负责界面展示
class TextureManagerWindow:
    def __init__(self, texture_service: ITextureManagerService):
        self._texture_service = texture_service
    
    def on_fix_button_clicked(self):
        """修复按钮点击"""
        # 调用服务层
        result = self._texture_service.fix_missing_textures(
            self.get_search_path(),
            self.get_options()
        )
        # 更新UI
        self.update_result(result)

# ❌ 错误：UI层包含业务逻辑
class TextureManagerWindow:
    def on_fix_button_clicked(self):
        """修复按钮点击"""
        # 直接操作文件系统（业务逻辑）
        import os
        files = os.listdir(self.get_search_path())
        for file in files:
            # ... 复杂的业务逻辑
```

#### 3.4.2 业务逻辑层边界

**职责：**
- 业务规则实现
- 业务流程控制
- 数据转换

**不应包含：**
- UI相关代码
- 直接的文件系统操作（通过Repository）
- 直接的Maya API调用（通过Repository）

**依赖：**
- 数据访问层接口（Repository）
- 基础设施层接口（Logger, EventBus, ConfigManager）

**示例：**

```python
# ✅ 正确：业务逻辑层调用仓储
class TextureManagerService(ITextureManagerService):
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失贴图"""
        # 调用仓储
        files = self._file_repo.search_files(search_path, options)
        # 业务逻辑
        matched = self._match_textures(files)
        return matched

# ❌ 错误：业务逻辑层直接调用Maya API
class TextureManagerService(ITextureManagerService):
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失贴图"""
        # 直接调用Maya API（违反边界）
        import maya.cmds as cmds
        nodes = cmds.ls(type='file')
        # ...
```

#### 3.4.3 数据访问层边界

**职责：**
- 数据持久化
- Maya API封装
- 文件系统操作

**不应包含：**
- 业务逻辑
- UI相关代码

**依赖：**
- 基础设施层接口（Logger）

**示例：**

```python
# ✅ 正确：数据访问层封装Maya API
class NodeDataRepository(INodeDataRepository):
    def get_all_nodes(self, node_types: List[str]) -> List[str]:
        """获取指定类型的所有节点"""
        import maya.cmds as cmds
        nodes = []
        for node_type in node_types:
            nodes.extend(cmds.ls(type=node_type))
        return nodes

# ❌ 错误：数据访问层包含业务逻辑
class NodeDataRepository(INodeDataRepository):
    def get_all_nodes(self, node_types: List[str]) -> List[str]:
        """获取指定类型的所有节点"""
        import maya.cmds as cmds
        nodes = []
        for node_type in node_types:
            # 业务逻辑：过滤特定节点（违反边界）
            node_list = cmds.ls(type=node_type)
            nodes.extend([n for n in node_list if not n.startswith('temp_')])
        return nodes
```

---

## 4. 实施步骤

### 4.1 阶段划分

#### 阶段一：基础设施搭建（2-3周）

**目标：** 建立核心基础设施，为后续重构提供支撑

**任务清单：**

1. **创建核心模块结构**
   - 创建 `core/` 目录
   - 创建 `config/` 目录
   - 创建 `data/` 目录
   - 创建 `services/` 目录
   - 创建 `ui/` 目录
   - 创建 `tests/` 目录

2. **实现IConfigManager和ConfigManager**
   - 定义IConfigManager接口
   - 实现ConfigManager类
   - 编写单元测试
   - 迁移现有配置加载逻辑

3. **实现ILogger和ConsoleLogger**
   - 定义ILogger接口
   - 实现ConsoleLogger类
   - 集成Python logging模块
   - 编写单元测试
   - 替换现有的FeedbackPrompt

4. **实现IEventBus和EventBus**
   - 定义IEventBus接口
   - 实现EventBus类
   - 支持同步和异步事件
   - 编写单元测试

5. **创建DIContainer**
   - 实现DIContainer类
   - 支持单例和瞬态服务
   - 支持自动依赖解析
   - 编写单元测试

6. **实现IConfigRepository和ConfigRepository**
   - 定义IConfigRepository接口
   - 实现ConfigRepository类
   - 封装msgpack配置读写
   - 编写单元测试

7. **迁移全局变量到ConfigManager**
   - 识别所有全局变量
   - 创建配置文件结构
   - 迁移全局变量到配置
   - 更新所有引用

8. **编写集成测试**
   - 测试核心模块集成
   - 测试配置管理流程
   - 测试事件发布订阅

**验收标准：**
- [ ] 所有核心接口定义完成
- [ ] 核心服务实现完成并通过测试
- [ ] 全局变量迁移完成
- [ ] 依赖注入容器正常工作
- [ ] 测试覆盖率达到80%+

**风险：**
- 全局变量迁移可能影响所有模块
- 配置结构设计不当可能导致后续重构

**应对措施：**
- 分阶段迁移，每阶段充分测试
- 保持向后兼容，使用特性开关
- 建立配置验证机制

#### 阶段二：数据访问层重构（2-3周）

**目标：** 封装数据访问逻辑，提供统一的数据访问接口

**任务清单：**

1. **实现INodeDataRepository和NodeDataRepository**
   - 定义INodeDataRepository接口
   - 实现NodeDataRepository类
   - 封装Maya cmds调用
   - 编写单元测试

2. **实现IFileSystemRepository和FileSystemRepository**
   - 定义IFileSystemRepository接口
   - 实现FileSystemRepository类
   - 封装文件系统操作
   - 编写单元测试

3. **重构GetNodeData类**
   - 将GetNodeData转换为Repository模式
   - 使用INodeDataRepository接口
   - 保持向后兼容
   - 编写单元测试

4. **重构PathDetection类**
   - 将PathDetection转换为Repository模式
   - 使用IFileSystemRepository接口
   - 保持向后兼容
   - 编写单元测试

5. **迁移所有Maya API调用**
   - 识别所有Maya cmds调用
   - 迁移到Repository层
   - 更新所有引用
   - 编写集成测试

6. **编写集成测试**
   - 测试Repository与Maya集成
   - 测试数据访问流程
   - 测试异常处理

**验收标准：**
- [ ] 所有数据访问接口定义完成
- [ ] Repository实现完成并通过测试
- [ ] Maya API调用完全封装
- [ ] 数据访问逻辑与业务逻辑分离
- [ ] 测试覆盖率达到80%+

**风险：**
- Maya API封装不完整
- Repository设计不当影响性能

**应对措施：**
- 逐步迁移，保持原有功能
- 性能测试，确保无性能退化
- 充分的单元测试和集成测试

#### 阶段三：服务层重构（4-6周）

**目标：** 将业务逻辑从UI层分离，创建独立的服务层

**任务清单：**

1. **实现ITextureManagerService和TextureManagerService**
   - 定义ITextureManagerService接口
   - 实现TextureManagerService类
   - 从TextureManagerWin提取业务逻辑
   - 编写单元测试

2. **实现INodeConnectionService和NodeConnectionService**
   - 定义INodeConnectionService接口
   - 实现NodeConnectionService类
   - 从Magic_Node_Connection提取业务逻辑
   - 编写单元测试

3. **实现IPathDetectionService和PathDetectionService**
   - 定义IPathDetectionService接口
   - 实现PathDetectionService类
   - 从Path_Detection_Connection提取业务逻辑
   - 编写单元测试

4. **实现IRenderPresetService和RenderPresetService**
   - 定义IRenderPresetService接口
   - 实现RenderPresetService类
   - 从rendering_preset_menu提取业务逻辑
   - 编写单元测试

5. **实现IMaterialRepairService和MaterialRepairService**
   - 定义IMaterialRepairService接口
   - 实现MaterialRepairService类
   - 从IntelligentMaterialRepair提取业务逻辑
   - 编写单元测试

6. **重构TextureManagerWin**
   - 使用TextureManagerService
   - 移除业务逻辑
   - 保持UI不变
   - 编写UI测试

7. **重构Magic_Node_Connection**
   - 使用NodeConnectionService
   - 移除业务逻辑
   - 保持功能不变
   - 编写UI测试

8. **重构Path_Detection_Connection**
   - 使用PathDetectionService
   - 移除业务逻辑
   - 保持功能不变
   - 编写UI测试

9. **重构rendering_preset_menu**
   - 使用RenderPresetService
   - 移除业务逻辑
   - 保持功能不变
   - 编写UI测试

10. **编写集成测试**
    - 测试Service与Repository集成
    - 测试Service与UI集成
    - 测试端到端流程

**验收标准：**
- [ ] 所有服务接口定义完成
- [ ] 服务实现完成并通过测试
- [ ] UI层不再包含业务逻辑
- [ ] 服务可独立测试
- [ ] 测试覆盖率达到80%+

**风险：**
- 业务逻辑提取不完整
- 服务设计不当导致性能问题
- UI重构影响用户体验

**应对措施：**
- 充分的单元测试和集成测试
- 性能测试，确保无性能退化
- 保持UI完全不变，只重构内部逻辑

#### 阶段四：UI层重构（3-4周）

**目标：** 重构UI层，使用依赖注入，简化UI逻辑

**任务清单：**

1. **重构Arnold_Magic_Node_UI**
   - 使用依赖注入
   - 移除硬编码
   - 使用事件驱动更新
   - 编写UI测试

2. **重构ArnoldMagicNodeSettingsPanel**
   - 使用依赖注入
   - 移除硬编码
   - 使用事件驱动更新
   - 编写UI测试

3. **重构TextureManagerWin**
   - 使用依赖注入
   - 移除硬编码
   - 使用事件驱动更新
   - 编写UI测试

4. **重构AOVLightGroupManager**
   - 使用依赖注入
   - 移除硬编码
   - 使用事件驱动更新
   - 编写UI测试

5. **实现事件驱动的UI更新机制**
   - 定义UI事件
   - 实现事件订阅
   - 实现UI更新逻辑
   - 编写测试

6. **移除UI层中的硬编码**
   - 识别所有硬编码
   - 迁移到配置
   - 更新所有引用
   - 编写测试

7. **编写UI测试**
   - 测试UI交互
   - 测试UI更新
   - 测试事件处理

**验收标准：**
- [ ] 所有UI类使用依赖注入
- [ ] UI层不再直接实例化业务逻辑类
- [ ] UI层不再包含业务逻辑
- [ ] 事件驱动机制正常工作
- [ ] 测试覆盖率达到70%+

**风险：**
- UI重构影响用户体验
- 事件驱动机制设计不当
- 依赖注入配置复杂

**应对措施：**
- 保持UI完全不变，只重构内部逻辑
- 充分的UI测试
- 简化依赖注入配置

#### 阶段五：模块化拆分（2-3周）

**目标：** 将代码拆分为独立的模块，实现模块独立开发、测试、部署

**任务清单：**

1. **创建模块目录结构**
   - 创建 `core/` 模块
   - 创建 `config/` 模块
   - 创建 `data/` 模块
   - 创建 `services/texture_manager/` 模块
   - 创建 `services/node_connection/` 模块
   - 创建 `services/path_detection/` 模块
   - 创建 `services/render_preset/` 模块
   - 创建 `services/material_repair/` 模块
   - 创建 `ui/` 模块

2. **将核心模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

3. **将配置模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

4. **将数据访问模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

5. **将贴图管理模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

6. **将节点连接模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

7. **将路径检测模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

8. **将渲染预设模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

9. **将材质修复模块拆分为独立包**
   - 创建 `__init__.py`
   - 导出公共接口
   - 编写模块文档
   - 编写模块测试

10. **将UI模块拆分为独立包**
    - 创建 `__init__.py`
    - 导出公共接口
    - 编写模块文档
    - 编写模块测试

11. **创建模块配置文件**
    - 创建 `module_config.py`
    - 定义模块依赖
    - 定义模块导出
    - 编写配置验证

12. **编写模块集成测试**
    - 测试模块间依赖
    - 测试模块导出
    - 测试模块加载

**验收标准：**
- [ ] 所有模块独立可运行
- [ ] 模块间依赖清晰
- [ ] 模块可独立测试
- [ ] 模块可独立部署
- [ ] 测试覆盖率达到80%+

**风险：**
- 模块拆分不完整
- 模块依赖循环
- 模块加载失败

**应对措施：**
- 充分的模块测试
- 使用依赖检查工具
- 建立模块加载验证

#### 阶段六：优化与完善（2-3周）

**目标：** 优化性能，完善文档，准备发布

**任务清单：**

1. **性能优化**
   - 识别性能瓶颈
   - 优化关键路径
   - 优化内存使用
   - 编写性能测试

2. **错误处理完善**
   - 统一错误处理机制
   - 完善错误信息
   - 添加错误恢复逻辑
   - 编写错误处理测试

3. **日志记录完善**
   - 完善日志记录
   - 添加性能日志
   - 添加错误日志
   - 编写日志测试

4. **文档编写**
   - 编写架构文档
   - 编写API文档
   - 编写用户手册
   - 编写开发指南

5. **示例代码编写**
   - 编写使用示例
   - 编写扩展示例
   - 编写测试示例

6. **用户手册编写**
   - 编写安装指南
   - 编写使用指南
   - 编写常见问题
   - 编写故障排除

7. **开发者文档编写**
   - 编写架构设计文档
   - 编写模块设计文档
   - 编写接口设计文档
   - 编写开发指南

8. **发布准备**
   - 版本号更新
   - 更新日志编写
   - 发布说明编写
   - 打包发布

**验收标准：**
- [ ] 性能达标
- [ ] 错误处理完善
- [ ] 日志记录完善
- [ ] 文档完整
- [ ] 可以发布

**风险：**
- 性能优化效果不明显
- 文档不完整
- 发布流程问题

**应对措施：**
- 充分的性能测试
- 文档审查
- 发布流程测试

### 4.2 实施优先级

**P0级（立即处理）：**
1. 创建核心模块结构
2. 实现IConfigManager和ConfigManager
3. 实现ILogger和ConsoleLogger
4. 创建DIContainer
5. 迁移全局变量

**P1级（近期处理）：**
1. 实现Repository层
2. 封装Maya API调用
3. 实现Service层接口
4. 从UI层分离业务逻辑

**P2级（中期处理）：**
1. UI层重构
2. 实现事件驱动机制
3. 移除硬编码

**P3级（长期规划）：**
1. 模块化拆分
2. 性能优化
3. 文档编写

### 4.3 实施时间表

| 阶段 | 任务 | 开始时间 | 结束时间 | 负责人 | 状态 |
|-----|------|---------|---------|-------|------|
| 阶段一 | 基础设施搭建 | Week 1 | Week 3 | TBD | 待开始 |
| 阶段二 | 数据访问层重构 | Week 4 | Week 6 | TBD | 待开始 |
| 阶段三 | 服务层重构 | Week 7 | Week 12 | TBD | 待开始 |
| 阶段四 | UI层重构 | Week 13 | Week 16 | TBD | 待开始 |
| 阶段五 | 模块化拆分 | Week 17 | Week 19 | TBD | 待开始 |
| 阶段六 | 优化与完善 | Week 20 | Week 22 | TBD | 待开始 |

---

## 5. 关键代码变更说明

### 5.1 全局变量迁移

#### 5.1.1 迁移前

**Arnold_Magic_Node.py**

```python
# 全局变量
script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))
datas_path = os.path.normpath(os.path.join(script_path, "Datas"))
settings_path = os.path.normpath(os.path.join(datas_path, "settings"))
icon_path = os.path.normpath(os.path.join(script_path, "icon"))
render_preset_path = os.path.normpath(os.path.join(datas_path, "render_presets"))

AMS_Config = "Arnold_Magic_Settings.bin"

# 使用全局变量
def some_function():
    config_path = os.path.join(settings_path, AMS_Config)
    # ...
```

#### 5.1.2 迁移后

**core/config_manager.py**

```python
class ConfigManager(IConfigManager):
    """配置管理器"""
    
    def __init__(self, config_repository: IConfigRepository):
        self._repo = config_repository
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置"""
        self._config = self._repo.load_config(self._get_config_path())
    
    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        script_path = os.path.dirname(os.path.abspath(__file__))
        datas_path = os.path.join(script_path, '..', 'Datas')
        settings_path = os.path.join(datas_path, 'settings')
        return os.path.join(settings_path, 'Arnold_Magic_Settings.bin')
```

**使用配置管理器**

```python
class SomeService:
    def __init__(self, config_manager: IConfigManager):
        self._config = config_manager
    
    def some_function(self):
        config_path = self._config.get('paths.settings_path')
        # ...
```

#### 5.1.3 变更说明

**变更类型：** 重构  
**影响范围：** 所有使用全局变量的模块  
**向后兼容：** 是（通过特性开关）  
**测试要求：** 单元测试、集成测试

**变更原因：**
- 消除全局变量污染
- 提高可测试性
- 支持配置热重载

**注意事项：**
- 需要识别所有全局变量的使用位置
- 需要确保配置结构合理
- 需要保持向后兼容

### 5.2 UI与业务逻辑分离

#### 5.2.1 分离前

**Arnold_Magic_Node.py - TextureManagerWin**

```python
class TextureManagerWin(QtWidgets.QDialog):
    def __init__(self):
        super(TextureManagerWin, self).__init__()
        
        # 直接实例化业务逻辑类
        self.getnodedata = GetNodeData()
        self.dataM = DataManager()
        self.feedback = FeedbackPrompt()
        self.pathD = PathDetection()
        self.dataP = DataProcessor()
        self.imageP = ImageProcessor()
        
        # UI初始化
        self.setup_ui()
        
        # 加载数据
        self.load_texture_data()
    
    def load_texture_data(self):
        """加载贴图数据"""
        # 直接调用业务逻辑
        self.MterialNodeAllInfoDict = self.getnodedata.GetMterialNodeAllInfo()
        self.update_table()
    
    def fix_missing_textures(self):
        """修复缺失贴图"""
        # 直接调用业务逻辑
        missing_textures = self.get_missing_textures()
        search_path = self.get_search_path()
        
        # 复杂的业务逻辑
        dir_files = self.pathD.detection_path_content(
            search_path,
            exclude_list=self.get_exclude_list()
        )
        
        matched = self.pathD.calculate_similarity(
            missing_textures,
            dir_files,
            self.get_weights()
        )
        
        # 更新节点路径
        for texture, new_path in matched.items():
            cmds.setAttr(texture + '.fileTextureName', new_path)
        
        # 重新加载数据
        self.load_texture_data()
```

#### 5.2.2 分离后

**services/texture_manager/texture_manager_service.py**

```python
class TextureManagerService(ITextureManagerService):
    """贴图管理服务"""
    
    def __init__(
        self,
        config_manager: IConfigManager,
        logger: ILogger,
        node_data_repo: INodeDataRepository,
        file_system_repo: IFileSystemRepository,
        event_bus: IEventBus
    ):
        self._config = config_manager
        self._logger = logger
        self._node_repo = node_data_repo
        self._file_repo = file_system_repo
        self._event_bus = event_bus
    
    def get_all_textures(self) -> Dict[str, Any]:
        """获取所有贴图信息"""
        return self._node_repo.get_all_textures()
    
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失贴图"""
        self._logger.info("开始修复缺失贴图", search_path=search_path)
        
        # 获取缺失贴图
        all_textures = self.get_all_textures()
        missing_textures = self._filter_missing_textures(all_textures)
        
        # 搜索文件
        dir_files = self._file_repo.search_files(
            search_path,
            exclude_list=options.get('exclude_list', []),
            extensions=options.get('extensions', None)
        )
        
        # 匹配贴图
        matched = self._match_textures(missing_textures, dir_files, options)
        
        # 更新节点路径
        fixed_count = 0
        failed_count = 0
        for texture, new_path in matched.items():
            try:
                self._node_repo.set_texture_path(texture, new_path)
                fixed_count += 1
            except Exception as e:
                self._logger.error(f"修复贴图失败: {texture}", error=str(e))
                failed_count += 1
        
        # 发布事件
        self._event_bus.publish('textures.fixed', {
            'fixed_count': fixed_count,
            'failed_count': failed_count
        })
        
        return {
            'fixed_count': fixed_count,
            'failed_count': failed_count,
            'matched': matched
        }
```

**ui/texture_manager_window.py**

```python
class TextureManagerWindow(QtWidgets.QDialog):
    """贴图管理器窗口"""
    
    def __init__(self, texture_service: ITextureManagerService, event_bus: IEventBus):
        super(TextureManagerWindow, self).__init__()
        
        # 依赖注入
        self._texture_service = texture_service
        self._event_bus = event_bus
        
        # UI初始化
        self.setup_ui()
        
        # 订阅事件
        self._event_bus.subscribe('textures.fixed', self._on_textures_fixed)
        
        # 加载数据
        self.load_texture_data()
    
    def load_texture_data(self):
        """加载贴图数据"""
        # 调用服务层
        self.MterialNodeAllInfoDict = self._texture_service.get_all_textures()
        self.update_table()
    
    def fix_missing_textures(self):
        """修复缺失贴图"""
        # 获取参数
        search_path = self.get_search_path()
        options = {
            'exclude_list': self.get_exclude_list(),
            'extensions': self.get_extensions(),
            'weights': self.get_weights()
        }
        
        # 调用服务层
        result = self._texture_service.fix_missing_textures(search_path, options)
        
        # 显示结果
        self.show_result(result)
    
    def _on_textures_fixed(self, data: Dict[str, Any]):
        """贴图修复完成回调"""
        self.show_result(data)
        self.load_texture_data()
```

#### 5.2.3 变更说明

**变更类型：** 重构  
**影响范围：** TextureManagerWin, TextureManagerService  
**向后兼容：** 是（UI界面完全不变）  
**测试要求：** 单元测试、集成测试、UI测试

**变更原因：**
- 分离UI与业务逻辑
- 提高可测试性
- 支持业务逻辑复用

**注意事项：**
- 保持UI界面完全不变
- 确保业务逻辑完整迁移
- 充分的测试覆盖

### 5.3 依赖注入实现

#### 5.3.1 实现前

**Arnold_Magic_Node.py**

```python
class Arnold_Magic_Node_UI:
    def __init__(self):
        # 直接实例化
        self.dataM = DataManager()
        self.feedback = FeedbackPrompt()
        self.getnodedata = GetNodeData()
        self.language = language_loading()['ArnoldMagicNode']['AMDUI_WIN']
        self.config = self.dataM.bin_load_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config)))
```

#### 5.3.2 实现后

**core/di_container.py**

```python
class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_singleton(self, interface: type, implementation: type) -> None:
        """注册单例服务"""
        interface_name = interface.__name__
        self._factories[interface_name] = implementation
    
    def register_transient(self, interface: type, implementation: type) -> None:
        """注册瞬态服务"""
        interface_name = interface.__name__
        self._services[interface_name] = implementation
    
    def resolve(self, interface: type) -> Any:
        """解析服务"""
        interface_name = interface.__name__
        
        # 检查是否为单例
        if interface_name in self._factories:
            if interface_name not in self._singletons:
                self._singletons[interface_name] = self._create_instance(
                    self._factories[interface_name]
                )
            return self._singletons[interface_name]
        
        # 检查是否为瞬态
        if interface_name in self._services:
            return self._create_instance(self._services[interface_name])
        
        raise ValueError(f"Service {interface_name} not registered")
    
    def _create_instance(self, implementation: type) -> Any:
        """创建实例"""
        import inspect
        constructor = implementation.__init__
        params = inspect.signature(constructor).parameters
        
        kwargs = {}
        for param_name, param in params.items():
            if param_name == 'self':
                continue
            
            # 尝试从容器中解析依赖
            param_type = param.annotation
            if param_type and param_type != inspect.Parameter.empty:
                kwargs[param_name] = self.resolve(param_type)
        
        return implementation(**kwargs)
```

**配置服务**

```python
def configure_services() -> DIContainer:
    """配置服务"""
    container = DIContainer()
    
    # 注册核心服务（单例）
    container.register_singleton(ILogger, ConsoleLogger)
    container.register_singleton(IEventBus, EventBus)
    container.register_singleton(IConfigManager, ConfigManager)
    
    # 注册仓储（单例）
    container.register_singleton(IConfigRepository, ConfigRepository)
    container.register_singleton(INodeDataRepository, NodeDataRepository)
    container.register_singleton(IFileSystemRepository, FileSystemRepository)
    
    # 注册服务（瞬态）
    container.register_transient(ITextureManagerService, TextureManagerService)
    container.register_transient(INodeConnectionService, NodeConnectionService)
    container.register_transient(IPathDetectionService, PathDetectionService)
    container.register_transient(IRenderPresetService, RenderPresetService)
    container.register_transient(IMaterialRepairService, MaterialRepairService)
    
    return container
```

**使用依赖注入**

```python
class Arnold_Magic_Node_UI:
    def __init__(self, container: DIContainer):
        # 从容器解析依赖
        self._config = container.resolve(IConfigManager)
        self._logger = container.resolve(ILogger)
        self._event_bus = container.resolve(IEventBus)
        
        # 加载语言
        self.language = self._config.get_nested(['language', 'ArnoldMagicNode', 'AMDUI_WIN'])
```

#### 5.3.3 变更说明

**变更类型：** 重构  
**影响范围：** 所有UI类和Service类  
**向后兼容：** 是（通过特性开关）  
**测试要求：** 单元测试、集成测试

**变更原因：**
- 解耦模块间依赖
- 提高可测试性
- 支持依赖替换

**注意事项：**
- 需要识别所有依赖关系
- 需要合理设计服务生命周期
- 需要避免循环依赖

### 5.4 事件驱动实现

#### 5.4.1 实现前

**Arnold_Magic_Node.py**

```python
class TextureManagerWin(QtWidgets.QDialog):
    def fix_missing_textures(self):
        """修复缺失贴图"""
        # 执行修复
        result = self.do_fix()
        
        # 直接更新UI
        self.update_result(result)
        self.load_texture_data()
```

#### 5.4.2 实现后

**core/event_bus.py**

```python
class EventBus(IEventBus):
    """事件总线"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._callback_id_counter = 0
        self._callback_ids: Dict[str, Callable] = {}
    
    def subscribe(self, event_name: str, callback: Callable) -> str:
        """订阅事件"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        callback_id = f"{event_name}_{self._callback_id_counter}"
        self._callback_id_counter += 1
        
        self._subscribers[event_name].append(callback)
        self._callback_ids[callback_id] = callback
        
        return callback_id
    
    def unsubscribe(self, event_name: str, callback_id: str) -> bool:
        """取消订阅"""
        if event_name not in self._subscribers:
            return False
        
        callback = self._callback_ids.get(callback_id)
        if callback and callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)
            del self._callback_ids[callback_id]
            return True
        
        return False
    
    def publish(self, event_name: str, data: Any = None) -> None:
        """发布事件"""
        if event_name not in self._subscribers:
            return
        
        for callback in self._subscribers[event_name]:
            try:
                callback(data)
            except Exception as e:
                print(f"事件处理失败: {event_name}, 错误: {e}")
    
    def clear(self, event_name: Optional[str] = None) -> None:
        """清除事件订阅"""
        if event_name:
            if event_name in self._subscribers:
                del self._subscribers[event_name]
        else:
            self._subscribers.clear()
```

**使用事件驱动**

```python
class TextureManagerService(ITextureManagerService):
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失贴图"""
        # 执行修复
        result = self._do_fix(search_path, options)
        
        # 发布事件
        self._event_bus.publish('textures.fixed', result)
        
        return result

class TextureManagerWindow(QtWidgets.QDialog):
    def __init__(self, texture_service: ITextureManagerService, event_bus: IEventBus):
        super(TextureManagerWindow, self).__init__()
        
        self._texture_service = texture_service
        self._event_bus = event_bus
        
        # 订阅事件
        self._event_bus.subscribe('textures.fixed', self._on_textures_fixed)
    
    def fix_missing_textures(self):
        """修复缺失贴图"""
        # 调用服务
        self._texture_service.fix_missing_textures(
            self.get_search_path(),
            self.get_options()
        )
    
    def _on_textures_fixed(self, data: Dict[str, Any]):
        """贴图修复完成回调"""
        # 更新UI
        self.update_result(data)
        self.load_texture_data()
```

#### 5.4.3 变更说明

**变更类型：** 重构  
**影响范围：** Service层和UI层  
**向后兼容：** 是（UI界面完全不变）  
**测试要求：** 单元测试、集成测试

**变更原因：**
- 解耦模块间通信
- 支持异步处理
- 提高可扩展性

**注意事项：**
- 需要合理设计事件
- 需要处理事件异常
- 需要避免内存泄漏

---

## 6. 测试策略及验证方法

### 6.1 测试金字塔

```
        /\
       /  \      E2E Tests (5%)
      /____\     端到端测试
     /      \
    /        \   Integration Tests (25%)
   /__________\  集成测试
  /            \
 /              \ Unit Tests (70%)
/________________\ 单元测试
```

### 6.2 单元测试

#### 6.2.1 测试框架

**选择：** pytest + pytest-mock + pytest-cov

**安装：**
```bash
pip install pytest pytest-mock pytest-cov
```

#### 6.2.2 测试示例

**ConfigManager测试**

```python
import pytest
from unittest.mock import Mock, patch

class TestConfigManager:
    """配置管理器测试"""
    
    @pytest.fixture
    def config_repo(self):
        """创建配置仓储mock"""
        return Mock()
    
    @pytest.fixture
    def config_manager(self, config_repo):
        """创建配置管理器"""
        from core.config_manager import ConfigManager
        return ConfigManager(config_repo)
    
    def test_get_config_value(self, config_manager, config_repo):
        """测试获取配置值"""
        # 设置mock返回值
        config_repo.load_config.return_value = {"key": "value"}
        
        # 重新加载配置
        config_manager.reload()
        
        # 测试获取配置值
        result = config_manager.get("key")
        
        # 验证结果
        assert result == "value"
        config_repo.load_config.assert_called_once()
    
    def test_set_config_value(self, config_manager, config_repo):
        """测试设置配置值"""
        # 设置配置值
        config_manager.set("key", "value")
        
        # 验证保存被调用
        config_repo.save_config.assert_called_once()
    
    def test_get_nested_config(self, config_manager, config_repo):
        """测试获取嵌套配置"""
        # 设置mock返回值
        config_repo.load_config.return_value = {
            "level1": {
                "level2": {
                    "key": "value"
                }
            }
        }
        
        # 重新加载配置
        config_manager.reload()
        
        # 测试获取嵌套配置
        result = config_manager.get_nested(["level1", "level2", "key"])
        
        # 验证结果
        assert result == "value"
    
    def test_get_nested_config_default(self, config_manager, config_repo):
        """测试获取嵌套配置（默认值）"""
        # 设置mock返回值
        config_repo.load_config.return_value = {"level1": {}}
        
        # 重新加载配置
        config_manager.reload()
        
        # 测试获取嵌套配置（使用默认值）
        result = config_manager.get_nested(["level1", "level2", "key"], default="default")
        
        # 验证结果
        assert result == "default"
```

**TextureManagerService测试**

```python
import pytest
from unittest.mock import Mock, patch

class TestTextureManagerService:
    """贴图管理服务测试"""
    
    @pytest.fixture
    def container(self):
        """创建依赖注入容器"""
        from core.di_container import DIContainer
        container = DIContainer()
        
        # 注册mock服务
        container.register_singleton(IConfigManager, Mock())
        container.register_singleton(ILogger, Mock())
        container.register_singleton(IEventBus, Mock())
        container.register_singleton(INodeDataRepository, Mock())
        container.register_singleton(IFileSystemRepository, Mock())
        
        return container
    
    @pytest.fixture
    def service(self, container):
        """创建服务实例"""
        from services.texture_manager.texture_manager_service import TextureManagerService
        return TextureManagerService(
            container.resolve(IConfigManager),
            container.resolve(ILogger),
            container.resolve(INodeDataRepository),
            container.resolve(IFileSystemRepository),
            container.resolve(IEventBus)
        )
    
    def test_get_all_textures(self, service, container):
        """测试获取所有贴图"""
        # 设置mock返回值
        node_repo = container.resolve(INodeDataRepository)
        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/path/to/texture1.jpg"}
            }
        }
        
        # 测试获取所有贴图
        result = service.get_all_textures()
        
        # 验证结果
        assert "material1" in result
        assert "texture1" in result["material1"]
        node_repo.get_all_textures.assert_called_once()
    
    def test_fix_missing_textures(self, service, container):
        """测试修复缺失贴图"""
        # 设置mock返回值
        node_repo = container.resolve(INodeDataRepository)
        file_repo = container.resolve(IFileSystemRepository)
        
        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/old/path/to/texture1.jpg", "isLoaded": False}
            }
        }
        
        file_repo.search_files.return_value = {
            "texture1.jpg": "/new/path/to/texture1.jpg"
        }
        
        # 测试修复缺失贴图
        result = service.fix_missing_textures(
            "/search/path",
            {"exclude_list": [], "extensions": None}
        )
        
        # 验证结果
        assert result["fixed_count"] == 1
        assert result["failed_count"] == 0
        node_repo.set_texture_path.assert_called_once()
    
    def test_fix_missing_textures_with_error(self, service, container):
        """测试修复缺失贴图（带错误）"""
        # 设置mock返回值
        node_repo = container.resolve(INodeDataRepository)
        file_repo = container.resolve(IFileSystemRepository)
        
        node_repo.get_all_textures.return_value = {
            "material1": {
                "texture1": {"Path": "/old/path/to/texture1.jpg", "isLoaded": False}
            }
        }
        
        file_repo.search_files.return_value = {
            "texture1.jpg": "/new/path/to/texture1.jpg"
        }
        
        # 设置mock抛出异常
        node_repo.set_texture_path.side_effect = Exception("设置失败")
        
        # 测试修复缺失贴图
        result = service.fix_missing_textures(
            "/search/path",
            {"exclude_list": [], "extensions": None}
        )
        
        # 验证结果
        assert result["fixed_count"] == 0
        assert result["failed_count"] == 1
```

#### 6.2.3 测试覆盖率

**目标：**
- 核心模块：90%+
- 服务层：85%+
- UI层：70%+
- 整体：80%+

**运行测试：**
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/core/

# 生成覆盖率报告
pytest --cov=arnold_magic_node --cov-report=html --cov-report=term
```

### 6.3 集成测试

#### 6.3.1 测试目标

验证模块间的协作是否正常

#### 6.3.2 测试示例

**贴图管理器集成测试**

```python
import pytest

class TestTextureManagerIntegration:
    """贴图管理器集成测试"""
    
    @pytest.fixture
    def container(self):
        """创建依赖注入容器"""
        from core.di_container import DIContainer
        from core.config_manager import ConfigManager
        from core.logger import ConsoleLogger
        from core.event_bus import EventBus
        from config.config_repository import ConfigRepository
        from data.node_data_repository import NodeDataRepository
        from data.file_system_repository import FileSystemRepository
        from services.texture_manager.texture_manager_service import TextureManagerService
        
        container = DIContainer()
        
        # 注册核心服务
        container.register_singleton(ILogger, ConsoleLogger)
        container.register_singleton(IEventBus, EventBus)
        container.register_singleton(IConfigManager, ConfigManager)
        container.register_singleton(IConfigRepository, ConfigRepository)
        
        # 注册仓储
        container.register_singleton(INodeDataRepository, NodeDataRepository)
        container.register_singleton(IFileSystemRepository, FileSystemRepository)
        
        # 注册服务
        container.register_transient(ITextureManagerService, TextureManagerService)
        
        return container
    
    def test_texture_manager_workflow(self, container):
        """测试贴图管理器完整工作流"""
        # 获取服务
        texture_service = container.resolve(ITextureManagerService)
        node_service = container.resolve(INodeConnectionService)
        
        # 1. 获取所有贴图
        textures = texture_service.get_all_textures()
        assert len(textures) > 0
        
        # 2. 过滤缺失贴图
        missing = texture_service.filter_textures({"isLoaded": False})
        assert len(missing) >= 0
        
        # 3. 修复缺失贴图
        if missing:
            result = texture_service.fix_missing_textures(
                "/search/path",
                {"exclude_list": [], "extensions": None}
            )
            assert result["fixed_count"] >= 0
        
        # 4. 连接节点
        for material_name, texture_data in textures.items():
            texture_nodes = list(texture_data.keys())
            node_service.auto_connect_nodes(
                material_name,
                texture_nodes,
                {}
            )
```

### 6.4 端到端测试

#### 6.4.1 测试目标

验证完整用户场景

#### 6.4.2 测试示例

**贴图管理器端到端测试**

```python
import pytest
import maya.cmds as cmds

class TestE2E:
    """端到端测试"""
    
    @pytest.fixture
    def ui(self):
        """创建UI实例"""
        from ui.main_window import Arnold_Magic_Node_UI
        from core.di_container import DIContainer
        container = configure_services()
        return Arnold_Magic_Node_UI(container)
    
    def test_texture_manager_complete_workflow(self, ui):
        """测试贴图管理器完整工作流"""
        # 1. 启动插件
        ui.show()
        
        # 2. 打开贴图管理器
        tm_win = ui.open_texture_manager()
        assert tm_win is not None
        
        # 3. 加载贴图数据
        tm_win.load_texture_data()
        assert len(tm_win.MterialNodeAllInfoDict) > 0
        
        # 4. 筛选缺失贴图
        tm_win.filter_missing_textures()
        missing_count = tm_win.get_missing_count()
        assert missing_count >= 0
        
        # 5. 修复缺失贴图
        if missing_count > 0:
            tm_win.fix_missing_textures("/test/path")
            assert tm_win.get_missing_count() == 0
        
        # 6. 验证Maya场景
        materials = cmds.ls(type='aiStandardSurface')
        assert len(materials) > 0
```

### 6.5 性能测试

#### 6.5.1 测试目标

验证性能指标是否达标

#### 6.5.2 测试示例

```python
import time
import pytest

class TestPerformance:
    """性能测试"""
    
    def test_load_texture_data_performance(self, container):
        """测试加载贴图数据性能"""
        texture_service = container.resolve(ITextureManagerService)
        
        start_time = time.time()
        texture_service.get_all_textures()
        end_time = time.time()
        
        assert end_time - start_time < 5.0  # 5秒内完成
    
    def test_fix_missing_textures_performance(self, container):
        """测试修复缺失贴图性能"""
        texture_service = container.resolve(ITextureManagerService)
        
        start_time = time.time()
        texture_service.fix_missing_textures(
            "/search/path",
            {"exclude_list": [], "extensions": None}
        )
        end_time = time.time()
        
        assert end_time - start_time < 10.0  # 10秒内完成
```

### 6.6 测试验收标准

**单元测试：**
- [ ] 所有核心模块测试通过
- [ ] 所有服务模块测试通过
- [ ] 测试覆盖率达到80%+

**集成测试：**
- [ ] 所有模块集成测试通过
- [ ] 事件驱动机制正常工作
- [ ] 依赖注入容器正常工作

**端到端测试：**
- [ ] 所有用户场景测试通过
- [ ] UI界面完全不变
- [ ] 功能完全正常

**性能测试：**
- [ ] 所有性能指标达标
- [ ] 无性能退化
- [ ] 内存使用正常

---

## 7. 解耦前后代码对比分析

### 7.1 架构对比

#### 7.1.1 解耦前

```
Arnold_Magic_Node.py (9500+ 行)
├── Arnold_Magic_Node_UI (主窗口)
├── ArnoldMagicNodeSettingsPanel (设置面板)
├── TextureManagerWin (贴图管理器)
├── AOVLightGroupManager (AOV管理器)
├── TM_FindAndReplace (查找替换)
├── TM_RepathFiles (重路径)
├── TM_ImageProcessing (图像处理)
├── TM_TexturePack (纹理打包)
├── direct_connection_button (直连按钮)
├── rendering_preset_menu (渲染预设)
├── Scene_Name_optimization (场景名称优化)
├── Path_Detection_Connection (路径检测连接)
├── Magic_Node_Connection (魔法节点连接)
├── ConvertOldMaterialsToArnold (转换旧材质)
├── IntelligentMaterialRepair (智能材质修复)
├── QuickConnectNode (快速连接)
└── SceneNameOptimization (场景名称优化)

Arnold_Magic_Node_lib.py (2277 行)
├── PathDetection (路径检测)
├── NodeProcessor (节点处理)
├── GetNodeData (获取节点数据)
├── DataProcessor (数据处理)
├── ImageProcessor (图像处理)
├── BlendNodeManager (混合节点管理)
├── FeedbackPrompt (反馈提示)
└── DataManager (数据管理)

耦合关系：
- UI类直接实例化业务逻辑类
- 全局变量被所有模块依赖
- Maya API调用分散在各处
- 配置管理混乱
```

#### 7.1.2 解耦后

```
core/ (核心模块)
├── config_manager.py (配置管理器)
├── logger.py (日志器)
├── event_bus.py (事件总线)
└── di_container.py (依赖注入容器)

config/ (配置模块)
├── config_repository.py (配置仓储)
└── config_validator.py (配置验证器)

data/ (数据访问模块)
├── node_data_repository.py (节点数据仓储)
└── file_system_repository.py (文件系统仓储)

services/ (业务逻辑模块)
├── texture_manager/
│   ├── texture_manager_service.py
│   ├── texture_path_service.py
│   └── texture_image_service.py
├── node_connection/
│   ├── node_connection_service.py
│   ├── material_service.py
│   └── udim_service.py
├── path_detection/
│   ├── path_detection_service.py
│   └── similarity_calculator.py
├── render_preset/
│   ├── render_preset_service.py
│   ├── aov_service.py
│   └── light_group_service.py
└── material_repair/
    ├── material_repair_service.py
    └── material_converter.py

ui/ (UI模块)
├── main_window.py (主窗口)
├── texture_manager_window.py (贴图管理器窗口)
├── settings_panel.py (设置面板)
└── aov_manager_window.py (AOV管理器窗口)

耦合关系：
- UI层依赖Service接口
- Service层依赖Repository接口
- Repository层依赖Core接口
- 所有依赖通过DIContainer注入
- 模块间通过EventBus通信
```

### 7.2 代码对比

#### 7.2.1 全局变量对比

**解耦前：**

```python
# Arnold_Magic_Node.py
script_path = os.path.normpath(os.path.join(os.path.dirname(__file__)))
datas_path = os.path.normpath(os.path.join(script_path, "Datas"))
settings_path = os.path.normpath(os.path.join(datas_path, "settings"))
icon_path = os.path.normpath(os.path.join(script_path, "icon"))
render_preset_path = os.path.normpath(os.path.join(datas_path, "render_presets"))

AMS_Config = "Arnold_Magic_Settings.bin"

# 使用
def some_function():
    config_path = os.path.join(settings_path, AMS_Config)
    # ...
```

**解耦后：**

```python
# core/config_manager.py
class ConfigManager(IConfigManager):
    def __init__(self, config_repository: IConfigRepository):
        self._repo = config_repository
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        script_path = os.path.dirname(os.path.abspath(__file__))
        datas_path = os.path.join(script_path, '..', 'Datas')
        settings_path = os.path.join(datas_path, 'settings')
        return self._repo.load_config(
            os.path.join(settings_path, 'Arnold_Magic_Settings.bin')
        )

# 使用
class SomeService:
    def __init__(self, config_manager: IConfigManager):
        self._config = config_manager
    
    def some_function(self):
        config_path = self._config.get('paths.settings_path')
        # ...
```

**对比分析：**
- 解耦前：全局变量污染，难以测试，难以维护
- 解耦后：配置集中管理，易于测试，易于维护

#### 7.2.2 UI与业务逻辑对比

**解耦前：**

```python
# Arnold_Magic_Node.py
class TextureManagerWin(QtWidgets.QDialog):
    def __init__(self):
        super(TextureManagerWin, self).__init__()
        
        # 直接实例化业务逻辑类
        self.getnodedata = GetNodeData()
        self.dataM = DataManager()
        self.feedback = FeedbackPrompt()
        self.pathD = PathDetection()
        
        # 加载数据
        self.load_texture_data()
    
    def load_texture_data(self):
        """加载贴图数据"""
        # 直接调用业务逻辑
        self.MterialNodeAllInfoDict = self.getnodedata.GetMterialNodeAllInfo()
        self.update_table()
    
    def fix_missing_textures(self):
        """修复缺失贴图"""
        # 直接调用业务逻辑
        missing_textures = self.get_missing_textures()
        search_path = self.get_search_path()
        
        # 复杂的业务逻辑
        dir_files = self.pathD.detection_path_content(
            search_path,
            exclude_list=self.get_exclude_list()
        )
        
        matched = self.pathD.calculate_similarity(
            missing_textures,
            dir_files,
            self.get_weights()
        )
        
        # 更新节点路径
        for texture, new_path in matched.items():
            cmds.setAttr(texture + '.fileTextureName', new_path)
        
        # 重新加载数据
        self.load_texture_data()
```

**解耦后：**

```python
# services/texture_manager/texture_manager_service.py
class TextureManagerService(ITextureManagerService):
    def __init__(
        self,
        config_manager: IConfigManager,
        logger: ILogger,
        node_data_repo: INodeDataRepository,
        file_system_repo: IFileSystemRepository,
        event_bus: IEventBus
    ):
        self._config = config_manager
        self._logger = logger
        self._node_repo = node_data_repo
        self._file_repo = file_system_repo
        self._event_bus = event_bus
    
    def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失贴图"""
        self._logger.info("开始修复缺失贴图", search_path=search_path)
        
        # 获取缺失贴图
        all_textures = self.get_all_textures()
        missing_textures = self._filter_missing_textures(all_textures)
        
        # 搜索文件
        dir_files = self._file_repo.search_files(
            search_path,
            exclude_list=options.get('exclude_list', []),
            extensions=options.get('extensions', None)
        )
        
        # 匹配贴图
        matched = self._match_textures(missing_textures, dir_files, options)
        
        # 更新节点路径
        fixed_count = 0
        failed_count = 0
        for texture, new_path in matched.items():
            try:
                self._node_repo.set_texture_path(texture, new_path)
                fixed_count += 1
            except Exception as e:
                self._logger.error(f"修复贴图失败: {texture}", error=str(e))
                failed_count += 1
        
        # 发布事件
        self._event_bus.publish('textures.fixed', {
            'fixed_count': fixed_count,
            'failed_count': failed_count
        })
        
        return {
            'fixed_count': fixed_count,
            'failed_count': failed_count,
            'matched': matched
        }

# ui/texture_manager_window.py
class TextureManagerWindow(QtWidgets.QDialog):
    def __init__(self, texture_service: ITextureManagerService, event_bus: IEventBus):
        super(TextureManagerWindow, self).__init__()
        
        # 依赖注入
        self._texture_service = texture_service
        self._event_bus = event_bus
        
        # 订阅事件
        self._event_bus.subscribe('textures.fixed', self._on_textures_fixed)
        
        # 加载数据
        self.load_texture_data()
    
    def load_texture_data(self):
        """加载贴图数据"""
        # 调用服务层
        self.MterialNodeAllInfoDict = self._texture_service.get_all_textures()
        self.update_table()
    
    def fix_missing_textures(self):
        """修复缺失贴图"""
        # 调用服务层
        result = self._texture_service.fix_missing_textures(
            self.get_search_path(),
            self.get_options()
        )
    
    def _on_textures_fixed(self, data: Dict[str, Any]):
        """贴图修复完成回调"""
        # 更新UI
        self.show_result(data)
        self.load_texture_data()
```

**对比分析：**
- 解耦前：UI包含业务逻辑，难以测试，难以复用
- 解耦后：UI只负责界面展示，业务逻辑独立，易于测试和复用

#### 7.2.3 依赖管理对比

**解耦前：**

```python
# Arnold_Magic_Node.py
class Arnold_Magic_Node_UI:
    def __init__(self):
        # 直接实例化
        self.dataM = DataManager()
        self.feedback = FeedbackPrompt()
        self.getnodedata = GetNodeData()
        self.language = language_loading()['ArnoldMagicNode']['AMDUI_WIN']
        self.config = self.dataM.bin_load_data(
            os.path.normpath(os.path.join(settings_path, AMS_Config)))
```

**解耦后：**

```python
# core/di_container.py
class DIContainer:
    def resolve(self, interface: type) -> Any:
        """解析服务"""
        # 自动解析依赖
        return self._create_instance(implementation)

# 使用依赖注入
class Arnold_Magic_Node_UI:
    def __init__(self, container: DIContainer):
        # 从容器解析依赖
        self._config = container.resolve(IConfigManager)
        self._logger = container.resolve(ILogger)
        self._event_bus = container.resolve(IEventBus)
```

**对比分析：**
- 解耦前：直接实例化，耦合度高，难以测试
- 解耦后：依赖注入，耦合度低，易于测试

### 7.3 优势对比

| 维度 | 解耦前 | 解耦后 |
|-----|-------|-------|
| **可维护性** | 低（全局变量、混合职责） | 高（清晰分层、单一职责） |
| **可测试性** | 低（难以mock、难以隔离） | 高（依赖注入、易于mock） |
| **可扩展性** | 低（修改影响范围大） | 高（接口隔离、易于扩展） |
| **可复用性** | 低（业务逻辑耦合在UI） | 高（服务独立、易于复用） |
| **协作性** | 低（职责不清、容易冲突） | 高（边界清晰、易于协作） |
| **性能** | 未知 | 无性能退化 |

---

## 8. 维护注意事项

### 8.1 代码规范

#### 8.1.1 命名规范

**类名：** PascalCase
```python
# ✅ 正确
class TextureManagerService:
    pass

# ❌ 错误
class textureManagerService:
    pass
```

**函数名：** snake_case
```python
# ✅ 正确
def get_all_textures():
    pass

# ❌ 错误
def GetAllTextures():
    pass
```

**常量：** UPPER_SNAKE_CASE
```python
# ✅ 正确
MAX_TEXTURE_SIZE = 4096

# ❌ 错误
maxTextureSize = 4096
```

**私有成员：** _leading_underscore
```python
# ✅ 正确
class TextureManagerService:
    def __init__(self):
        self._config = None
        self._logger = None

# ❌ 错误
class TextureManagerService:
    def __init__(self):
        self.config = None
        self.logger = None
```

#### 8.1.2 注释规范

**类注释：**
```python
class TextureManagerService(ITextureManagerService):
    """
    贴图管理服务
    
    职责：
    - 提供贴图管理相关业务逻辑
    - 包括贴图查询、过滤、修复、处理等功能
    
    使用场景：
    - 贴图管理器窗口
    - 批量贴图处理
    
    边界：
    - 不包含UI相关代码
    - 不包含直接文件系统操作（通过Repository）
    - 不包含直接Maya API调用（通过Repository）
    """
    
    def __init__(self, config_manager: IConfigManager, logger: ILogger, ...):
        """初始化服务"""
        pass
```

**函数注释：**
```python
def fix_missing_textures(self, search_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    修复缺失贴图
    
    参数:
        search_path: 搜索路径
        options: 修复选项
            - exclude_list: 排除列表
            - extensions: 文件扩展名列表
            - weights: 相似度权重
    
    返回:
        修复结果字典
        - fixed_count: 修复数量
        - failed_count: 失败数量
        - matched: 匹配结果
    
    异常:
        ValueError: 搜索路径无效
        IOError: 文件读取失败
    """
    pass
```

**关键逻辑注释：**
```python
def _match_textures(self, missing_textures, dir_files, options):
    """匹配贴图"""
    # 使用多维度相似度算法匹配贴图
    # 原因：单一维度匹配准确率低，多维度可以提高准确率
    weights = options.get('weights', {
        'name_weight': 0.4,
        'resolution_weight': 0.3,
        'format_weight': 0.1,
        'creation_time_weight': 0.2
    })
    
    # 计算相似度
    for texture, info in missing_textures.items():
        similarities = {}
        for filename, filepath in dir_files.items():
            sim = self._calculate_similarity(info, filepath, weights)
            similarities[filename] = sim
        
        # 选择最佳匹配
        best_match = max(similarities.items(), key=lambda x: x[1])
        if best_match[1] > 0.8:  # 相似度阈值
            matched[texture] = filepath
    
    return matched
```

#### 8.1.3 代码格式

**使用black进行代码格式化：**
```bash
pip install black
black arnold_magic_node/
```

**使用isort进行import排序：**
```bash
pip install isort
isort arnold_magic_node/
```

**使用pylint进行代码检查：**
```bash
pip install pylint
pylint arnold_magic_node/
```

### 8.2 测试规范

#### 8.2.1 测试命名

**测试类名：** Test{ClassName}
```python
# ✅ 正确
class TestTextureManagerService:
    pass

# ❌ 错误
class TextureManagerServiceTest:
    pass
```

**测试函数名：** test_{function_name}_{scenario}
```python
# ✅ 正确
def test_fix_missing_textures_with_success():
    pass

def test_fix_missing_textures_with_error():
    pass

# ❌ 错误
def testFixMissingTextures():
    pass
```

#### 8.2.2 测试结构

```python
class TestTextureManagerService:
    """贴图管理服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return TextureManagerService(...)
    
    def test_fix_missing_textures_with_success(self, service):
        """测试修复缺失贴图（成功场景）"""
        # Arrange（准备）
        search_path = "/test/path"
        options = {"exclude_list": []}
        
        # Act（执行）
        result = service.fix_missing_textures(search_path, options)
        
        # Assert（断言）
        assert result["fixed_count"] > 0
        assert result["failed_count"] == 0
```

### 8.3 文档规范

#### 8.3.1 代码文档

**使用docstring编写文档：**
```python
class TextureManagerService(ITextureManagerService):
    """
    贴图管理服务
    
    提供贴图管理相关业务逻辑，包括贴图查询、过滤、修复、处理等功能。
    
    示例:
        >>> service = TextureManagerService(config, logger, ...)
        >>> textures = service.get_all_textures()
        >>> result = service.fix_missing_textures("/path", {})
    
    参见:
        ITextureManagerService
    """
    pass
```

#### 8.3.2 用户文档

**安装指南：**
```markdown
# 安装指南

## 前置要求

- Maya 2022+
- Arnold 5.0+
- Python 3.7+

## 安装步骤

1. 下载插件
2. 解压到Maya模块目录
3. 重启Maya
4. 运行插件
```

#### 8.3.3 开发者文档

**架构设计文档：**
```markdown
# 架构设计文档

## 概述

Arnold Magic Node采用四层架构：
- 表现层（UI Layer）
- 业务逻辑层（Service Layer）
- 数据访问层（Repository Layer）
- 基础设施层（Infrastructure Layer）

## 模块划分

### 核心模块

提供基础服务和工具，包括配置管理、日志、事件总线等。

### 配置模块

统一管理所有配置，包括配置仓储和配置验证器。

### 数据访问模块

封装数据访问逻辑，包括节点数据仓储和文件系统仓储。

### 服务模块

提供业务逻辑，包括贴图管理、节点连接、路径检测等。

### UI模块

提供用户界面和交互。
```

### 8.4 版本管理

#### 8.4.1 语义化版本

**版本格式：** MAJOR.MINOR.PATCH

**规则：**
- MAJOR：不兼容的API变更
- MINOR：向后兼容的功能新增
- PATCH：向后兼容的问题修复

**示例：**
- 1.0.0 → 1.1.0：新增功能（向后兼容）
- 1.1.0 → 2.0.0：不兼容的API变更
- 2.0.0 → 2.0.1：问题修复（向后兼容）

#### 8.4.2 发布流程

1. 创建release分支
2. 更新版本号
3. 更新CHANGELOG
4. 编写发布说明
5. 打包发布
6. 合并到main分支

### 8.5 持续集成

#### 8.5.1 CI/CD流程

```
代码提交
    ↓
自动运行单元测试
    ↓
自动运行集成测试
    ↓
代码覆盖率检查
    ↓
代码质量检查
    ↓
自动打包
    ↓
自动部署
```

#### 8.5.2 工具推荐

**GitHub Actions配置示例：**

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.7
      - name: Install dependencies
        run: |
          pip install pytest pytest-mock pytest-cov
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=arnold_magic_node --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### 8.6 常见问题

#### 8.6.1 如何添加新功能？

1. 确定功能所属模块
2. 在对应模块中创建Service
3. 定义接口和实现
4. 在DIContainer中注册
5. 在UI层调用
6. 编写测试

#### 8.6.2 如何修改配置？

1. 修改配置文件
2. 使用ConfigManager重新加载
3. 验证配置有效性
4. 测试配置变更

#### 8.6.3 如何调试问题？

1. 查看日志
2. 使用断点调试
3. 运行单元测试
4. 检查事件发布订阅

---

## 9. 风险评估与应对

### 9.1 风险识别

| 风险 | 概率 | 影响 | 优先级 | 应对措施 |
|-----|------|------|-------|---------|
| 全局变量迁移影响所有模块 | 高 | 高 | P0 | 分阶段迁移，充分测试 |
| UI重构影响用户体验 | 中 | 高 | P0 | 保持UI完全不变 |
| 性能退化 | 中 | 中 | P1 | 性能测试，优化关键路径 |
| 测试覆盖不足 | 中 | 高 | P1 | 充分的单元测试和集成测试 |
| 依赖注入配置复杂 | 低 | 中 | P2 | 简化配置，提供文档 |
| 事件驱动机制设计不当 | 低 | 中 | P2 | 充分的设计和测试 |
| 模块拆分不完整 | 低 | 中 | P2 | 充分的模块测试 |
| 文档不完整 | 中 | 低 | P3 | 文档审查，持续更新 |

### 9.2 风险应对

#### 9.2.1 全局变量迁移风险

**风险描述：** 全局变量被所有模块依赖，迁移可能影响所有模块

**应对措施：**
1. 分阶段迁移，每阶段充分测试
2. 保持向后兼容，使用特性开关
3. 建立配置验证机制
4. 充分的单元测试和集成测试

**回滚计划：**
- 如果迁移失败，立即回滚到上一个稳定版本
- 保留原有全局变量作为备份

#### 9.2.2 UI重构风险

**风险描述：** UI重构可能影响用户体验

**应对措施：**
1. 保持UI界面完全不变，只重构内部逻辑
2. 充分的UI测试
3. 用户验收测试
4. 灰度发布

**回滚计划：**
- 如果UI出现问题，立即回滚到上一个稳定版本
- 保留原有UI代码作为备份

#### 9.2.3 性能退化风险

**风险描述：** 重构可能导致性能退化

**应对措施：**
1. 性能基准测试
2. 持续性能监控
3. 优化关键路径
4. 性能回归测试

**回滚计划：**
- 如果性能退化超过阈值，立即回滚到上一个稳定版本
- 优化后重新发布

### 9.3 应急预案

#### 9.3.1 回滚流程

1. 停止新版本部署
2. 恢复上一个稳定版本
3. 验证功能正常
4. 分析失败原因
5. 修复问题
6. 重新测试
7. 重新部署

#### 9.3.2 紧急修复流程

1. 识别问题
2. 评估影响范围
3. 制定修复方案
4. 实施修复
5. 测试验证
6. 部署修复
7. 监控验证

---

## 10. 附录

### 10.1 术语表

| 术语 | 定义 |
|-----|------|
| **依赖注入（DI）** | 一种设计模式，通过构造函数、属性或方法参数将依赖传递给对象 |
| **依赖倒置原则（DIP）** | 高层模块不应依赖低层模块，两者都应依赖抽象 |
| **单一职责原则（SRP）** | 一个类应该只有一个引起它变化的原因 |
| **开闭原则（OCP）** | 对扩展开放，对修改关闭 |
| **接口隔离原则（ISP）** | 客户端不应依赖它不需要的接口 |
| **里氏替换原则（LSP）** | 子类可以替换父类而不影响程序正确性 |
| **仓储模式（Repository）** | 一种设计模式，封装数据访问逻辑 |
| **服务层（Service Layer）** | 业务逻辑层，负责业务规则和流程控制 |
| **数据访问层（Repository Layer）** | 数据访问层，负责数据持久化 |
| **表现层（UI Layer）** | 用户界面层，负责用户交互 |
| **事件总线（Event Bus）** | 一种消息传递机制，用于解耦模块间通信 |
| **单元测试** | 对最小可测试单元（函数、方法）进行测试 |
| **集成测试** | 对多个模块集成后的行为进行测试 |
| **端到端测试** | 对完整用户场景进行测试 |
| **测试覆盖率** | 测试代码覆盖的代码比例 |

### 10.2 参考资料

**设计模式：**
- 《设计模式：可复用面向对象软件的基础》- GoF
- 《企业应用架构模式》- Martin Fowler

**软件架构：**
- 《Clean Architecture》- Robert C. Martin
- 《架构整洁之道》- Robert C. Martin

**测试：**
- 《测试驱动开发》- Kent Beck
- 《单元测试的艺术》- Roy Osherove

**Python：**
- 《Python编程：从入门到实践》- Eric Matthes
- 《流畅的Python》- Luciano Ramalho

### 10.3 工具清单

**开发工具：**
- Python 3.7+
- Maya 2022+
- Arnold 5.0+

**测试工具：**
- pytest
- pytest-mock
- pytest-cov

**代码质量工具：**
- black（代码格式化）
- isort（import排序）
- pylint（代码检查）

**文档工具：**
- Sphinx（文档生成）
- MkDocs（文档生成）

**CI/CD工具：**
- GitHub Actions
- GitLab CI

### 10.4 联系方式

**技术支持：**
- Email: 1925250542@qq.com
- WeChat: 13549971630

**项目主页：**
- https://flowus.cn/amazingike/share/93cfb135-4ab3-4536-8a5b-9b3e53042b51?code=LZVF69

**问题反馈：**
- https://flowus.cn/form/7b125d97-3971-40ee-ac8b-9338e4a91909?code=LZVF69

**帮助文档：**
- https://flowus.cn/amazingike/share/6e8b16c6-f8b1-4f04-bad7-24ff003224dc?code=LZVF69

---

## 文档修订历史

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|------|---------|
| 1.0 | 2026-01-19 | Arnold Magic Node Team | 初始版本 |

---

**文档结束**
