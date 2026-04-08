# 后端项目全面重构 Spec

## Why

现有后端项目（`cloud/` 目录）存在以下核心问题：

1. **数据库选型不符规范**：当前使用 MongoDB（Motor），规范要求 MySQL + Redis
2. **项目结构不符规范**：当前使用 `modules/` 分层，规范要求 `api/` + `business/` + `utils/` + `core/` 结构
3. **编程范式不符规范**：当前大量使用 OOP（类静态方法），规范要求函数式编程风格
4. **接口方法不符规范**：当前混用 GET/POST/PUT/DELETE，规范要求所有接口使用 POST
5. **接口响应格式不符规范**：登录接口应返回 `{code, msg, token}`，分页接口应返回 `{code, msg, data, total}`
6. **代码重复严重**：`user/services/auth.py` 和 `system/services/auth.py` 几乎完全相同
7. **异常处理不一致**：部分使用 HTTPException，部分使用 ApiResponse.error，缺少统一异常机制
8. **配置硬编码**：敏感信息（API Key、JWT Secret）直接写在代码中

## What Changes

- **BREAKING**: 数据库从 MongoDB 迁移到 MySQL + Redis，所有数据访问层重写
- **BREAKING**: 项目结构从 `modules/` 改为 `api/` + `business/` + `utils/` + `core/`
- **BREAKING**: 所有 API 接口从 RESTful 风格（GET/PUT/DELETE）改为统一 POST 请求
- **BREAKING**: 登录接口响应格式从 `{code, msg, data: {access_token, token_type}}` 改为 `{code, msg, token}`
- **BREAKING**: 分页接口响应格式从 `{code, msg, data: {list, total, page, size, total_pages}}` 改为 `{code, msg, data, total}`
- **BREAKING**: 编程范式从 OOP 类静态方法改为函数式编程风格
- 合并重复的 auth 服务为统一的认证模块
- 引入统一异常处理机制（自定义异常 + 全局异常处理器）
- 引入 Redis 缓存和会话管理
- 引入数据库索引自动创建
- 配置管理优化，移除硬编码敏感信息
- 日志系统按规范配置（error.log + access.log，10MB 轮转，每天凌晨轮转，保留 7 天）
- 重构后的代码输出到新的 `backend/` 目录

## Impact

- Affected specs: 所有业务模块（用户认证、导航管理、文件上传、代理服务、系统管理、中转站、OpenList STRM）
- Affected code: 全部后端代码需要重写
- 前端兼容性：由于接口方法和响应格式变更，前端需要同步调整

## ADDED Requirements

### Requirement: 项目结构规范

系统 SHALL 按照以下目录结构组织代码：

```
backend/
├── app/
│   ├── api/             # API 路由层
│   │   ├── __init__.py
│   │   ├── auth.py      # 认证相关路由
│   │   ├── nav.py       # 导航管理路由
│   │   ├── upload.py    # 文件上传路由
│   │   ├── proxy.py     # 代理服务路由
│   │   ├── system.py    # 系统管理路由
│   │   ├── transfer.py  # 中转站路由
│   │   └── openlist.py  # OpenList STRM 路由
│   ├── business/        # 业务逻辑层（按功能划分）
│   │   ├── auth/        # 认证业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   ├── nav/         # 导航管理业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   ├── user/        # 用户管理业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   ├── system/      # 系统管理业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   ├── upload/      # 文件上传业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   ├── proxy/       # 代理服务业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   ├── transfer/    # 中转站业务
│   │   │   ├── __init__.py
│   │   │   ├── service.py
│   │   │   └── schema.py
│   │   └── openlist/    # OpenList STRM 业务
│   │       ├── __init__.py
│   │       ├── service.py
│   │       ├── schema.py
│   │       ├── openlist_api.py
│   │       ├── strm_generator.py
│   │       └── task_status_manager.py
│   ├── utils/           # 工具函数
│   │   ├── __init__.py
│   │   ├── response.py  # 统一响应工具
│   │   ├── security.py  # 安全相关工具
│   │   └── helpers.py   # 通用辅助函数
│   ├── core/            # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py    # 配置管理
│   │   ├── database.py  # 数据库连接（MySQL）
│   │   ├── redis.py     # Redis 连接
│   │   ├── logger.py    # 日志系统
│   │   ├── exceptions.py # 自定义异常
│   │   └── websocket_manager.py
│   └── main.py          # 应用入口
├── logs/                # 日志目录
├── requirements.txt     # 依赖管理
└── .env                 # 环境变量
```

