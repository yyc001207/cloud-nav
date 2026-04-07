---
alwaysApply: false
description: 在前后端接口开发、对接过程中遵循
---

# 前后端数据接口规范

## 通用规则

- 响应格式：所有接口返回包含 `code`（状态码）、`msg`（提示信息）字段
- 请求方法：所有接口均使用 POST 请求

## 接口类型定义

### 1. 登录接口（获取token）

- 功能：用户登录并获取身份认证令牌
- 请求参数：`userName`（String，必填）、`password`（String，必填）
- 响应结构：`{code: Number, msg: String, token: String}`

### 2. 普通接口

- 功能：获取非分页的业务数据
- 请求参数：根据具体业务需求确定
- 响应结构：`{code: Number, msg: String, data: any}`

### 3. 分页接口

- 功能：获取分页数据
- 请求参数：`pageNum`（Number，必填，页码从 1 开始）、`pageSize`（Number，必填，每页条数）
- 响应结构：`{code: Number, msg: String, data: Array, total: Number}`

## 状态码规范

- 200：操作成功
- 400：请求参数错误
- 401：未授权或登录失效
- 403：权限不足
- 404：资源不存在
- 500：服务器内部错误

## 数据类型约束

- 字符串：根据业务需求限制长度，特殊字符需转义
- 数字：使用 Number 类型，小数保留适当位数
- 布尔：使用 Boolean 类型，值为 true/false
- 数组：元素类型和长度根据业务需求确定
