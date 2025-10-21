# 🚀 小学和中学接口性能优化部署指南

## 📋 更新说明

本次优化针对**实际使用的小学和中学接口**进行性能提升，通用接口已废弃。

### 优化接口列表

**小学接口**：
- `GET /api/schools/primary/` - 小学列表
- `GET /api/schools/primary/{id}/` - 小学详情  
- `GET /api/schools/primary/stats/` - 小学统计
- `GET /api/schools/primary/filters/` - 小学筛选器

**中学接口**：
- `GET /api/schools/secondary/` - 中学列表
- `GET /api/schools/secondary/{id}/` - 中学详情
- `GET /api/schools/secondary/stats/` - 中学统计

## 🎯 优化内容

### 1. Redis缓存层
- ✅ 列表查询缓存（5分钟）
- ✅ 详情查询缓存（30分钟）
- ✅ 统计数据缓存（1小时）
- ✅ 筛选器数据缓存（1小时）

### 2. 数据库优化
- ✅ 为`tb_primary_schools`表添加8个索引
- ✅ 为`tb_secondary_schools`表添加9个索引
- ✅ 简化搜索逻辑（只搜索school_name和district）
- ✅ COUNT查询结果缓存

### 3. 查询优化
- ✅ 减少不必要的字段查询
- ✅ 优化排序逻辑
- ✅ 使用切片代替Paginator

## 📦 新增文件

```
backend/
├── backend/
│   ├── api/
│   │   └── schools/
│   │       ├── primary_views_optimized.py      # 优化后的小学视图
│   │       └── secondary_views_optimized.py    # 优化后的中学视图
│   └── utils/
│       └── cache.py                            # 缓存工具类（共用）
├── common/
│   └── db/
│       └── optimize_primary_secondary_indexes.sql  # 索引优化脚本
└── test_performance_primary_secondary.py       # 性能测试脚本
```

## 🚀 快速部署（5分钟）

### 步骤1：确保依赖已安装

```bash
cd backend

# django-redis已在requirements.txt中，确认安装
pip show django-redis
```

### 步骤2：执行数据库索引优化

```bash
# 在服务器上执行
docker exec -i edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft < common/db/optimize_primary_secondary_indexes.sql
```

**预期输出**：
```
Query OK, 0 rows affected
Query OK, 0 rows affected
...
```

### 步骤3：验证索引创建

```bash
# 进入MySQL容器
docker exec -it edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft

# 查看小学表索引
SHOW INDEX FROM tb_primary_schools;

# 查看中学表索引
SHOW INDEX FROM tb_secondary_schools;

# 退出
exit
```

### 步骤4：重启后端服务

```bash
# 在项目根目录
docker-compose restart backend

# 查看启动日志
docker-compose logs -f backend
```

### 步骤5：性能测试

```bash
# 运行完整测试套件
cd backend
python test_performance_primary_secondary.py
```

## 🧪 测试验证

### 手动测试

```bash
# 1. 测试小学列表（首次请求）
time curl "http://9.135.78.24/api/schools/primary/?page=1&pageSize=20"

# 2. 测试小学列表（缓存命中）
time curl "http://9.135.78.24/api/schools/primary/?page=1&pageSize=20"

# 3. 测试中学列表（首次请求）
time curl "http://9.135.78.24/api/schools/secondary/?page=1&pageSize=20"

# 4. 测试中学列表（缓存命中）
time curl "http://9.135.78.24/api/schools/secondary/?page=1&pageSize=20"

# 5. 测试小学统计
time curl "http://9.135.78.24/api/schools/primary/stats/"

# 6. 测试小学筛选器
time curl "http://9.135.78.24/api/schools/primary/filters/"
```

### 查看缓存状态

```bash
# 查看Redis中的缓存keys
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj KEYS "edu:*"

# 应该看到类似的keys:
# edu:primary:list:xxxxx
# edu:secondary:list:xxxxx
# edu:primary:stats:xxxxx
# ...

# 查看缓存统计
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj INFO stats
```

## 📊 性能对比

### 优化前

| 接口 | 响应时间 | 数据库查询 |
|------|---------|-----------|
| 小学列表 | 800-1200ms | 5-10次 |
| 中学列表 | 800-1200ms | 5-10次 |
| 统计接口 | 500-800ms | 3-5次 |

### 优化后（预期）

| 接口 | 首次请求 | 缓存命中 | 数据库查询 |
|------|---------|---------|-----------|
| 小学列表 | 100-300ms ⚡ | 10-50ms 🚀 | 0-2次 |
| 中学列表 | 100-300ms ⚡ | 10-50ms 🚀 | 0-2次 |
| 统计接口 | 50-150ms ⚡ | 5-30ms 🚀 | 0-1次 |

**提升效果**：
- 响应时间降低：**70-90%**
- 数据库压力降低：**80-90%**
- 并发能力提升：**5-10倍**

## 🔧 配置说明

### URL路由配置