#### Scenario: 目录结构验证

- **WHEN** 检查项目目录
- **THEN** 所有目录和文件按照上述结构组织

### Requirement: 数据库迁移（MongoDB → MySQL + Redis）

系统 SHALL 使用 MySQL 作为主数据库，Redis 作为缓存和会话管理。

#### Scenario: MySQL 数据库连接

- **WHEN** 应用启动
- **THEN** 成功连接到 MySQL 数据库（localhost:3306，用户名 root，密码 root123456，数据库 cloud）

#### Scenario: Redis 连接

- **WHEN** 应用启动
- **THEN** 成功连接到 Redis（localhost:6379，密码 114514）

#### Scenario: 数据表设计

- **WHEN** 应用启动
- **THEN** 自动创建以下数据表：
  - `users`：id, user_name, password, is_active, created_at, updated_at
  - `tabs`：id, user_id, label, `desc`, `order`, created_at, updated_at
  - `websites`：id, user_id, tab_id, label, url, `desc`, icon, github, document, `order`, created_at, updated_at
  - `menus`：id, path, name, component, meta, parent_id, `order`, created_at, updated_at
  - `holidays`：id, year, holiday, adjustment, created_at, updated_at
  - `text_transfers`：id, user_id, content, title, created_at, updated_at
  - `file_transfers`：id, user_id, filename, file_size, file_hash, content_type, status, chunks_uploaded, total_chunks, created_at, updated_at
  - `openlist_global_configs`：id, user_id, base_url, token, video_extensions, subtitle_extensions, created_at, updated_at
  - `openlist_task_configs`：id, user_id, name, output_dir, task_paths, max_scan_depth, execution_history, created_at, updated_at

### Requirement: 统一 POST 接口

系统 SHALL 所有接口均使用 POST 请求方法，遵循数据规范文档。

#### Scenario: 登录接口

- **WHEN** 用户发送 POST /api/user/login，请求体包含 `userName` 和 `password`
- **THEN** 返回 `{code: 200, msg: "success", token: "xxx"}`

#### Scenario: 普通接口

- **WHEN** 用户发送 POST 请求到任意业务接口
- **THEN** 返回 `{code: Number, msg: String, data: any}`

#### Scenario: 分页接口

- **WHEN** 用户发送 POST 请求到分页接口，请求体包含 `pageNum` 和 `pageSize`
- **THEN** 返回 `{code: Number, msg: String, data: Array, total: Number}`

### Requirement: 函数式编程风格

系统 SHALL 优先使用函数式编程风格实现业务逻辑。

#### Scenario: 服务层实现

- **WHEN** 实现业务逻辑
- **THEN** 使用纯函数而非类静态方法，避免可变状态，合理使用高阶函数和闭包

### Requirement: 统一异常处理

系统 SHALL 实现统一的异常处理机制。

#### Scenario: 自定义异常

- **WHEN** 业务逻辑出现错误
- **THEN** 抛出对应的自定义异常（NotFoundException、ValidationException、AuthException 等）

#### Scenario: 全局异常处理

- **WHEN** 应用抛出任何异常
- **THEN** 全局异常处理器捕获并返回统一格式的错误响应 `{code, msg}`

### Requirement: 日志管理规范

系统 SHALL 按照规范配置日志系统。

#### Scenario: 日志文件

- **WHEN** 应用运行
- **THEN** 生成 `logs/error.log` 和 `logs/access.log`

#### Scenario: 日志轮转

