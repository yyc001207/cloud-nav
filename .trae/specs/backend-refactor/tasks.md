# 后端项目全面重构 - 实现任务清单

## Task 1: 创建新项目目录结构与依赖配置

- [x] Task 1.1: 创建 `backend/` 目录及完整子目录结构（app/api、app/business、app/utils、app/core）
- [x] Task 1.2: 创建 `requirements.txt`，包含 FastAPI、uvicorn、aiomysql、sqlalchemy、redis、pydantic、loguru、httpx、python-jose、passlib 等依赖
- [x] Task 1.3: 创建 `.env` 环境变量文件模板，移除所有硬编码敏感信息
- [x] Task 1.4: 创建所有 `__init__.py` 文件

## Task 2: 实现核心基础设施层（core/）

- [x] Task 2.1: 实现 `core/config.py` - 使用 pydantic-settings 管理配置，包含 MySQL、Redis、JWT、日志等配置项，敏感信息通过环境变量注入
- [x] Task 2.2: 实现 `core/database.py` - MySQL 数据库连接（使用 SQLAlchemy + aiomysql 异步引擎），包含连接池配置、启动/关闭生命周期管理
- [x] Task 2.3: 实现 `core/redis.py` - Redis 连接管理，提供 get/set/delete 等异步操作封装
- [x] Task 2.4: 实现 `core/logger.py` - 日志系统（error.log + access.log），10MB 大小轮转，每天凌晨时间轮转，保留 7 天
- [x] Task 2.5: 实现 `core/exceptions.py` - 自定义异常类（AppException、NotFoundException、ValidationException、AuthException）+ FastAPI 全局异常处理器
- [x] Task 2.6: 实现 `core/websocket_manager.py` - WebSocket 连接管理器，保留原有的频道广播功能

## Task 3: 实现工具函数层（utils/）

- [x] Task 3.1: 实现 `utils/response.py` - 统一响应工具函数，包含 `success_response()`、`error_response()`、`paginated_response()` 等
- [x] Task 3.2: 实现 `utils/security.py` - JWT Token 创建/验证、密码哈希/验证、Token 黑名单管理（Redis）
- [x] Task 3.3: 实现 `utils/helpers.py` - 通用辅助函数（驼峰转换、ObjectId 处理、时区转换、数据脱敏等）

## Task 4: 实现数据模型与数据库表

- [x] Task 4.1: 定义 SQLAlchemy ORM 模型 - User、Tab、Website、Menu、Holiday、TextTransfer、FileTransfer、OpenListGlobalConfig、OpenListTaskConfig
- [x] Task 4.2: 实现数据库自动建表和索引创建逻辑
- [x] Task 4.3: 确保所有字段名使用小驼峰命名（camelCase），通过 SQLAlchemy column 映射实现

## Task 5: 实现认证业务模块（business/auth/）

- [x] Task 5.1: 实现 `business/auth/schema.py` - 登录请求（userName + password）、Token 响应等 Pydantic 模型
- [x] Task 5.2: 实现 `business/auth/service.py` - 统一认证服务函数（authenticate_user、create_access_token、verify_token、get_current_user），函数式风格

## Task 6: 实现用户管理业务模块（business/user/）

- [x] Task 6.1: 实现 `business/user/schema.py` - 用户创建、更新、响应等 Pydantic 模型
- [x] Task 6.2: 实现 `business/user/service.py` - 用户 CRUD 函数（create_user、get_user_by_id、update_user），函数式风格

## Task 7: 实现导航管理业务模块（business/nav/）

- [x] Task 7.1: 实现 `business/nav/schema.py` - Tab 和 Website 的创建、更新、响应等 Pydantic 模型，包含 IconInfo
- [x] Task 7.2: 实现 `business/nav/service.py` - Tab CRUD、Website CRUD、排序逻辑、批量操作，函数式风格

## Task 8: 实现系统管理业务模块（business/system/）

- [x] Task 8.1: 实现 `business/system/schema.py` - Menu 的创建、更新、响应等 Pydantic 模型，包含 MenuMeta
- [x] Task 8.2: 实现 `business/system/service.py` - Menu CRUD、树形结构构建、递归删除，函数式风格

## Task 9: 实现文件上传业务模块（business/upload/）

- [x] Task 9.1: 实现 `business/upload/schema.py` - 上传响应 Pydantic 模型
- [x] Task 9.2: 实现 `business/upload/service.py` - 文件上传（流式读取）、UUID 命名、大小限制，函数式风格

