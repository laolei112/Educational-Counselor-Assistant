# 小学升学数据统计工具

## 📋 概述

本工具用于统计每个小学的升中 Band 1 比例。基于各区的升学数据 Excel 文件和中学 banding 信息，自动计算每所小学的升 Band 1 比例。

## 📁 数据文件

### 输入文件

#### 1. 中学 Banding 信息
- **文件**: `中学banding信息.xlsx`
- **列名**: `school_name`, `school_group`
- **示例**:
  ```
  school_name         | school_group
  拔萃男书院          | Band 1B
  拔萃女书院          | Band 1A
  ```
- **总计**: 368 所中学（Band 1: 123所, Band 2: 123所, Band 3: 122所）

#### 2. 小学升学数据
- **文件**: 11 个区域的升学数据 Excel 文件
  - 中西區小学升学数据.xlsx
  - 九龙城区升学数据.xlsx
  - 元朗區升学数据.xlsx
  - 北区升学数据.xlsx
  - 南区升学数据.xlsx
  - 大埔区升学数据.xlsx
  - 屯門升学数据.xlsx
  - 东区小学升学数据.xlsx
  - 灣仔區升学数据.xlsx
  - 离岛区升学数据.xlsx
  - 西贡区升学数据.xlsx

- **结构**: 每个文件包含多个工作表，每个工作表代表一所小学
- **列名**: `是否可统计升中数据`, `年份`, `升入学校`, `人数`, `参考资料`

### 输出文件

#### 1. primary_schools_band1_stats.json
完整的 JSON 格式统计数据：
```json
{
  "summary": {
    "total_schools": 76,
    "total_students": 8144,
    "band1_students": 1684,
    "band1_rate": 20.68
  },
  "schools": [
    {
      "primary_school": "圓玄小學",
      "total_students": 94,
      "band1_students": 61,
      "band1_rate": 64.89,
      "band_distribution": {...},
      "secondary_schools": {...}
    }
  ]
}
```

#### 2. primary_schools_band1_rate.csv
CSV 格式汇总表：
```csv
小学名称,区域,总人数,Band 1人数,Band 1比例
圓玄小學,屯門,94,61,64.89%
聖公會聖彼得小學,中西区,106,67,63.21%
...
```

#### 3. primary_schools_detailed_report.txt
详细文本报告，包含每所小学的：
- Band 1 比例
- Band 分布详情
- 主要升学中学列表
- 未匹配学校列表

## 🚀 使用方法

### 运行统计脚本

```bash
cd /Users/roylei/projects/Educational-Counselor-Assistant/backend/common/primary_data
python3 calculate_primary_band1_rate.py
```

### 查看统计结果

```bash
# 查看 CSV 报告
cat primary_schools_band1_rate.csv

# 查看详细报告
less primary_schools_detailed_report.txt

# 查看 JSON（格式化）
cat primary_schools_band1_stats.json | python3 -m json.tool | head -50
```

## 📊 统计结果

### 整体数据
- **统计小学数**: 76 所
- **升学总人数**: 8,144 人
- **升入 Band 1**: 1,684 人
- **Band 1 比例**: 20.68%

### Top 10 小学（Band 1 比例）

| 排名 | 小学名称 | Band 1 比例 | 人数 |
|------|---------|------------|------|
| 1 | 圓玄小學 | 64.89% | 61/94 |
| 2 | 聖公會聖彼得小學 | 63.21% | 67/106 |
| 3 | 保良局田家炳小學 | 57.89% | 33/57 |
| 4 | 九龍塘學校(小學部) | 54.08% | 53/98 |
| 5 | 九龍塘宣道小學 | 53.85% | 119/221 |
| 6 | 英皇書院同學會小學第二校 | 45.45% | 70/154 |
| 7 | 聖安多尼學校 | 41.38% | 36/87 |
| 8 | 大埔舊墟公立學校 | 40.91% | 45/110 |
| 9 | 中西區聖安多尼學校 | 37.58% | 62/165 |
| 10 | 樂善堂梁銶琚學校 | 35.71% | 15/42 |

### 各区域 Band 1 比例

| 区域 | Band 1 比例 | 人数 | 小学数 |
|------|------------|------|--------|
| 中西区 | 34.53% | 453/1312 | 11所 |
| 大埔区 | 25.76% | 272/1056 | 11所 |
| 九龙城区 | 24.53% | 431/1757 | 10所 |
| 南区 | 20.21% | 39/193 | 2所 |
| 屯門 | 17.73% | 114/643 | 8所 |
| 元朗区 | 14.16% | 211/1490 | 18所 |
| 北区 | 9.69% | 164/1693 | 16所 |

## 🔧 技术细节

### 数据结构

