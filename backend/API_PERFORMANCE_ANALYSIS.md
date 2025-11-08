# API性能问题分析报告

## 问题描述

`/api/schools/primary/?page=1&pageSize=20` 接口请求耗时波动很大，从几百毫秒到几秒不等。

## 性能瓶颈分析

### 1. **JSON_EXTRACT在排序中的性能问题** ⚠️ 最严重

**问题位置**：`primary_views.py` 第179-183行

```python
queryset = queryset.extra(
    select={
        'band1_rate': "CAST(JSON_EXTRACT(promotion_info, '$.band1_rate') AS DECIMAL(5,2))"
    }
).order_by('-band1_rate', 'school_name')
```

**问题分析**：
- 每次排序都要对**每一行**执行 `JSON_EXTRACT` 操作
- JSON字段无法建立索引，导致全表扫描
- 对于有数百条记录的表，这会导致：
  - 全表扫描（Full Table Scan）
  - 每行都要解析JSON
  - 无法使用索引优化排序

**性能影响**：
- 无过滤条件时：需要扫描所有记录并提取JSON
- 有过滤条件时：先过滤，再对结果集执行JSON提取
- 耗时：**500ms - 3000ms+**（取决于数据量和过滤条件）

### 2. **Paginator.count() 的COUNT查询** ⚠️

**问题位置**：`primary_views.py` 第186-198行

```python
paginator = Paginator(queryset, page_size)
schools_page = paginator.get_page(page)
# ...
"total": paginator.count,  # 这里会执行 COUNT(*) 查询
```

**问题分析**：
- `paginator.count` 会执行 `SELECT COUNT(*) FROM ...` 查询
- 对于复杂的查询（包含JSON_EXTRACT），COUNT查询也需要执行相同的操作
- 即使只需要20条数据，也要先计算总数

**性能影响**：
- COUNT查询需要扫描所有匹配的记录
- 包含JSON_EXTRACT时，COUNT也会很慢
- 耗时：**200ms - 1500ms**

### 3. **缺少缓存机制** ⚠️

**问题分析**：
- 每次请求都直接查询数据库
- 相同参数的请求无法复用结果
- 没有利用Redis缓存

**性能影响**：
- 相同查询重复执行
- 无法利用缓存加速
- 增加数据库压力

### 4. **复杂的搜索查询** ⚠️

**问题位置**：`primary_views.py` 第117-176行

**问题分析**：
- 使用多个 `icontains` 查询（无法使用索引）
- 使用 `Case/When` 注解进行排序权重计算
- 对多个字段进行模糊匹配

**性能影响**：
- 模糊查询无法使用索引
- 需要扫描大量数据
- 耗时：**300ms - 2000ms**

### 5. **序列化开销**

**问题位置**：`primary_views.py` 第190行

```python
schools_data = [serialize_primary_school(school) for school in schools_page]
```

**问题分析**：
- 每次序列化都要调用 `get_total_classes()` 方法
- 需要解析JSON字段
- 虽然开销相对较小，但累积起来也有影响

## 性能测试数据（预估）

| 场景 | 当前耗时 | 主要瓶颈 |
|------|---------|---------|
| 无过滤，第一页 | 800-2000ms | JSON_EXTRACT排序 + COUNT |
| 有过滤，第一页 | 500-1500ms | JSON_EXTRACT排序 + COUNT |
| 有搜索关键词 | 1000-3000ms | 模糊查询 + JSON_EXTRACT |
| 缓存命中 | N/A | 未实现缓存 |

## 优化方案

### 方案1：启用优化版本（推荐）✅

**操作**：切换到已存在的优化版本

**文件**：`backend/backend/api/schools/urls.py`

```python
# 当前（未优化）
re_path(r'^primary/$', primary_views.primary_schools_list, ...)

# 改为（优化版本）
re_path(r'^primary/$', primary_schools_list_optimized, ...)
```

**优化内容**：
- ✅ 添加了Redis缓存（5分钟）
- ✅ 优化了COUNT查询（缓存总数）
- ✅ 使用切片分页替代Paginator
- ✅ 优化了JSON字段处理

**预期效果**：
- 首次请求：200-500ms
- 缓存命中：10-50ms
- 性能提升：**70-90%**

### 方案2：优化JSON排序（如果必须使用当前版本）

**问题**：JSON_EXTRACT无法使用索引

**解决方案**：
1. **添加计算字段**（推荐）
   - 在模型中添加 `band1_rate` 字段
   - 在保存时从JSON中提取并存储
   - 建立索引