## Task 10: 实现代理服务业务模块（business/proxy/）

- [x] Task 10.1: 实现 `business/proxy/schema.py` - 天气请求/响应、节假日请求/响应 Pydantic 模型
- [x] Task 10.2: 实现 `business/proxy/service.py` - 天气代理（含 Redis 缓存）、节假日数据管理，函数式风格

## Task 11: 实现中转站业务模块（business/transfer/）

- [x] Task 11.1: 实现 `business/transfer/schema.py` - 文本/文件中转的创建、更新、响应 Pydantic 模型
- [x] Task 11.2: 实现 `business/transfer/service.py` - 文本中转 CRUD、文件中转（分片上传/合并/下载），函数式风格

## Task 12: 实现 OpenList STRM 业务模块（business/openlist/）

- [x] Task 12.1: 实现 `business/openlist/schema.py` - 全局配置、任务配置、执行请求/响应 Pydantic 模型
- [x] Task 12.2: 实现 `business/openlist/service.py` - 全局配置 CRUD、任务配置 CRUD、执行记录管理，函数式风格
- [x] Task 12.3: 实现 `business/openlist/openlist_api.py` - OpenList API 异步客户端（保留原有逻辑）
- [x] Task 12.4: 实现 `business/openlist/strm_generator.py` - STRM 文件生成器（保留原有核心逻辑）
- [x] Task 12.5: 实现 `business/openlist/task_status_manager.py` - 任务状态管理器（保留原有逻辑）

## Task 13: 实现 API 路由层（api/）

- [x] Task 13.1: 实现 `api/auth.py` - 认证路由（POST /login、POST /register），使用统一认证模块
- [x] Task 13.2: 实现 `api/user.py` - 用户路由（POST /userInfo 获取/更新）
- [x] Task 13.3: 实现 `api/nav.py` - 导航路由（POST /tabs、POST /websites 等），所有接口使用 POST 方法
- [x] Task 13.4: 实现 `api/system.py` - 系统路由（POST /menus 等）
- [x] Task 13.5: 实现 `api/upload.py` - 上传路由（POST /file、POST /files）
- [x] Task 13.6: 实现 `api/proxy.py` - 代理路由（POST /weather、POST /holidays 等）
- [x] Task 13.7: 实现 `api/transfer.py` - 中转站路由（POST /text、POST /file 等）
- [x] Task 13.8: 实现 `api/openlist.py` - OpenList 路由（POST /global-config、POST /task-config、POST /execute 等）+ WebSocket 路由

## Task 14: 实现应用入口与整合

- [x] Task 14.1: 实现 `main.py` - FastAPI 应用创建、路由注册、CORS 配置、生命周期管理（数据库/Redis 连接/断开）、静态文件挂载
- [x] Task 14.2: 实现统一 JWT 认证依赖注入（从 Header 提取 Token → 验证 → 返回用户信息）
- [x] Task 14.3: 实现请求日志中间件（记录 IP、方法、路径、状态码、响应时间）

## Task 15: 验证与测试

- [x] Task 15.1: 使用 flake8 检查代码是否符合 PEP 8 规范
- [x] Task 15.2: 验证所有 API 接口是否使用 POST 方法
- [x] Task 15.3: 验证接口响应格式是否符合数据规范
- [x] Task 15.4: 验证 MySQL 数据库连接和表创建
- [x] Task 15.5: 验证 Redis 连接和缓存功能
- [x] Task 15.6: 验证日志生成、记录和轮转

# Task Dependencies

- Task 1 → Task 2（目录结构创建后才能实现核心层）
- Task 2 → Task 3（核心层完成后才能实现工具函数）
- Task 2 → Task 4（核心层完成后才能定义数据模型）
- Task 3 + Task 4 → Task 5~12（工具函数和数据模型完成后才能实现业务模块）
- Task 5 → Task 6（认证模块是用户管理的基础）
- Task 5 → Task 13（认证模块是路由层 JWT 验证的基础）
- Task 5~12 → Task 13（业务模块完成后才能实现路由层）
- Task 13 → Task 14（路由层完成后才能整合应用入口）
- Task 14 → Task 15（应用整合完成后才能进行验证测试）
- Task 7 和 Task 8 可并行
- Task 9、Task 10、Task 11 可并行
- Task 12 独立于 Task 7~11
