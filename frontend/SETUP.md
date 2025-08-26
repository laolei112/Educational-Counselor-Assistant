# 项目设置指南

## 系统要求

- Node.js 18+ 
- npm 或 yarn 或 pnpm

## 快速开始

### 1. 安装 Node.js

如果您还没有安装 Node.js，请访问 [https://nodejs.org/](https://nodejs.org/) 下载并安装最新的 LTS 版本。

### 2. 安装项目依赖

在 `frontend` 目录下运行以下命令：

```bash
# 使用 npm
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

### 3. 启动开发服务器

```bash
# 使用 npm
npm run dev

# 或使用 yarn
yarn dev

# 或使用 pnpm
pnpm dev
```

### 4. 打开浏览器

开发服务器启动后，通常会在 `http://localhost:3000` 提供服务。

## 项目功能

✅ **已实现的功能：**
- 学校信息展示（小学/中学切换）
- 学校统计数据（总数、开放申请数）
- 学校卡片展示（包含所有图片中的信息）
- 响应式设计（支持移动端）
- 学校分类标签
- 申请状态标识
- 学费、地区、校网信息
- 升学衔接信息

## 技术特性

- **Vue 3 Composition API** - 现代化的响应式框架
- **TypeScript** - 类型安全
- **Pinia** - 轻量级状态管理
- **Vite** - 极速构建工具
- **响应式设计** - 完美适配各种设备

## 目录结构解释

```
frontend/
├── src/
│   ├── components/
│   │   └── SchoolCard.vue    # 学校信息卡片组件
│   ├── stores/
│   │   └── school.ts         # 学校数据状态管理
│   ├── types/
│   │   └── school.ts         # TypeScript 类型定义
│   ├── views/
│   │   └── Home.vue          # 主页面
│   ├── router/
│   │   └── index.ts          # 路由配置
│   ├── App.vue               # 根组件
│   ├── main.ts               # 应用入口点
│   └── style.css             # 全局样式
├── index.html                # HTML 模板
├── package.json              # 依赖和脚本配置
├── vite.config.ts           # Vite 构建配置
└── tsconfig.json            # TypeScript 配置
```

## 常见问题

**Q: 如果遇到依赖安装问题怎么办？**
A: 尝试删除 `node_modules` 文件夹和 `package-lock.json` 文件，然后重新运行 `npm install`。

**Q: 如何修改学校数据？**
A: 编辑 `src/stores/school.ts` 文件中的 `schools` 数组。

**Q: 如何添加新的学校类别？**
A: 在 `src/types/school.ts` 中更新 `category` 类型，然后在组件中添加对应的样式。

**Q: 如何部署到生产环境？**
A: 运行 `npm run build` 生成 `dist` 目录，然后将该目录部署到您的服务器。 