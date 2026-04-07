---
alwaysApply: false
description: 后端服务规则
---

# 后端服务规则

## 技术栈

- 语言：Python 3.8+
- Web框架：FastAPI
- 数据库：MongoDB
- 认证：JWT

## 统一响应格式

- **登录接口**：{"code": 200, "msg": "", "token": "xxxx"}
- **普通数据**：{"code": 200, "msg": "", "data": []|{}}
- **分页接口**：{"code": 200, "msg": "", "list": [], "total": 0}
- 所有字段使用小驼峰命名

## 技术架构

- FastAPI构建RESTful API
- MongoDB数据存储，实现模型映射
- 模块化组织，按业务领域划分
- JWT认证保护授权接口

## 核心模块

- **认证模块**：登录接口，JWT token生成与验证
- **基础数据**：CRUD接口，数据验证和错误处理
- **分页数据**：分页查询，支持排序和筛选

## 实现标准

- 代码符合PEP 8规范
- 请求参数验证和错误处理
- 完整日志记录：
  - 记录API请求响应
  - 错误日志单独存储
  - 多级别日志（DEBUG-INFO-WARNING-ERROR-CRITICAL）
  - 包含时间戳、级别、模块名、消息
- FastAPI自动生成API文档
- 基本单元测试

## 部署准备

- requirements.txt依赖管理
- 环境变量配置管理
- 启动脚本和部署说明
