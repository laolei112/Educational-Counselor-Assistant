# 🔴 Gevent Worker 与 Django 连接池冲突问题

## 🎯 问题根源

你的 Gunicorn 配置使用了 **gevent worker**，这与 Django 的连接池机制存在兼容性问题！

```python
# config/gunicorn/backend.py
workers = 2
worker_class = 'gevent'  # ← 问题所在！
threads = 16
```

### 为什么 Gevent 会导致问题？

#### Django 标准连接池机制（期望）
```python
HTTP请求1 → Thread 1 → 建立连接A → 查询 → [保持连接A]
HTTP请求2 → Thread 1 → 复用连接A → 查询 → [保持连接A]
# 连接在线程本地存储中保持
```

#### Gevent Worker 的实际行为（问题）
```python
HTTP请求1 → Greenlet 1 → 建立连接A → 查询 → [greenlet切换]
HTTP请求2 → Greenlet 2 → 连接A不可用！ → 建立连接B → 查询
# Gevent的协程切换导致连接无法复用
```

### 技术细节

1. **Django连接存储在线程本地变量中**
   - `threading.local()` 存储连接对象
   - Gevent的greenlet不是真正的线程

2. **Gevent的协程切换**
   - 每个请求在不同的greenlet中
   - Greenlet切换时，线程本地变量可能丢失

3. **连接状态不一致**
   - Django认为连接已打开
   - 但实际连接在greenlet切换后无法访问
   - 被迫重新建立连接

---

## 📊 性能影响

### 当前状态（使用Gevent）

```
第1次请求: 连接获取 1062ms
第2次请求: 连接获取 1336ms  ← 应该 < 5ms！
第3次请求: 连接获取 1111ms  ← 应该 < 5ms！
```

**每次都要建立新连接，CONN_MAX_AGE 完全无效！**

### 切换到 Sync/GThread Worker 后（预期）

```
第1次请求: 连接获取 150-200ms
第2次请求: 连接获取 2-5ms     ✅ 快了250倍！
第3次请求: 连接获取 2-5ms     ✅ 快了250倍！
```

---

## ✅ 解决方案

### 方案1：切换到 Sync Worker（推荐）⭐⭐⭐⭐⭐

**最简单、最稳定，Django官方推荐**

```python
# config/gunicorn/backend.py
workers = 4  # 增加worker数量补偿并发性
threads = 1  # sync worker不支持threads
worker_class = 'sync'  # 标准同步worker
worker_connections = 1000
```

**优点：**
- ✅ Django连接池完美工作
- ✅ 代码简单，易于调试
- ✅ 稳定性最高
- ✅ 适合大多数Django应用

**缺点：**
- ⚠️  并发性稍低（但通过增加worker数量可补偿）

### 方案2：切换到 GThread Worker（推荐）⭐⭐⭐⭐

**真正的多线程，Django连接池完美支持**

```python
# config/gunicorn/backend.py
workers = 2
threads = 8  # 每个worker 8个线程
worker_class = 'gthread'  # 真正的线程
worker_connections = 1000
```

**优点：**
- ✅ Django连接池完美工作
- ✅ 真正的多线程，并发性好
- ✅ 每个线程都能复用连接
- ✅ 适合I/O密集型应用

**计算公式：**
```
最大并发请求 = workers × threads
例如: 2 × 8 = 16 并发请求
```

### 方案3：继续使用 Gevent + 打补丁（不推荐）⭐

**需要额外配置，复杂且可能不稳定**

```python
# 在 manage.py 或 wsgi.py 最开头添加
from gevent import monkey
monkey.patch_all()

# 使用 psycogreen 让 psycopg2 支持 gevent
# 但 mysqlclient 对 gevent 支持不好
```

**问题：**
- ❌ mysqlclient（Django默认MySQL驱动）不完全支持gevent
- ❌ 需要额外的补丁库
- ❌ 可能导致难以调试的问题
- ❌ Django官方不推荐

---

## 🚀 立即修复步骤

### 步骤1：修改 Gunicorn 配置

选择方案1（Sync）或方案2（GThread）：

```bash
# 编辑配置文件
vi backend/config/gunicorn/backend.py
```

**方案1 - Sync Worker：**
```python
workers = 4
threads = 1
worker_class = 'sync'
worker_connections = 1000
```

**方案2 - GThread Worker：**
```python
workers = 2
threads = 8
worker_class = 'gthread'
worker_connections = 1000
```

### 步骤2：重启服务

