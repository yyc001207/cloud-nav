# Cloud Server — 待修复问题与功能规划

## 文档信息

- **项目名称**: Cloud Server v2.0.0
- **创建日期**: 2026-04-12
- **文档用途**: 记录已知问题、待修复缺陷及计划实现的功能

---

## 问题清单

### BUG-001：前端缺乏主动退出登录功能

| 属性     | 值                                 |
| -------- | ---------------------------------- |
| 严重程度 | 🟡 中                              |
| 影响范围 | 前端                               |
| 模块     | 认证                               |
| 状态     | 待实现                             |

**问题描述**

系统前端没有提供主动退出登录的入口，用户无法手动注销当前会话。后端已实现完整的登出接口 `POST /api/user/logout`（Redis Token 黑名单机制），但前端未对接。

**后端接口现状**

- `POST /api/user/logout` — 已实现，接收 Token 并加入 Redis 黑名单
- Token 黑名单 TTL 与 Token 剩余有效期一致，过期后自动清理

**修复方案**

1. 前端添加退出登录按钮（通常在用户头像/菜单下拉中）
2. 点击后调用 `POST /api/user/logout`，请求头携带 `Authorization: <token>`
3. 成功后清除前端存储的 Token（localStorage / cookie）
4. 跳转至登录页面

**验收标准**

- 用户可点击退出按钮完成登出
- 登出后旧 Token 立即失效（访问需认证接口返回 401）
- 登出后自动跳转至登录页

---

### BUG-002：WebSocket 实时日志连接失败（无报错）

| 属性     | 值                                 |
| -------- | ---------------------------------- |
| 严重程度 | 🔴 高                              |
| 影响范围 | 前端 + 后端                        |
| 模块     | OpenList STRM                      |
| 状态     | 待排查                             |

**问题描述**

测试过程中，WebSocket 实时日志推送连接建立失败，但前端和后端均无报错信息，导致用户无法实时查看 STRM 任务执行日志。

**代码分析**

当前 WebSocket 端点实现（`app/api/openlist.py`）：

```python
@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket, "all")
    set_websocket_broadcast(manager.broadcast)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, "all")
```

**已发现的问题**

1. **无身份验证**：WebSocket 连接不进行身份验证，任何人可连接接收日志广播。FastAPI WebSocket 不支持 Header 依赖注入，需通过查询参数传递 Token
2. **无心跳机制**：缺少 ping/pong 心跳，客户端异常断开时服务端无法及时感知，可能产生僵尸连接
3. **重复广播风险**：`ConnectionManager` 维护三个频道（`strm_logs`、`strm_error`、`all`），但端点只订阅 `"all"`，广播时可能向同一连接发送重复消息
4. **`set_websocket_broadcast` 每次连接重复调用**：应在应用启动时初始化一次

**修复方案**

1. 添加查询参数 Token 验证：`ws://host/api/openlist/ws/logs?token=<jwt_token>`
2. 添加心跳机制：服务端定期发送 ping，超时未响应则断开连接
3. 修复频道订阅逻辑，避免重复消息
4. 将 `set_websocket_broadcast` 移至应用启动事件
5. 添加连接失败时的错误响应（如认证失败返回 4001 关闭码）

**验收标准**

- 前端可成功建立 WebSocket 连接并接收实时日志
- 无效 Token 连接被拒绝并返回明确错误
- 客户端异常断开后服务端自动清理连接
- 不出现重复日志消息

---

### BUG-003：STRM 文件生成未删除移动过的文件

| 属性     | 值                                 |
| -------- | ---------------------------------- |
| 严重程度 | 🟡 中                              |
| 影响范围 | 后端                               |
| 模块     | OpenList STRM                      |
| 状态     | 部分修复，存在边缘问题             |

**问题描述**

当网盘中将 A 目录的文件或文件夹移动到 B 目录时，本地 A 目录中对应的文件或文件夹未被完全删除。

**已完成的修复**

- `_scan_and_process` 方法已添加云端子目录名称收集
- `_cleanup_current_dir` 方法已添加子目录递归删除逻辑
- 新增 `_cleanup_empty_dirs` 方法清理空目录

