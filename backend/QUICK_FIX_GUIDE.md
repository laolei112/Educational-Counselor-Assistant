# ⚡ 快速修复指南

## 🎯 问题

COUNT查询耗时 **1145ms**，但数据库实际执行只需 **14ms**。

**原因：** 每次HTTP请求都要建立新的数据库连接，浪费约1秒。

---

## ✅ 已修复

已在 `backend/settings.py` 中添加：

```python
"CONN_MAX_AGE": 600,  # 连接复用10分钟
"CONN_HEALTH_CHECKS": True,
```

---

## 🚀 立即生效（3步）

### 1️⃣ 重启后端服务

```bash
docker-compose restart backend
```

### 2️⃣ 等待5秒

```bash
sleep 5
```

### 3️⃣ 测试性能

```bash
# 发送请求
curl http://localhost:8000/api/schools/primary/

# 查看日志
docker-compose logs backend --tail 50 | grep "SQL_DEBUG"
```

---

## 📊 期望结果

### 修复前 ❌
```
连接获取耗时: 1000ms  ← 很慢！
网络+开销耗时: 1006ms
总耗时: 1145ms
```

### 修复后 ✅
```
连接获取耗时: 2ms     ← 快了500倍！
网络+开销耗时: 8ms
总耗时: 24ms          ← 快了47倍！
```

---

## 🔍 如何确认修复生效？

在日志中看到：

```
[SQL_DEBUG] 📊 连接获取耗时: 2.00ms     ✅ < 10ms = 成功
[SQL_DEBUG] 📊 网络+开销耗时: 8.00ms    ✅ < 20ms = 成功
[SQL_DEBUG] 📊 总耗时: 24.00ms          ✅ < 50ms = 成功
```

**如果第二次、第三次请求的连接获取耗时都 < 10ms，说明连接池生效！**

---

## ❌ 如果还是很慢？

### 检查配置是否生效：

```bash
docker-compose exec backend python manage.py shell
```

在shell中运行：
```python
from django.db import connection
print(connection.settings_dict.get('CONN_MAX_AGE'))
# 应该输出: 600
# 如果是 0 或 None，说明配置未生效
```

### 如果输出不是600：

1. 确认代码已更新：
   ```bash
   docker-compose exec backend cat backend/settings.py | grep CONN_MAX_AGE
   ```

2. 重新构建镜像（如果使用Docker）：
   ```bash
   docker-compose build backend
   docker-compose up -d backend
   ```

---

## 📞 需要帮助？

查看详细文档：
- `CONNECTION_POOL_FIX.md` - 完整的修复说明
- `PERFORMANCE_DIAGNOSIS.md` - 性能问题诊断
- 运行 `./test_db_connection.sh` - 自动化测试

---

**预期性能提升：92%** 🚀