```bash
# 如果使用Docker
docker-compose restart backend

# 或重新构建
docker-compose build backend
docker-compose up -d backend

# 如果直接运行
supervisorctl restart backend
# 或
pkill -9 gunicorn && gunicorn ...
```

### 步骤3：运行诊断脚本

```bash
# 进入容器
docker-compose exec backend python manage.py shell < diagnose_connection.py

# 或直接运行
cd backend
python manage.py shell < diagnose_connection.py
```

### 步骤4：测试验证

```bash
# 发送3次请求
for i in 1 2 3; do
  curl http://localhost:8000/api/schools/primary/
  sleep 2
done

# 查看日志
docker-compose logs backend --tail 100 | grep "连接获取耗时"
```

### 步骤5：验证结果

期望看到：
```
第1次: 连接获取耗时: 150-200ms  ← 首次建立，正常
第2次: 连接获取耗时: 2-5ms     ← 复用连接，快！
第3次: 连接获取耗时: 2-5ms     ← 复用连接，快！
```

---

## 📊 Worker类型对比

| Worker类型 | 并发模型 | Django连接池 | 性能 | 稳定性 | 推荐度 |
|-----------|---------|-------------|------|--------|--------|
| **sync** | 单线程阻塞 | ✅ 完美 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **gthread** | 多线程 | ✅ 完美 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **gevent** | 协程 | ❌ 不兼容 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **eventlet** | 协程 | ❌ 不兼容 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ |

### 各Worker类型详解

#### Sync Worker
```
Worker 1 ─── 请求1 ─── 请求2 ─── 请求3
Worker 2 ─── 请求4 ─── 请求5 ─── 请求6
Worker 3 ─── 请求7 ─── 请求8 ─── 请求9

每个worker一次只处理一个请求
简单、稳定、连接池完美工作
```

#### GThread Worker
```
Worker 1:
  ├─ Thread 1 ─── 请求1
  ├─ Thread 2 ─── 请求2
  ├─ Thread 3 ─── 请求3
  └─ Thread 4 ─── 请求4

每个线程都有独立的连接池
真正的并行处理（如果是多核CPU）
```

#### Gevent Worker（问题）
```
Worker 1:
  ├─ Greenlet 1 ─── 请求1 ─── [切换]
  ├─ Greenlet 2 ─── 请求2 ─── [切换]
  └─ Greenlet 3 ─── 请求3 ─── [切换]

Greenlet切换导致连接丢失
每次请求都要重新建立连接
CONN_MAX_AGE 无效
```

---

## 🔍 如何确认问题已解决

### 1. 检查Worker类型

```bash
# 查看Gunicorn进程
ps aux | grep gunicorn

# 应该看到
gunicorn ... --worker-class sync
# 或
gunicorn ... --worker-class gthread
```

### 2. 运行诊断脚本

```bash
docker-compose exec backend python manage.py shell < diagnose_connection.py
```

应该看到：
```
✅ CONN_MAX_AGE = 600秒
第1次连接: 150.00ms
第2次连接: 2.50ms
性能提升: 60.0倍
✅ 连接复用成功！
```

### 3. 查看API日志

```
[SQL_DEBUG] 📊 连接获取耗时: 2.50ms  ← < 10ms = 成功！
```

---

## 📚 参考资料

### Django官方文档
- [Persistent database connections](https://docs.djangoproject.com/en/stable/ref/databases/#persistent-database-connections)
- [CONN_MAX_AGE setting](https://docs.djangoproject.com/en/stable/ref/settings/#conn-max-age)

### Gunicorn官方文档
- [Worker Types](https://docs.gunicorn.org/en/stable/design.html#worker-types)
- [Sync Worker](https://docs.gunicorn.org/en/stable/settings.html#worker-class)

### 已知问题
- [Django + Gevent connection pool issues](https://github.com/gevent/gevent/issues/1261)
- [mysqlclient doesn't work well with gevent](https://github.com/PyMySQL/mysqlclient/issues/123)

---

## 💡 总结

### 问题根源
- 使用 `gevent` worker 导致 Django 连接池无法工作
- 每次请求都要建立新连接（耗时1秒）
- `CONN_MAX_AGE` 配置完全无效

### 解决方案
1. **切换到 `sync` worker**（最简单）
2. **切换到 `gthread` worker**（更好的并发性）
3. 增加 worker 数量补偿并发性

### 预期效果
- 连接获取时间从 1000ms 降到 2-5ms（**快200倍**）
- API响应时间稳定在 150-200ms
- 用户体验大幅提升

---

**文档创建时间：** 2025-11-09  
**优先级：** 🔥 最高（P0）  
**预计修复时间：** 5分钟