**仍存在的边缘问题**

1. **`cloud_files` 为空时不执行清理**：当云端某目录下无视频/字幕文件时，`_cleanup_current_dir` 直接返回，不清理该目录下的残留文件

   ```python
   def _cleanup_current_dir(self, output_base, cloud_files, base_path, scan_path, cloud_dir_names=None):
       if not cloud_files:
           return  # ← 此处导致空目录下的残留文件不被清理
   ```

2. **深层嵌套目录的清理依赖递归调用**：如果中间层目录被移动，需要确保递归扫描能正确到达所有层级

**修复方案**

1. 修改 `cloud_files` 为空时的处理逻辑：即使云端无文件，仍应检查并清理本地残留
2. 添加集成测试覆盖文件移动场景

**验收标准**

- 网盘文件移动后，本地对应文件/目录被正确删除
- 云端空目录下无残留本地文件
- 空目录被自动清理

---

### BUG-004：OpenList 同一任务执行多次只返回第一次执行结果

| 属性     | 值                                 |
| -------- | ---------------------------------- |
| 严重程度 | 🔴 高                              |
| 影响范围 | 后端                               |
| 模块     | OpenList STRM                      |
| 状态     | 待修复                             |

**问题描述**

同一任务配置被多次执行时，查询执行历史只返回第一次的执行结果，后续执行的结果丢失。

**根本原因**

执行记录存储在 `OpenListTaskConfigModel.execution_history` JSON 字段中，采用"读取 → 追加 → 写回"的模式。当同一任务并发执行时，存在**丢失更新**的数据竞争：

```
协程 A 读取 history = [record1, record2]
协程 B 读取 history = [record1, record2]
协程 A 写入 history = [record1, record2, recordA]
协程 B 写入 history = [record1, record2, recordB]  ← recordA 被覆盖丢失
```

**代码位置**

- `app/business/openlist/service.py` — `add_execution_record` 函数

**修复方案**

1. **方案 A：数据库行级锁**（推荐）
   - 使用 `SELECT ... FOR UPDATE` 锁定任务配置行，确保读取和写入的原子性
   - 适用于当前 JSON 字段存储方式

2. **方案 B：独立执行记录表**
   - 创建 `openlist_execution_records` 表，每次执行插入新行
   - 彻底避免并发写入冲突，且不受 20 条上限限制
   - 支持更灵活的查询和索引

3. **方案 C：Redis 分布式锁**
   - 在写入前获取任务级别的 Redis 锁
   - 适用于高并发场景

**验收标准**

- 同一任务并发执行多次，所有执行结果均被正确记录
- 执行历史按时间倒序排列
- 不存在记录丢失或覆盖

---

### BUG-005：文件中转上传小文件失败

| 属性     | 值                                 |
| -------- | ---------------------------------- |
| 严重程度 | 🔴 高                              |
| 影响范围 | 后端                               |
| 模块     | 中转站                             |
| 状态     | 待修复                             |

**问题描述**

文件中转上传小文件时失败，初步判断未对小文件做不分片处理。当前所有文件必须走"创建 → 分片上传 → 合并"三步流程，即使文件只有几 KB。

**已发现的严重 Bug**

分片上传端点的参数声明有误，导致文件数据无法正确接收：

```python
@router.post("/file/chunk")
async def upload_file_chunk(
    fileId: int = None,
    chunkIndex: int = None,
    chunk: bytes = None,       # ← 严重 Bug：无法正确接收文件数据
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
```

`chunk: bytes = None` 在 FastAPI 中无法正确接收二进制文件上传数据，应使用 `UploadFile` 或 `File(...)` 类型。

**其他问题**

1. 小文件无快捷上传路径，必须走三步流程
2. 分片完整性校验缺失（无哈希校验、无索引越界检查）
3. `complete_upload` 未校验已上传分片数是否等于总分片数
4. `chunks_uploaded` 并发递增非原子操作

**修复方案**

1. **修复分片上传参数**：将 `chunk: bytes` 改为 `chunk: UploadFile`
2. **新增小文件直接上传接口**：文件大小低于阈值（如 5MB）时，支持单次请求直接上传

   ```
   POST /api/transfer/file/upload
   Content-Type: multipart/form-data
   
   file: <文件数据>
   ```

