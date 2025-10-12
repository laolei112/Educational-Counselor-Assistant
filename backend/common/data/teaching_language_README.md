# 授课语言数据分析和更新说明

## 概述

根据"香港各中学信息.xlsx"文件中的两列数据统计英文授课占比：
- **以中文为教学语言_中四至中六**
- **以英文为教学语言_中四至中六**

## 数据处理规则

### 1. 科目解析
- 使用 `、` (顿号) 分隔科目
- 忽略 `<br>` 及其后的内容（非DSE课程）
- 去除空白字符

### 2. 英文占比计算
```
英文占比 = (英文科目数 / 总科目数) × 100%
总科目数 = 中文科目数 + 英文科目数
```

### 3. 分类标准

| 英文占比范围 | 教学语言分类 |
|------------|-----------|
| >= 80%     | 英文       |
| 60% - 79%  | 主要英文    |
| 40% - 59%  | 中英文并重  |
| 20% - 39%  | 主要中文    |
| < 20%      | 中文       |
| 无数据      | NULL      |

## 使用方法

### 方法1: 仅分析数据（推荐先运行）

运行分析脚本查看统计结果，不修改数据库：

```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend/common/data
python3 analyze_teaching_language.py
```

**输出内容：**
- 前20所学校的详细分析
- 各分类的统计汇总
- 生成 `update_teaching_language.sql` 文件

### 方法2: 执行 SQL 更新数据库

1. 先运行分析脚本生成 SQL 文件
2. 执行 SQL 更新数据库：

```bash
# 使用 Docker 容器
docker exec -i <mysql-container-name> mysql -u root -p<password> educational_counselor < update_teaching_language.sql

# 或直接使用 MySQL
mysql -h localhost -u root -p educational_counselor < update_teaching_language.sql
```

### 方法3: 使用 Python 脚本直接更新

在 Docker 容器内运行：

```bash
# 进入后端容器
docker exec -it <backend-container-name> bash

# 运行更新脚本
cd /data/home/roylei/Educational-Counselor-Assistant/backend
python common/data/update_teaching_language.py
```

## 示例分析结果

```
1. 拔萃男书院
   中文科目数: 4, 英文科目数: 10
   总科目数: 14, 英文占比: 71.4%
   教学语言: 主要英文

2. 拔萃女书院
   中文科目数: 3, 英文科目数: 8
   总科目数: 11, 英文占比: 72.7%
   教学语言: 主要英文

3. 保良局罗杰承（一九八三）中学
   中文科目数: 4, 英文科目数: 8
   总科目数: 12, 英文占比: 66.7%
   教学语言: 主要英文
```

## 预期统计分布

根据香港中学的实际情况，预期分布大致为：

- **英文** (>=80%): 约5-10%的学校（顶尖国际学校、名校）
- **主要英文** (60-79%): 约15-25%的学校（Band 1学校）
- **中英文并重** (40-59%): 约30-40%的学校（Band 1-2学校）
- **主要中文** (20-39%): 约20-30%的学校（Band 2-3学校）
- **中文** (<20%): 约10-20%的学校（Band 3学校）

## 注意事项

1. **数据准确性**: Excel 中的数据格式可能有变化，运行前请检查列名是否匹配
2. **学校名称匹配**: 更新脚本通过学校名称匹配，确保 Excel 和数据库中的学校名称一致
3. **备份数据**: 执行更新前建议备份数据库
4. **验证结果**: 更新后可以查询几所典型学校验证结果是否合理

## 验证查询

更新后可以执行以下 SQL 验证：

```sql
-- 查看各分类的学校数量
SELECT teaching_language, COUNT(*) as count
FROM tb_secondary_schools
GROUP BY teaching_language
ORDER BY 
  CASE teaching_language
    WHEN '英文' THEN 1
    WHEN '主要英文' THEN 2
    WHEN '中英文并重' THEN 3
    WHEN '主要中文' THEN 4
    WHEN '中文' THEN 5
    ELSE 6
  END;

-- 查看具体学校
SELECT school_name, teaching_language, school_group
FROM tb_secondary_schools
WHERE teaching_language = '英文'
ORDER BY school_name;
```

## 前端显示

更新完成后，授课语言会在以下位置显示：

1. **学校详情页** (`SchoolDetailModal.vue`): 基本信息 → 教学语言
2. **API 响应**: `teachingLanguage` 字段

如果数据库中没有授课语言数据，前端会显示"中英文并重"作为默认值。