- **WHEN** 日志文件达到 10MB
- **THEN** 自动轮转

#### Scenario: 日志保留

- **WHEN** 日志超过 7 天
- **THEN** 自动清理

### Requirement: Redis 缓存与 JWT 会话管理

系统 SHALL 使用 Redis 进行缓存和 JWT Token 管理。

#### Scenario: Token 黑名单

- **WHEN** 用户登出或 Token 需要失效
- **THEN** 将 Token 加入 Redis 黑名单

#### Scenario: 天气数据缓存

- **WHEN** 请求天气数据
- **THEN** 优先从 Redis 缓存获取，缓存未命中时请求外部 API 并写入缓存（TTL 5 分钟）

### Requirement: 配置安全

系统 SHALL 移除所有硬编码的敏感信息，通过环境变量管理。

#### Scenario: 敏感配置

- **WHEN** 应用加载配置
- **THEN** JWT_SECRET_KEY、QWEATHER_KEY 等敏感信息从 .env 文件读取，代码中不包含默认值

### Requirement: 数据库索引

系统 SHALL 在应用启动时自动创建必要的数据库索引。

#### Scenario: 索引创建

- **WHEN** 应用启动
- **THEN** 为 users.user_name（唯一索引）、tabs(user_id, order)、websites(user_id, tab_id, order) 等创建索引

## MODIFIED Requirements

### Requirement: 用户认证模块

原有功能：登录、注册、获取用户信息、更新用户信息。

修改内容：

- 登录接口请求参数从 `{username, password}` 改为 `{userName, password}`
- 登录接口响应从 `{code, msg, data: {access_token, token_type}}` 改为 `{code, msg, token}`
- 所有接口方法改为 POST
- 合并 user/services/auth.py 和 system/services/auth.py 为统一的 business/auth/service.py
- 使用 MySQL 替代 MongoDB 存储用户数据
- 使用 Redis 管理 Token 黑名单

### Requirement: 导航管理模块

原有功能：Tab 和 Website 的 CRUD、排序。

修改内容：

- 所有接口方法改为 POST
- 分页接口响应格式改为 `{code, msg, data, total}`
- 使用 MySQL 替代 MongoDB
- 数据库字段名使用小驼峰命名（camelCase）

### Requirement: 系统管理模块

原有功能：菜单 CRUD、树形结构构建。

修改内容：

- 所有接口方法改为 POST
- 使用 MySQL 替代 MongoDB
- 移除重复的 auth 服务，使用统一的 business/auth/ 模块

### Requirement: 文件上传模块

原有功能：单文件和批量文件上传。

修改内容：

- 接口方法改为 POST
- 使用流式读取替代一次性读取
- 使用 MySQL 记录文件信息（如需要）

### Requirement: 代理服务模块

原有功能：天气代理、节假日数据管理。

修改内容：

- 天气接口方法改为 POST
- 节假日接口方法改为 POST
- 引入 Redis 缓存天气数据
- 使用 MySQL 替代 MongoDB 存储节假日数据

### Requirement: 中转站模块

原有功能：文本中转、文件中转（分片上传）。

修改内容：

- 所有接口方法改为 POST
- 分页接口响应格式改为 `{code, msg, data, total}`
- 使用 MySQL 替代 MongoDB

### Requirement: OpenList STRM 模块

原有功能：全局配置管理、任务配置管理、STRM 生成、WebSocket 日志。

修改内容：

- 所有接口方法改为 POST
- 使用 MySQL 替代 MongoDB
- 保留 WebSocket 功能
- 保留 STRM 生成核心逻辑

## REMOVED Requirements

### Requirement: MongoDB 数据库

**Reason**: 规范要求使用 MySQL + Redis
**Migration**: 所有 MongoDB 集合迁移为 MySQL 数据表，ObjectId 迁移为自增 ID

### Requirement: OOP 类静态方法服务模式

**Reason**: 规范要求函数式编程风格
**Migration**: 所有 `class XxxService: @staticmethod` 改为模块级纯函数
