# 数据库迁移说明

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