3. 添加分片完整性校验（MD5/SHA256）
4. 合并前校验分片数量完整性
5. 使用数据库原子操作更新 `chunks_uploaded`

**验收标准**

- 小文件（< 5MB）可通过单次请求直接上传
- 大文件分片上传正常工作
- 分片数据完整性可验证
- 并发分片上传计数准确

---

### FEATURE-001：文件中转下载功能增强

| 属性     | 值                                 |
| -------- | ---------------------------------- |
| 严重程度 | 🟡 中                              |
| 影响范围 | 前端 + 后端                        |
| 模块     | 中转站                             |
| 状态     | 部分实现，需增强                   |

**功能描述**

文件中转模块需要完善的下载功能，支持断点续传、流式下载，以及跳转新标签页下载。

**当前实现现状**

后端已实现 `POST /api/transfer/file/download` 端点，支持：
- ✅ 流式下载（StreamingResponse，64KB 分块读取）
- ✅ 断点续传（Range 请求头解析，返回 206 Partial Content）

**仍需完善的部分**

1. **跳转新标签页下载**：当前使用 POST 方法，浏览器无法直接在新标签页打开下载。需要提供 GET 方式的下载链接

2. **文件名编码问题**：`Content-Disposition` 头中的文件名未做 RFC 5987 编码，中文文件名可能导致乱码

   ```python
   # 当前实现
   Content-Disposition: attachment; filename="中文文件名.txt"
   
   # 应改为
   Content-Disposition: attachment; filename="encoded.txt"; filename*=UTF-8''%E4%B8%AD%E6%96%87%E6%96%87%E4%BB%B6%E5%90%8D.txt
   ```

3. **缺少缓存支持**：未实现 ETag 和 Last-Modified，无法利用浏览器缓存

4. **缺少 GET 下载端点**：新增 `GET /api/transfer/file/download/{file_id}?token=<jwt_token>` 端点，支持浏览器直接访问下载

**修复方案**

1. 新增 GET 下载端点，通过查询参数传递 Token 进行认证
2. 修复文件名编码，使用 RFC 5987 标准处理非 ASCII 字符
3. 添加 ETag（基于文件 MD5）和 Last-Modified 响应头
4. 前端实现新标签页下载：`window.open(downloadUrl, '_blank')`

**验收标准**

- 点击下载可在浏览器新标签页直接下载文件
- 中文文件名显示正确
- 大文件下载支持断点续传
- 重复下载相同文件可利用缓存

---

## 优先级排序

| 优先级 | 编号       | 问题                                   | 原因                       |
| ------ | ---------- | -------------------------------------- | -------------------------- |
| P0     | BUG-005    | 文件上传小文件失败                     | 核心功能不可用，存在严重 Bug |
| P0     | BUG-004    | 同一任务多次执行结果丢失               | 数据丢失，影响执行记录完整性 |
| P1     | BUG-002    | WebSocket 日志连接失败                 | 影响用户体验，无法实时监控  |
| P1     | FEATURE-001 | 文件下载功能增强                      | 功能不完善，影响使用体验    |
| P2     | BUG-001    | 前端缺乏退出登录                       | 功能缺失但不影响核心流程    |
| P2     | BUG-003    | STRM 文件移动后残留（边缘场景）        | 已部分修复，仅边缘场景存在问题 |

---

## 修复计划

### 阶段一：紧急修复（P0）

1. **BUG-005**：修复分片上传参数声明，新增小文件直接上传接口
2. **BUG-004**：引入数据库行级锁或独立执行记录表，解决并发写入问题

### 阶段二：重要修复（P1）

3. **BUG-002**：WebSocket 添加身份验证、心跳机制，修复连接失败问题
4. **FEATURE-001**：新增 GET 下载端点，修复文件名编码，支持新标签页下载

### 阶段三：一般修复（P2）

5. **BUG-001**：前端实现退出登录功能
6. **BUG-003**：修复 `cloud_files` 为空时的清理逻辑，完善边缘场景处理
