# ⚙️ 配置更新说明

## 📌 重要更新

Redis和数据库配置已更新为从配置文件读取，不再硬编码。

## 🔧 配置文件位置

```
config/conf/dev/backend/settings.json  # 开发环境
config/conf/prd/backend/settings.json  # 生产环境
```

## 📝 配置文件格式

```json
{
    "mysql": {
        "user": "root",
        "password": "your_password",
        "host": "mysql_host",
        "port": 3306,
        "db": "database_name",
        "charset": "utf8mb4",
        "timezone": "asia/shanghai",
        "init_command": ""
    },
    "redis": {
        "host": "redis_host",
        "port": 6380,
        "db": 0,
        "password": "redis_password"
    }
}
```

## 🚀 快速验证

### 1. 检查配置文件

```bash
# 开发环境
cat config/conf/dev/backend/settings.json

# 生产环境
cat config/conf/prd/backend/settings.json
```

### 2. 测试配置加载

```bash
# 启动Django shell
python manage.py shell

# 测试缓存
>>> from backend.utils.cache import CacheManager
>>> CacheManager.set('test', 'value', 60)
>>> print(CacheManager.get('test'))
value
```

### 3. 查看加载日志

启动后端服务时会显示：

```
Loaded Redis config from config/conf/dev/backend/settings.json: redis:6380/0
Loaded MySQL config from config/conf/dev/backend/settings.json: mysql:3306/dev_yundisoft
```

## 🔄 环境切换

通过`EDU_ENV`环境变量控制：

```bash
# 开发环境（默认）
export EDU_ENV=DEV

# 生产环境
export EDU_ENV=PRD
```

在`docker-compose.yml`中：

```yaml
services:
  backend:
    environment:
      - EDU_ENV=DEV  # 或 PRD
```

## ✅ 更新的文件

1. **backend/backend/cache_settings.py**
   - 从配置文件读取Redis配置
   - 自动根据环境选择配置文件

2. **backend/backend/database_settings.py**
   - 从配置文件读取MySQL配置
   - 提供连接池优化配置

## ⚠️ 注意事项

1. **配置文件不要提交到git**
   - 包含敏感信息（密码）
   - 已在.gitignore中

2. **环境变量优先级**
   - 配置文件优先
   - 环境变量作为fallback

3. **异常处理**
   - 配置加载失败会使用默认值
   - 不会导致应用崩溃

## 📚 详细文档

完整配置说明请查看：`CONFIG_INTEGRATION_GUIDE.md`

---

**更新完成，无需额外配置，开箱即用！** ✨

