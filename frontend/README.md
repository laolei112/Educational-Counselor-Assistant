# 香港升学助手 - 前端应用

基于 Vue 3 + Vite + TypeScript 构建的香港学校信息展示应用。

## 功能特性

- 🏫 学校信息展示（小学/中学）
- 📊 学校统计数据
- 🏷️ 学校分类标签（名校联盟、传统名校、直资学校等）
- 📍 学校位置和校网信息
- 💰 学费信息展示
- 🎓 升学衔接信息
- 📱 响应式设计，支持移动端
- 🔗 **API集成** - 支持从后端动态获取数据
- 📡 **Mock模式** - 内置静态数据，支持离线开发
- ⚡ **加载状态** - 优雅的加载和错误处理
- 🔄 **数据刷新** - 支持重试和数据更新

## 技术栈

- **Vue 3** - 渐进式前端框架
- **Vite** - 快速构建工具
- **TypeScript** - 类型安全的JavaScript
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API服务层
│   │   ├── config.ts     # API配置
│   │   ├── request.ts    # HTTP请求工具
│   │   ├── school.ts     # 学校API服务
│   │   ├── types.ts      # API类型定义
│   │   └── index.ts      # API模块入口
│   ├── components/        # 组件目录
│   │   └── SchoolCard.vue # 学校卡片组件
│   ├── stores/           # 状态管理
│   │   └── school.ts     # 学校数据store（已集成API）
│   ├── types/            # 类型定义
│   │   └── school.ts     # 学校相关类型
│   ├── views/            # 页面组件
│   │   └── Home.vue      # 主页（含加载/错误状态）
│   ├── router/           # 路由配置
│   │   └── index.ts      # 路由入口
│   ├── App.vue           # 根组件
│   ├── main.ts           # 应用入口
│   └── style.css         # 全局样式
├── index.html            # HTML模板
├── package.json          # 项目配置
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
└── API_接口文档.md        # API接口规范文档
```

## 安装和运行

1. 安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

4. 预览生产版本：
```bash
npm run preview
```

## 开发说明

### 数据获取模式

应用支持两种数据获取模式：

1. **Mock模式**（默认）- 使用内置静态数据，适用于开发和演示
2. **API模式** - 从后端API动态获取数据

### 配置API

1. 设置环境变量（可选，创建 `.env.local` 文件）：
```bash
# API基础地址
VITE_API_BASE_URL=http://localhost:8080/api

# 禁用Mock模式以使用真实API
VITE_ENABLE_MOCK=false
```

2. 确保后端API按照 `API_接口文档.md` 中的规范实现

### 开发特性

- **Mock数据** - 内置完整测试数据，无需后端即可开发
- **错误处理** - 自动回退到Mock数据，保证应用可用性
- **加载状态** - 优雅的loading和错误提示
- **TypeScript** - 完整的类型定义和API接口规范
- **响应式设计** - 适配移动端设备

### 目录说明

- `src/api/` - API服务层，处理所有HTTP请求
- `src/stores/school.ts` - 学校数据状态管理，已集成API调用
- `src/types/school.ts` - 学校数据类型定义
- `src/components/` - 可复用UI组件
- `API_接口文档.md` - 完整的API接口规范

## 数据模型

学校信息包含以下字段：
- 基本信息：名称、类型（小学/中学）
- 分类：名校联盟、传统名校、直资学校等
- 学术指标：Band1比例
- 申请状态：开放申请、申请截止、即将截止
- 地理信息：地区、校网
- 费用：学费
- 其他：性别类型、衔接学校/大学

## 许可证

MIT License 