---
alwaysApply: false
description: 前端服务规则
---
# 前端服务规则

## 技术栈

- 框架：Vue 3
- 语言：TypeScript
- 构建工具：Vite
- HTTP客户端：Axios
- 状态管理：Pinia
- UI组件库：Element Plus

## 项目结构

```
frontend/
├── public/            # 静态资源
├── src/
│   ├── assets/        # 资源文件
│   ├── components/    # 通用组件
│   ├── views/         # 页面组件
│   ├── services/      # API服务
│   ├── stores/        # Pinia状态管理
│   ├── utils/         # 工具函数
│   ├── router/        # 路由配置
│   ├── types/         # TypeScript类型
│   ├── App.vue        # 根组件
│   └── main.ts        # 入口文件
├── package.json       # 依赖管理
├── vite.config.ts     # 构建配置
├── tsconfig.json      # TypeScript配置
└── .env               # 环境变量
```

## 编码规范

- 代码风格：ESLint + Prettier
- 命名：组件PascalCase，变量camelCase，常量UPPER_CASE，接口I开头PascalCase
- 注释：复杂逻辑使用JSDoc
- TypeScript：类型注解，接口定义，避免any，使用泛型

## API调用

- 统一封装函数
- 处理请求状态
- 错误处理与重试
- TypeScript类型定义

## Vue3组件

- Composition API
- `<script setup>`语法
- 合理使用ref/reactive
- Props和Emits类型定义

## Pinia状态管理

- 按模块划分store
- TypeScript类型定义
- 单向数据流
- async/await异步操作

## 样式规范

- 全局背景：#1a1a1a
- 主题色：#2ecc71
- 文本颜色：#e5eaf3
- Element UI：Primary按钮使用主题色，其他保持默认
- SCSS变量：避免硬编码，使用CSS变量
- 优先级：全局CSS变量 > Element UI变量 > 局部样式

## 响应式设计

- 适配多屏幕
- CSS Grid/Flexbox布局
- PC端优先

## 性能优化

- 组件懒加载
- 图片优化
- 代码分割
- 缓存策略

## 部署与开发

- 构建产物优化
- Git版本控制
- 代码审查
- 自动化测试
