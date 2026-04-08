# Cloud Server

轻量级导航页后端服务，提供用户认证、导航管理、文件上传、代理服务、系统管理、中转站和 OpenList STRM 生成等核心能力。

## 版本信息

| 项目     | 值                        |
| -------- | ------------------------- |
| 当前版本 | 2.0.0                     |
| 前一版本 | [1.0.0](PROJECT_ANALYSIS.md) |
| Python   | 3.9+                      |
| 框架     | FastAPI 0.109+            |

---

## v2.0.0 与 v1.0.0 对比

### 架构变更

| 变更项     | v1.0.0                           | v2.0.0                                                      |
| ---------- | -------------------------------- | ----------------------------------------------------------- |
| 数据库     | MongoDB (Motor)                  | **MySQL (SQLAlchemy + aiomysql)**                     |
| 缓存       | 无                               | **Redis**                                             |
| 项目结构   | `modules/` 分层                | **`api/` + `business/` + `utils/` + `core/`** |
| 编程范式   | OOP 类静态方法                   | **函数式编程风格（纯函数）**                          |
| 接口方法   | GET/POST/PUT/DELETE 混用         | **统一 POST 请求**                                    |
| 认证服务   | 重复代码 (user + system)         | **统一合并为 business/auth/**                         |
| 异常处理   | HTTPException + ApiResponse 混用 | **自定义异常 + 全局异常处理器**                       |
| 配置管理   | 硬编码敏感信息                   | **环境变量注入 (.env)**                               |
| 日志系统   | 基础日志                         | **access.log + error.log 分离，自动轮转**             |
| Token 管理 | 仅客户端存储                     | **Redis 黑名单支持服务端失效**                        |
| 天气缓存   | 无缓存                           | **Redis 缓存 (TTL 5 分钟)**                           |
| 文件上传   | 一次性读取                       | **流式读取 (1MB chunk)**                              |
| 数据库索引 | 无索引                           | **自动创建复合索引**                                  |

### 接口规范变更

| 变更项       | v1.0.0                                                        | v2.0.0                                 |
| ------------ | ------------------------------------------------------------- | -------------------------------------- |
| 登录请求参数 | `{username, password}`                                      | **`{userName, password}`**     |
| 登录响应格式 | `{code, msg, data: {access_token, token_type}}`             | **`{code, msg, token}`**       |
| 普通接口响应 | `{code, msg, data}`                                         | `{code, msg, data}` (不变)           |
| 分页接口响应 | `{code, msg, data: {list, total, page, size, total_pages}}` | **`{code, msg, data, total}`** |
| 分页请求参数 | `{page, size}`                                              | **`{pageNum, pageSize}`**      |
| HTTP 方法    | GET/POST/PUT/DELETE                                           | **统一 POST**                    |

### 状态码规范

| 状态码 | 含义             |
| ------ | ---------------- |
| 200    | 操作成功         |
| 400    | 请求参数错误     |
| 401    | 未授权或登录失效 |
| 403    | 权限不足         |
| 404    | 资源不存在       |
| 500    | 服务器内部错误   |

---

## 项目结构

```
cloud-nav/
├── app/
│   ├── api/                 # API 路由层
│   │   ├── auth.py          # 认证路由
│   │   ├── user.py          # 用户路由
│   │   ├── nav.py           # 导航管理路由
│   │   ├── system.py        # 系统管理路由
│   │   ├── upload.py        # 文件上传路由
│   │   ├── proxy.py         # 代理服务路由
│   │   ├── transfer.py      # 中转站路由
│   │   └── openlist.py      # OpenList STRM 路由
│   ├── business/            # 业务逻辑层
│   │   ├── auth/            # 认证业务
│   │   ├── user/            # 用户管理业务
│   │   ├── nav/             # 导航管理业务
│   │   ├── system/          # 系统管理业务
│   │   ├── upload/          # 文件上传业务
│   │   ├── proxy/           # 代理服务业务
│   │   ├── transfer/        # 中转站业务
│   │   └── openlist/        # OpenList STRM 业务
│   ├── utils/               # 工具函数
│   │   ├── response.py      # 统一响应
│   │   ├── security.py      # JWT / 密码安全
│   │   └── helpers.py       # 通用辅助函数
│   ├── core/                # 核心基础设施
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # MySQL 连接
│   │   ├── redis.py         # Redis 连接
│   │   ├── logger.py        # 日志系统
│   │   ├── exceptions.py    # 自定义异常
│   │   ├── models.py        # ORM 数据模型
│   │   └── websocket_manager.py  # WebSocket 管理
│   └── main.py              # 应用入口
├── logs/                    # 日志目录
├── uploads/                 # 上传文件目录
├── requirements.txt         # 依赖管理
├── run.py                   # 启动脚本
├── .env                     # 环境变量
└── .gitignore
```

---

## 快速开始

### 环境要求

- Python 3.9+
- MySQL 8.0+
- Redis 7.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制以下内容到 `.env` 文件并填写实际值：

```env
APP_NAME=Cloud Server
APP_VERSION=2.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=cloud
MYSQL_POOL_SIZE=10
MYSQL_MAX_OVERFLOW=20

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

LOG_LEVEL=INFO
LOG_DIR=logs

JWT_SECRET_KEY=your_jwt_secret_key_at_least_32_chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

QWEATHER_HOST=https://devapi.qweather.com
QWEATHER_KEY=your_qweather_api_key

HOLIDAY_API_BASE=http://timor.tech/api/holiday/year
```

### 启动服务

```bash
python run.py
```

或直接使用 uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：

- 服务地址: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 数据库设计

### 数据表

| 表名                    | 说明              | 关键索引                 |
| ----------------------- | ----------------- | ------------------------ |
| users                   | 用户表            | user_name (UNIQUE)       |
| tabs                    | 导航标签表        | (user_id, order)         |
| websites                | 网站表            | (user_id, tab_id, order) |
| menus                   | 菜单表            | parent_id                |
| holidays                | 节假日表          | year (UNIQUE)            |
| text_transfers          | 文本中转表        | user_id                  |
| file_transfers          | 文件中转表        | user_id                  |
| openlist_global_configs | OpenList 全局配置 | user_id (UNIQUE)         |
| openlist_task_configs   | OpenList 任务配置 | user_id                  |

应用启动时自动创建数据表和索引，无需手动建表。

---

## API 接口

### 认证接口

| 路径                    | 功能     | 认证 |
| ----------------------- | -------- | ---- |
| POST /api/user/login    | 用户登录 | 否   |
| POST /api/user/register | 用户注册 | 否   |

### 用户接口

| 路径                    | 功能              | 认证 |
| ----------------------- | ----------------- | ---- |
| POST /api/user/userInfo | 获取/更新用户信息 | 是   |

### 导航管理接口

| 路径                         | 功能                     | 认证 |
| ---------------------------- | ------------------------ | ---- |
| POST /api/nav/tabs           | 获取所有标签             | 是   |
| POST /api/nav/tab/add        | 创建标签                 | 是   |
| POST /api/nav/tab/update     | 更新标签                 | 是   |
| POST /api/nav/tab/delete     | 删除标签                 | 是   |
| POST /api/nav/websites       | 获取网站列表（支持分页） | 是   |
| POST /api/nav/website/add    | 创建网站                 | 是   |
| POST /api/nav/website/update | 更新网站                 | 是   |
| POST /api/nav/website/delete | 删除网站                 | 是   |
| POST /api/nav/website/order  | 批量更新排序             | 是   |

### 系统管理接口

| 路径                         | 功能             | 认证 |
| ---------------------------- | ---------------- | ---- |
| POST /api/system/menus       | 获取菜单树       | 是   |
| POST /api/system/menu/add    | 创建菜单         | 是   |
| POST /api/system/menu/update | 更新菜单         | 是   |
| POST /api/system/menu/delete | 删除菜单（递归） | 是   |

### 文件上传接口

| 路径                   | 功能         | 认证 |
| ---------------------- | ------------ | ---- |
| POST /api/upload/file  | 上传单个文件 | 是   |
| POST /api/upload/files | 批量上传文件 | 是   |

### 代理服务接口

| 路径                           | 功能                       | 认证 |
| ------------------------------ | -------------------------- | ---- |
| POST /api/proxy/weather        | 获取天气信息（Redis 缓存） | 是   |
| POST /api/proxy/holidays       | 获取节假日列表             | 是   |
| POST /api/proxy/holiday/add    | 创建/更新节假日数据        | 是   |
| POST /api/proxy/holiday/delete | 删除节假日数据             | 是   |

### 中转站接口

| 路径                             | 功能                 | 认证 |
| -------------------------------- | -------------------- | ---- |
| POST /api/transfer/text/list     | 获取文本列表         | 是   |
| POST /api/transfer/text/add      | 创建文本中转         | 是   |
| POST /api/transfer/text/update   | 更新文本中转         | 是   |
| POST /api/transfer/text/delete   | 删除文本中转         | 是   |
| POST /api/transfer/file/create   | 创建文件中转         | 是   |
| POST /api/transfer/file/chunk    | 上传文件分片         | 是   |
| POST /api/transfer/file/complete | 完成文件上传         | 是   |
| POST /api/transfer/file/list     | 获取文件列表（分页） | 是   |
| POST /api/transfer/file/delete   | 删除文件中转         | 是   |

### OpenList STRM 接口

| 路径                                    | 功能               | 认证 |
| --------------------------------------- | ------------------ | ---- |
| POST /api/openlist/global-config        | 获取全局配置       | 是   |
| POST /api/openlist/global-config/add    | 创建全局配置       | 是   |
| POST /api/openlist/global-config/update | 更新全局配置       | 是   |
| POST /api/openlist/global-config/delete | 删除全局配置       | 是   |
| POST /api/openlist/task-config/list     | 获取任务配置列表   | 是   |
| POST /api/openlist/task-config          | 获取单个任务配置   | 是   |
| POST /api/openlist/task-config/add      | 创建任务配置       | 是   |
| POST /api/openlist/task-config/update   | 更新任务配置       | 是   |
| POST /api/openlist/task-config/delete   | 删除任务配置       | 是   |
| POST /api/openlist/execute              | 执行 STRM 生成任务 | 是   |
| POST /api/openlist/cancel               | 取消任务           | 是   |
| WS /api/openlist/ws/logs                | 实时日志推送       | -    |

---

## 认证机制

所有需要认证的接口通过 `Authorization` Header 传递 JWT Token：

```
Authorization: Bearer <token>
```

或直接传递 Token：

```
Authorization: <token>
```

### Token 黑名单

v2.0.0 新增 Redis Token 黑名单机制，支持服务端强制使 Token 失效（如用户登出场景）。

---

## 日志系统

| 日志文件                  | 内容          | 轮转策略      | 保留策略 |
| ------------------------- | ------------- | ------------- | -------- |
| logs/access.log           | 访问日志      | 10MB 大小轮转 | 7 天     |
| logs/error.log            | 错误日志      | 10MB 大小轮转 | 7 天     |
| logs/alist_strm.log       | STRM 任务日志 | 50MB 大小轮转 | 10 天    |
| logs/alist_strm_error.log | STRM 错误日志 | 10MB 大小轮转 | 30 天    |

日志格式：`时间 | 级别 | IP | 方法 | 路径 | 状态码 | 响应时间`

---

## 技术栈

| 类别        | 技术              | 版本      | 用途            |
| ----------- | ----------------- | --------- | --------------- |
| Web 框架    | FastAPI           | >=0.109.0 | API 开发框架    |
| ASGI 服务器 | Uvicorn           | >=0.27.0  | 异步服务器      |
| 数据库      | MySQL             | 8.0+      | 关系型数据库    |
| ORM         | SQLAlchemy        | >=2.0.0   | 异步 ORM        |
| MySQL 驱动  | aiomysql          | >=0.2.0   | 异步 MySQL 驱动 |
| 缓存        | Redis             | >=5.0.0   | 缓存和会话管理  |
| 数据验证    | Pydantic          | >=2.5.0   | 数据模型验证    |
| 配置管理    | pydantic-settings | >=2.1.0   | 环境配置        |
| 日志系统    | Loguru            | >=0.7.2   | 结构化日志      |
| HTTP 客户端 | httpx             | >=0.26.0  | 异步 HTTP 请求  |
| JWT         | python-jose       | >=3.3.0   | JWT 处理        |
| 密码加密    | passlib[bcrypt]   | >=1.7.4   | 密码哈希        |
