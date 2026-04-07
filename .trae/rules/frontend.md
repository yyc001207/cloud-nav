---
alwaysApply: false
description: 编写前端代码时
---

# 前端项目规则

## 技术栈

- Vite 6.x、Vue 3.x、TypeScript 5.x
- Axios、Element Plus、Pinia、Vue Router 4.x、SCSS

## 项目结构

```
├── public/              # 静态资源
├── src/
│   ├── assets/          # 项目资源文件
│   ├── components/      # 通用组件
│   ├── views/           # 页面组件
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态管理
│   ├── api/             # API 接口
│   ├── utils/           # 工具函数
│   ├── types/           # TypeScript 类型定义
│   ├── styles/          # 全局样式
│   ├── App.vue          # 根组件
│   └── main.ts          # 入口文件
├── 配置文件              # ESLint、Prettier、TypeScript、Vite 配置
└── package.json         # 项目依赖
```

## 代码规范

- 代码风格: 2 个空格缩进，单引号优先，行尾不加分号
- 组件使用: 组合式 API，`<script setup>` 语法

## 开发规范

- 组件开发: props 和 emit 使用 TypeScript 类型定义
- API 调用: 统一放在 `src/api` 目录，使用 Axios 封装
- 状态管理: 使用 Pinia，按功能模块划分 store
- 路由管理: 使用 Vue Router 4，支持动态路由和路由守卫
- 样式管理: 全局样式放在 `src/styles` 目录
- 类型管理: TypeScript 类型定义统一放在 `src/types` 目录

## 构建和部署

- 构建命令: `yarn build`
- 预览命令: `yarn preview`
- 部署规范: 构建产物部署到静态文件服务器