文件：`backend/backend/api/schools/urls.py`

```python
# 小学接口（使用优化后的视图）
re_path(r'^primary/$', primary_schools_list_optimized, ...),
re_path(r'^primary/stats/$', primary_schools_stats_optimized, ...),
re_path(r'^primary/filters/$', primary_schools_filters_optimized, ...),
re_path(r'^primary/(?P<school_id>\d+)/$', primary_school_detail_optimized, ...),

# 中学接口（使用优化后的视图）
re_path(r'^secondary/$', secondary_schools_list_optimized, ...),
re_path(r'^secondary/stats/$', secondary_schools_stats_optimized, ...),
re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_school_detail_optimized, ...),
```

### 缓存配置

使用共用的缓存工具类：`backend/backend/utils/cache.py`

**缓存策略**：
- 列表数据：5分钟（`TIMEOUT_SHORT = 300`）
- 详情数据：30分钟（`TIMEOUT_MEDIUM = 1800`）
- 统计数据：1小时（`TIMEOUT_LONG = 3600`）
- 筛选器数据：1小时（`TIMEOUT_LONG = 3600`）

### 数据库索引

**小学表索引**：
- 单字段索引：district, category, school_net, gender, religion, teaching_language
- 复合索引：district+category, district+school_net, category+gender
- 前缀索引：school_name(20)

**中学表索引**：
- 单字段索引：district, category, school_group, gender, religion
- 复合索引：district+category, district+school_group, category+school_group, school_group+gender
- 前缀索引：school_name(20)

## 🔍 监控和维护

### 查看性能指标

```bash
# 查看响应头中的性能指标
curl -i "http://9.135.78.24/api/schools/primary/?page=1"

# 响应头示例：
# X-Request-Duration: 0.123s
# X-Database-Queries: 2
# X-Database-Time: 0.045s
# X-Cache-Hit: HIT
```

### 清除缓存

```bash
# 使用Django管理命令
python manage.py clear_cache --all

# 或直接清空Redis
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj FLUSHDB
```

### 查看慢查询

```bash
# 查看后端日志中的慢查询警告
docker-compose logs backend | grep "Slow request"

# 查看MySQL慢查询日志
docker logs edu_mysql | grep "Query_time"
```

## 🐛 故障排查

### 问题1：缓存不生效

**症状**：每次请求都很慢，X-Cache-Hit一直是MISS

**排查步骤**：
```bash
# 1. 检查Redis是否运行
docker ps | grep redis

# 2. 测试Redis连接
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj PING

# 3. 查看缓存keys
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj KEYS "edu:*"

# 4. 在Django shell中测试
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> print(cache.get('test'))
```

### 问题2：查询仍然很慢

**排查步骤**：
```sql
-- 1. 确认索引已创建
SHOW INDEX FROM tb_primary_schools;
SHOW INDEX FROM tb_secondary_schools;

-- 2. 分析查询计划
EXPLAIN SELECT * FROM tb_primary_schools WHERE district='中西区' LIMIT 20;

-- 3. 更新表统计信息
ANALYZE TABLE tb_primary_schools;
ANALYZE TABLE tb_secondary_schools;

-- 4. 优化表
OPTIMIZE TABLE tb_primary_schools;
OPTIMIZE TABLE tb_secondary_schools;
```

### 问题3：内存不足

**症状**：Redis或MySQL内存溢出

**解决方案**：
```bash
# 查看Redis内存使用
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj INFO memory

# 清理缓存
docker exec -it edu_redis redis-cli -p 6380 -a HaWSD*9265tZYj FLUSHDB

# 调整Redis最大内存（在docker-compose.yml中）
command: redis-server --port 6380 --requirepass HaWSD*9265tZYj --maxmemory 512mb
```

## 📈 性能优化检查清单

部署后请检查以下项目：

- [ ] 数据库索引已创建（小学表和中学表）
- [ ] Redis服务正常运行
- [ ] 后端服务已重启
- [ ] 缓存keys可以正常创建
- [ ] 首次请求响应时间 < 500ms
- [ ] 缓存命中响应时间 < 100ms
- [ ] 缓存命中率 > 50%
- [ ] 无慢查询警告（>1s）
- [ ] 接口返回数据正确
- [ ] 性能测试通过

## 🎯 后续优化建议

如果性能仍不满意，可以考虑：

1. **增加缓存预热**
   - 在低峰期预先加载热点数据到缓存

2. **实现增量更新**
   - 数据更新时，只清除相关缓存

3. **使用CDN**
   - 对静态内容使用CDN加速

4. **数据库读写分离**
   - 配置MySQL主从复制

5. **使用全文索引**
   - 如果搜索功能使用频繁，考虑Elasticsearch

## 📞 支持

如果遇到问题：
1. 查看本文档的故障排查章节
2. 检查日志文件
3. 运行性能测试脚本诊断

---

**更新日期**: 2025-10-21  
**版本**: 2.0（针对小学和中学接口）