2. **使用生成列**（MySQL 5.7+）
   ```sql
   ALTER TABLE tb_primary_schools 
   ADD COLUMN band1_rate DECIMAL(5,2) 
   GENERATED ALWAYS AS (CAST(JSON_EXTRACT(promotion_info, '$.band1_rate') AS DECIMAL(5,2))) 
   STORED;
   
   CREATE INDEX idx_band1_rate ON tb_primary_schools(band1_rate);
   ```

3. **延迟排序**
   - 先获取数据，在Python中排序
   - 只对当前页数据排序

### 方案3：优化COUNT查询

**当前问题**：
```python
paginator = Paginator(queryset, page_size)
total = paginator.count  # 执行 COUNT(*)
```

**优化方案**：
```python
# 缓存总数
count_cache_key = f"primary:count:{hash_key}"
total = cache.get(count_cache_key)
if total is None:
    total = queryset.count()
    cache.set(count_cache_key, total, 300)  # 缓存5分钟
```

### 方案4：添加数据库索引

**已存在的索引**：
- ✅ district, school_net, school_category 等单字段索引

**建议添加**：
```sql
-- 复合索引（针对常见查询组合）
CREATE INDEX idx_primary_district_category 
ON tb_primary_schools(district, school_category);

CREATE INDEX idx_primary_district_net 
ON tb_primary_schools(district, school_net);

-- 如果添加了band1_rate字段
CREATE INDEX idx_primary_band1_rate 
ON tb_primary_schools(band1_rate DESC);
```

### 方案5：优化搜索查询

**当前问题**：多个 `icontains` 查询无法使用索引

**优化方案**：
1. **使用全文索引**（MySQL 5.6+）
   ```sql
   ALTER TABLE tb_primary_schools 
   ADD FULLTEXT INDEX idx_fulltext_name (school_name, school_name_traditional);
   ```

2. **限制搜索范围**
   - 只搜索学校名称（使用索引）
   - 其他字段使用精确匹配

3. **使用Elasticsearch**（长期方案）
   - 专门用于全文搜索
   - 性能更好，但需要额外基础设施

## 立即行动方案

### 步骤1：启用优化版本（5分钟）

修改 `backend/backend/api/schools/urls.py`：

```python
# 注释掉未优化版本
# re_path(r'^primary/$', primary_views.primary_schools_list, name='primary_schools_list'),

# 启用优化版本
re_path(r'^primary/$', primary_schools_list_optimized, name='primary_schools_list'),
```

**预期效果**：性能提升 70-90%

### 步骤2：检查Redis配置（10分钟）

确保Redis已正确配置并运行：

```bash
# 检查Redis连接
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'
```

### 步骤3：添加生成列（可选，30分钟）

如果MySQL版本支持（5.7+），添加生成列：

```sql
-- 添加band1_rate生成列
ALTER TABLE tb_primary_schools 
ADD COLUMN band1_rate DECIMAL(5,2) 
GENERATED ALWAYS AS (
    CAST(JSON_EXTRACT(promotion_info, '$.band1_rate') AS DECIMAL(5,2))
) STORED;

-- 添加索引
CREATE INDEX idx_primary_band1_rate ON tb_primary_schools(band1_rate DESC);
```

然后修改查询：
```python
# 不再使用JSON_EXTRACT，直接使用字段
queryset = queryset.order_by('-band1_rate', 'school_name')
```

## 性能监控

### 添加性能日志

在视图中添加时间记录：

```python
import time
from django.utils.log import logger

def primary_schools_list(request):
    start_time = time.time()
    try:
        # ... 现有代码 ...
        response = JsonResponse({...})
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Primary schools list API: {elapsed:.2f}ms")
        
        return response
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(f"Primary schools list API error ({elapsed:.2f}ms): {str(e)}")
        raise
```

### 使用Django Debug Toolbar

在开发环境中使用Django Debug Toolbar查看SQL查询：
- 查询数量
- 查询耗时
- 是否有N+1问题

## 总结

**主要问题**：
1. JSON_EXTRACT在排序中（最严重）
2. COUNT查询开销大
3. 缺少缓存机制
4. 复杂搜索查询

**推荐方案**：
1. ✅ 立即启用优化版本（最大收益）
2. ✅ 确保Redis配置正确
3. ⚠️ 考虑添加生成列（长期优化）

**预期效果**：
- 首次请求：200-500ms（当前：800-3000ms）
- 缓存命中：10-50ms
- 性能提升：**70-90%**

