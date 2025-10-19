# 数据库迁移说明

## 目录

1. [添加 teaching_language 字段](#添加-teaching_language-字段)
2. [添加 transfer_info 和 promotion_info 字段](#添加-transfer_info-和-promotion_info-字段)

---

## 添加 teaching_language 字段

### 迁移脚本
`add_teaching_language.sql` - 为 tb_schools 和 tb_secondary_schools 添加授课语言字段

### 执行方法

#### 方法1：使用 MySQL 命令行

```bash
# 进入 MySQL 容器（如果使用 Docker）
docker exec -it <mysql-container-name> mysql -u root -p

# 或者直接使用 MySQL 客户端
mysql -h localhost -u root -p educational_counselor

# 执行迁移脚本
source /path/to/add_teaching_language.sql;
```

#### 方法2：使用 Docker 执行

```bash
# 假设您的 MySQL 容器名称为 mysql-container
docker exec -i <mysql-container-name> mysql -u root -p<password> educational_counselor < backend/common/db/alter/add_teaching_language.sql
```

#### 方法3：直接通过文件执行

```bash
mysql -h localhost -u root -p educational_counselor < backend/common/db/alter/add_teaching_language.sql
```

### 迁移内容

1. 在 `tb_schools` 表中添加 `teaching_language` 列（VARCHAR(100)）
2. 在 `tb_secondary_schools` 表中添加 `teaching_language` 列（VARCHAR(100)）
3. 为两个表的 `teaching_language` 字段创建索引

### 验证迁移

执行以下 SQL 语句验证字段已成功添加：

```sql
-- 检查 tb_schools 表
DESCRIBE tb_schools;

-- 检查 tb_secondary_schools 表
DESCRIBE tb_secondary_schools;

-- 检查索引
SHOW INDEX FROM tb_schools;
SHOW INDEX FROM tb_secondary_schools;
```

### 代码更改

以下文件已经更新以支持 teaching_language 字段：

#### 后端
- `backend/backend/models/tb_schools.py` - 添加了 teaching_language 字段
- `backend/backend/models/tb_secondary_schools.py` - 添加了 teaching_language 字段
- `backend/backend/api/schools/views.py` - 更新了序列化函数
- `backend/backend/api/schools/secondary_views.py` - 更新了序列化函数

#### 前端
- `frontend/src/components/SchoolDetailModal.vue` - 在详情页显示授课语言

### 注意事项

1. 执行迁移前请先备份数据库
2. 新字段允许为 NULL，因此不会影响现有数据
3. 执行迁移后无需重启应用，Django ORM 会自动识别新字段

---

## 添加 transfer_info 和 promotion_info 字段

### 迁移脚本

- `add_transfer_promotion_info.sql` - 带检查的完整版本（推荐）
- `add_transfer_promotion_info_simple.sql` - 简化版本（字段已存在会报错）

### 执行方法

#### 方法1：使用带检查的版本（推荐）

```bash
# 使用 MySQL 客户端
mysql -h localhost -u root -p dev_yundisoft < backend/common/db/alter/add_transfer_promotion_info.sql

# 或使用 Docker
docker exec -i edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft < backend/common/db/alter/add_transfer_promotion_info.sql
```

这个版本会先检查字段是否存在，如果已存在则跳过，不会报错。

#### 方法2：使用简化版本

```bash
# 使用 MySQL 客户端
mysql -h localhost -u root -p dev_yundisoft < backend/common/db/alter/add_transfer_promotion_info_simple.sql

# 或使用 Docker
docker exec -i edu_mysql mysql -u root -pfgdTv@4629uGdY dev_yundisoft < backend/common/db/alter/add_transfer_promotion_info_simple.sql
```

⚠️ **注意**: 如果字段已存在，这个版本会报错。

### 迁移内容

#### 为 tb_primary_schools 表添加：
1. `transfer_info` - JSON 类型，存储插班申请信息
2. `promotion_info` - JSON 类型，存储升学信息

#### 为 tb_secondary_schools 表添加：
1. `transfer_info` - JSON 类型，存储插班申请信息
2. `promotion_info` - JSON 类型，存储升学信息

### JSON 字段结构示例

#### transfer_info（插班信息）
```json
{
  "open_time": "9月至次年6月",
  "requirements": "需提供成绩单、推荐信",
  "contact": "请致电学校查询",
  "remarks": "视学位情况而定"
}
```

#### promotion_info（升学信息）
```json
{
  "secondary_schools": ["学校A", "学校B"],
  "promotion_rate": 95,
  "band1_rate": 60,
  "remarks": "大部分学生升读Band 1中学"
}
```

### 验证迁移

执行以下 SQL 语句验证字段已成功添加：

```sql
-- 检查 tb_primary_schools 表
DESCRIBE tb_primary_schools;

-- 检查 tb_secondary_schools 表
DESCRIBE tb_secondary_schools;

-- 查看具体字段信息
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    COLUMN_TYPE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'dev_yundisoft'
AND TABLE_NAME IN ('tb_primary_schools', 'tb_secondary_schools')
AND COLUMN_NAME IN ('transfer_info', 'promotion_info')
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

### 代码更改

以下文件已经更新以支持新字段：

#### 后端模型
- `backend/backend/models/tb_primary_schools.py` - 添加了 transfer_info 和 promotion_info 字段
- `backend/backend/models/tb_secondary_schools.py` - 添加了 transfer_info 和 promotion_info 字段

#### 后端视图
- `backend/backend/api/schools/primary_views.py` - 更新了序列化函数，返回插班和升学信息
- `backend/backend/api/schools/secondary_views.py` - 更新了序列化函数，返回插班和升学信息

#### 数据导入脚本
- `backend/common/data/import_primary_schools.py` - 支持导入插班和升学信息

### 使用示例

#### Python 查询示例
```python
from backend.models.tb_primary_schools import TbPrimarySchools

# 查询有插班信息的学校
schools_with_transfer = TbPrimarySchools.objects.exclude(transfer_info__isnull=True)

# 查询有升学信息的学校
schools_with_promotion = TbPrimarySchools.objects.exclude(promotion_info__isnull=True)

# 获取学校的插班信息
school = TbPrimarySchools.objects.first()
if school.transfer_info:
    print(f"插班开放时间: {school.transfer_info.get('open_time')}")

# 获取学校的升学信息
if school.promotion_info:
    print(f"升学率: {school.promotion_info.get('promotion_rate')}%")
```

#### API 调用示例
```bash
# 获取小学详情（包含插班和升学信息）
curl http://localhost:8080/api/schools/primary/1/

# 返回示例
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "圣公会圣马太小学",
    "transferInfo": {
      "open_time": "视学位情况而定",
      "contact": "请致电学校查询"
    },
    "promotionInfo": {
      "secondary_schools": ["圣公会某某中学"],
      "remarks": "大部分学生升读Band 1中学"
    }
  }
}
```

### 注意事项

1. **执行前备份** - 执行迁移前请务必备份数据库
2. **字段类型** - JSON 类型需要 MySQL 5.7.8+ 版本
3. **NULL 值** - 新字段允许为 NULL，不影响现有数据
4. **无需重启** - 执行迁移后无需重启应用，Django ORM 会自动识别新字段
5. **数据导入** - 使用 `import_primary_schools.py` 导入数据时会自动填充这些字段

### 回滚方法

如果需要回滚迁移，可以执行以下 SQL：

```sql
-- 删除 tb_primary_schools 的字段
ALTER TABLE tb_primary_schools DROP COLUMN transfer_info;
ALTER TABLE tb_primary_schools DROP COLUMN promotion_info;

-- 删除 tb_secondary_schools 的字段
ALTER TABLE tb_secondary_schools DROP COLUMN transfer_info;
ALTER TABLE tb_secondary_schools DROP COLUMN promotion_info;
```

