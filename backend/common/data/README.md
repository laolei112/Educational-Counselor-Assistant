# 学校数据导入工具

本目录包含用于将学校数据从 JSON 文件导入到数据库的工具。

## 文件说明

- `all_primary_schools.json` - 小学数据文件
- `all_secondary_schools.json` - 中学数据文件
- `import_schools_to_db.py` - 直接导入数据库的 Python 脚本
- `generate_insert_sql.py` - 生成 INSERT SQL 语句的 Python 脚本

## 使用方法

### 方法一：直接导入数据库

```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend
python common/data/import_schools_to_db.py
```

这个脚本会：
- 读取两个 JSON 文件
- 将数据直接写入数据库
- 显示导入统计信息
- 处理重复数据（更新现有记录）

### 方法二：生成 SQL 语句

```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend
python common/data/generate_insert_sql.py
```

这个脚本会：
- 读取两个 JSON 文件
- 生成 `insert_schools_data.sql` 文件
- 包含所有学校的 INSERT 语句

然后可以手动执行 SQL 文件：
```bash
mysql -u username -p database_name < common/data/insert_schools_data.sql
```

## 字段映射

### 小学数据字段映射

| JSON 字段 | 数据库字段 | 说明 |
|-----------|------------|------|
| name | name | 学校名称 |
| url | url | 学校信息页面URL |
| type | category | 学校类型（官立→government, 資助→traditional, 直資→direct, 私立→private） |
| network | net_name | 校网 |
| religion | religion | 宗教背景 |
| gender | gender | 性别（男女→coed, 男校→boys, 女校→girls） |
| address | address | 学校地址 |
| district | district | 所属地区 |
| school_level | level | 学校级别（固定为 primary） |
| official_website | official_website | 官方网站 |
| secondary_note | remarks | 备注 |

### 中学数据字段映射

| JSON 字段 | 数据库字段 | 说明 |
|-----------|------------|------|
| name | name | 学校名称 |
| url | url | 学校信息页面URL |
| type | category | 学校类型 |
| religion | religion | 宗教背景 |
| gender | gender | 性别 |
| address | address | 学校地址 |
| district | district | 所属地区 |
| school_level | level | 学校级别（固定为 secondary） |
| official_website | official_website | 官方网站 |
| language + banding | remarks | 语言和等级信息作为备注 |

## 特殊处理

1. **promotion_rate 字段**：根据学校类型和 banding 信息自动生成 JSON 数据
2. **重复数据处理**：如果学校名称已存在，会更新现有记录
3. **空值处理**：空字符串和特殊值（如 "-", "無"）会被转换为 NULL
4. **字符编码**：支持 UTF-8 编码的中文字符

## 注意事项

1. 确保数据库连接配置正确
2. 建议在导入前备份数据库
3. 大量数据导入可能需要较长时间
4. 如果出现错误，脚本会继续处理其他记录并显示错误信息

## 数据统计

- 小学数据：约 7000+ 条记录
- 中学数据：约 6000+ 条记录
- 总计：约 13000+ 条学校记录
