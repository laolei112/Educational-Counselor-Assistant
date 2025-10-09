# 香港中学数据导入工具使用说明

## 概述

本脚本用于从 Excel 文件（`香港各中学信息.xlsx`）导入中学数据到 `tb_secondary_schools` 表。
使用 Django ORM 进行数据操作，遵循项目的标准开发模式。

## 文件说明

- **import_secondary_schools.py**: 主导入脚本
- **tb_secondary_schools.py**: ORM 模型文件（位于 `backend/backend/models/`）
- **香港各中学信息.xlsx**: 源数据文件

## 前提条件

1. Python 3.x 环境
2. 已安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 数据库已创建 `tb_secondary_schools` 表：
   ```bash
   # 在 backend 目录下运行
   python manage.py makemigrations
   python manage.py migrate
   ```

## 使用方法

### 1. 进入项目目录

```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend/common/data
```

### 2. 确认 Excel 文件存在

确保 `香港各中学信息.xlsx` 文件在当前目录下。

### 3. 运行导入脚本

```bash
python3 import_secondary_schools.py
```

## 导入字段说明

| Excel 列名 | 数据库字段 | 说明 |
|-----------|-----------|------|
| 学校名称 | school_name | 学校名称（必填） |
| 区域 | district | 所在区域 |
| 对应校网 | school_net | 对应校网 |
| 宗教 | religion | 宗教背景 |
| 学生性别 | student_gender | 学生性别 |
| 学费（相同的概括，不同的独立罗列） | tuition | 学费信息 |
| 学校类别 | school_category | 学校类别 |
| 学校组别 | school_group | 学校组别 |
| 插班开放时间 | transfer_open_time | 插班开放时间 |
| 全校总班数 | total_classes | 全校总班数 |
| 中一入学 | admission_info | 入学信息 |
| 学校地址 | address | 学校地址 |
| 电话 | phone | 联系电话 |
| 电邮 | email | 电子邮箱 |
| 网站 | website | 官方网站 |

**注意**: `school_curriculum`（课程设置）字段暂时不导入。

## 数据处理逻辑

1. **去重逻辑**: 根据 `school_name` 判断学校是否已存在
   - 如果存在，更新现有记录
   - 如果不存在，创建新记录

2. **数据清理**:
   - 空值（NaN、'-'、空字符串）转换为 `None`
   - 电话号码自动格式化
   - 字符串去除首尾空格

3. **错误处理**:
   - 单条记录错误不影响其他记录
   - 所有错误会输出到控制台

## 输出示例

```
============================================================
香港中学数据导入工具
============================================================
开始时间: 2025-10-09 15:30:00

正在读取 Excel 文件: /path/to/香港各中学信息.xlsx
成功读取 500 条记录

开始导入数据...
创建中学: 拔萃男书院
创建中学: 拔萃女书院
创建中学: 保良局罗杰承（一九八三）中学
...
已处理 10 条记录...
已处理 20 条记录...
...

============================================================
导入完成
============================================================
成功创建: 450 条记录
成功更新: 50 条记录
失败记录: 0 条
结束时间: 2025-10-09 15:31:00

数据库中共有 500 条中学记录

区域分布:
  黄大仙区: 35 所
  九龙城区: 32 所
  油尖旺区: 28 所
  ...

学校类别分布:
  资助: 300 所
  直资: 120 所
  官立: 50 所
  私立: 30 所
```

## ORM 模型使用示例

### 查询示例

```python
from backend.models.tb_secondary_schools import TbSecondarySchools

# 获取所有中学
schools = TbSecondarySchools.objects.all()

# 按区域查询
schools_in_district = TbSecondarySchools.objects.filter(district='黄大仙区')

# 查询 Band 1 学校
band1_schools = TbSecondarySchools.objects.filter(school_group__startswith='1')

# 查询男女校
coed_schools = TbSecondarySchools.objects.filter(student_gender='男女')

# 获取学校详细信息
school = TbSecondarySchools.objects.get(school_name='拔萃男书院')
info = school.get_full_info()
```

### 创建/更新示例

```python
# 创建新记录
school = TbSecondarySchools.objects.create(
    school_name='测试中学',
    district='九龙城区',
    school_category='资助',
    school_group='1A',
    student_gender='男女',
    total_classes=24
)

# 更新记录
school = TbSecondarySchools.objects.get(school_name='测试中学')
school.phone = '12345678'
school.email = 'test@school.edu.hk'
school.save()
```

## 故障排除

### 问题 1: Django 环境初始化失败

**错误信息**: `ModuleNotFoundError: No module named 'django'`

**解决方法**:
```bash
pip install django
```

### 问题 2: 数据库表不存在

**错误信息**: `Table 'dev_yundisoft.tb_secondary_schools' doesn't exist`

**解决方法**:
```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend
python manage.py makemigrations
python manage.py migrate
```

### 问题 3: Excel 文件读取失败

**错误信息**: `读取 Excel 文件失败: No such file or directory`

**解决方法**:
- 确认 Excel 文件在正确的目录下
- 检查文件名是否为 `香港各中学信息.xlsx`

### 问题 4: 部分数据导入失败

**解决方法**:
- 查看控制台输出的错误信息
- 检查 Excel 文件中对应行的数据格式
- 确认必填字段（学校名称）是否为空

## 注意事项

1. **数据备份**: 导入前建议备份数据库
2. **重复运行**: 脚本可以重复运行，会自动更新已存在的记录
3. **课程设置**: 暂不导入课程相关字段，后续可单独处理
4. **性能**: 大批量数据导入时可能需要几分钟时间

## 数据库迁移

如果修改了 ORM 模型，需要执行迁移：

```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend
python manage.py makemigrations
python manage.py migrate
```

## 相关文件

- ORM 模型: `backend/backend/models/tb_secondary_schools.py`
- SQL 创建脚本: `backend/common/db/tb_secondary_schools.sql`
- 导入脚本: `backend/common/data/import_secondary_schools.py`