#### Excel 文件结构
```
区域升学数据.xlsx
├── 小学A（工作表）
│   ├── 是否可统计升中数据
│   ├── 年份
│   ├── 升入学校
│   └── 人数
├── 小学B（工作表）
└── 小学C（工作表）
```

### 统计逻辑

1. **加载中学 Band 映射**
   - 从 `中学banding信息.xlsx` 读取
   - 建立学校名称到 Band 的映射

2. **遍历升学数据文件**
   - 每个文件代表一个区域
   - 每个工作表代表一所小学

3. **计算每所小学的 Band 1 比例**
   ```python
   Band 1 比例 = (升入 Band 1 中学的学生数 / 总升学人数) × 100%
   ```

4. **学校名称匹配**
   - 完全匹配
   - 繁简转换匹配
   - 部分匹配（去除"中學"后缀）

### Band 判断规则

```python
def is_band_1(band_str):
    return 'Band 1' in band_str or band_str.startswith('1')
```

Band 1 包括：
- Band 1A
- Band 1B
- Band 1C

## 📝 应用到数据库

### 更新小学数据库的 promotion_info 字段

使用生成的统计结果更新数据库：

```python
from backend.models.tb_primary_schools import TbPrimarySchools
import json

# 读取统计结果
with open('primary_schools_band1_stats.json', 'r') as f:
    stats = json.load(f)

# 更新每所小学的升学信息
for school_stat in stats['schools']:
    school_name = school_stat['primary_school']
    
    # 查找对应的数据库记录
    schools = TbPrimarySchools.objects.filter(school_name__icontains=school_name)
    
    for school in schools:
        school.promotion_info = {
            'band1_rate': school_stat['band1_rate'],
            'total_graduates': school_stat['total_students'],
            'band1_graduates': school_stat['band1_students'],
            'band_distribution': school_stat['band_distribution'],
            'top_secondary_schools': list(school_stat['secondary_schools'].items())[:10]
        }
        school.save()
        print(f"更新: {school.school_name}")
```

## ⚠️ 注意事项

### 1. Excel 文件格式问题
部分 Excel 文件可能因为格式问题无法读取（如东区、灣仔區）：
```
TypeError: expected <class 'openpyxl.styles.fills.Fill'>
```

**解决方案**：
- 在 Excel 中重新打开并另存为新文件
- 或手动提取数据

### 2. 学校名称匹配
脚本会尝试多种方式匹配学校名称：
- 完全匹配
- 繁简转换
- 部分匹配

如果仍有未匹配的学校，会在报告中标注。

### 3. 数据质量
- 部分小学可能没有升学数据（工作表为空）
- 部分中学名称可能在 Band 映射中不存在
- 需要人工审核未匹配的学校

## 🔍 数据验证

### 查看未匹配的学校

```bash
# 在详细报告中查找未匹配的学校
grep "未匹配到 Band 的学校" primary_schools_detailed_report.txt -A 5
```

### 手动添加缺失的中学 Band 信息

如果发现重要的中学未包含在 banding 信息中：
1. 在 `中学banding信息.xlsx` 中添加
2. 重新运行统计脚本

## 📈 数据应用

### 1. 更新小学数据库

创建脚本将统计结果应用到数据库的 `promotion_info` 字段

### 2. 前端展示

在前端小学卡片上显示：
```vue
<template v-if="school.promotionInfo?.band1_rate">
  <span>升Band 1: {{ school.promotionInfo.band1_rate }}%</span>
</template>
```

### 3. 筛选功能

支持按 Band 1 比例筛选小学：
- Band 1 比例 > 50%
- Band 1 比例 30-50%
- Band 1 比例 < 30%

## 🎯 后续优化

### 1. 改进匹配算法
- 使用更智能的字符串相似度算法（如编辑距离）
- 建立学校别名映射表

### 2. 多年数据分析
- 分析升学趋势（2023-2025）
- 计算平均 Band 1 比例

### 3. 数据可视化
- 生成图表展示各区 Band 1 比例
- 小学排名可视化

### 4. 自动化更新
- 定期从最新 Excel 文件更新统计
- 自动同步到数据库

## 📞 文件清单

### 脚本文件
- `calculate_primary_band1_rate.py` - 主统计脚本

### 输入文件
- `中学banding信息.xlsx` - 中学 Band 映射
- `*升学数据.xlsx` - 各区升学数据（11个文件）

### 输出文件
- `primary_schools_band1_stats.json` - JSON 格式统计结果
- `primary_schools_band1_rate.csv` - CSV 汇总表
- `primary_schools_detailed_report.txt` - 详细文本报告

---

**创建时间**: 2025-10-19  
**统计小学数**: 76 所  
**覆盖区域**: 7 个区（中西区、九龙城区、元朗区、北区、南区、大埔区、屯門）  
**Band 1 总体比例**: 20.68%
