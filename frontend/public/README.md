# Public 静态资源目录

## 目录说明

此目录用于存放不需要经过构建处理的静态资源文件。

## 特点

- ✅ **直接访问**: 文件会被原样复制到 `dist` 根目录
- ✅ **不经过构建**: 不会被 Vite 处理或打包
- ✅ **根路径映射**: `public/favicon.jpg` → `/favicon.jpg`
- ✅ **性能优化**: 减少构建时间，适合大文件

## 当前文件

### favicon.jpg
- **用途**: 网站图标（Favicon）
- **尺寸**: 45KB
- **引用位置**: `index.html`
- **访问路径**: `/favicon.jpg`

## 使用规则

### 应该放在 public 的文件
- ✅ Favicon 图标
- ✅ Robots.txt
- ✅ Sitemap.xml
- ✅ Web App Manifest
- ✅ 不需要处理的大型文件
- ✅ 第三方静态资源

### 不应该放在 public 的文件
- ❌ 组件中使用的图片 → 放在 `src/assets/`
- ❌ 需要优化的图片 → 放在 `src/assets/`
- ❌ CSS/JS 文件 → 放在 `src/` 中

## 最佳实践

### 1. 命名规范
- 使用小写字母
- 使用连字符分隔 (kebab-case)
- 避免空格和特殊字符

### 2. 组织结构
```
public/
├── favicon.jpg          # 网站图标
├── robots.txt          # 搜索引擎爬虫规则
├── manifest.json       # PWA 配置
└── assets/             # 其他静态资源
    ├── images/
    └── documents/
```

### 3. 引用方式
```html
<!-- 在 HTML 中 -->
<link rel="icon" href="/favicon.jpg">

<!-- 在 JS 中不推荐引用 public 文件 -->
<!-- 应该使用 src/assets/ 中的文件 -->
```

## 注意事项

1. ⚠️ **不要在代码中导入**: public 目录的文件不应该被 import
2. ⚠️ **使用绝对路径**: 始终使用 `/` 开头的绝对路径
3. ⚠️ **不会被打包**: 文件不会经过优化、压缩或重命名
4. ⚠️ **部署时保留**: 确保部署脚本包含此目录

## 更多信息

查看 Vite 官方文档：
https://vitejs.dev/guide/assets.html#the-public-directory

