#!/usr/bin/env python3
"""
导入描述性升学数据到数据库

使用方法：
1. 准备数据文件（CSV或JSON格式）
2. 运行此脚本导入数据

数据格式示例（CSV）：
学校名称,升学描述
圣保罗小学,"约85%学生可升入直属中学圣保罗书院（Band 1A）"
嘉诺撒圣心学校,"约85%学生升入直属中学嘉诺撒圣心书院（Band 1B）"

或JSON格式：
{
  "学校名称": [
    "约85%学生可升入直属中学圣保罗书院（Band 1A）",
    "约85%学生升入直属中学嘉诺撒圣心书院（Band 1B）"
  ]
}
"""

import os
import sys
import django
import json
import csv
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools
from .parse_promotion_descriptions import parse_promotion_descriptions


def import_from_csv(csv_file):
    """
    从CSV文件导入数据
    
    CSV格式：
    学校名称,升学描述
    圣保罗小学,"约85%学生可升入直属中学圣保罗书院（Band 1A）"
    """
    schools_data = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            school_name = row.get('学校名称', '').strip()
            description = row.get('升学描述', '').strip()
            
            if school_name and description:
                if school_name not in schools_data:
                    schools_data[school_name] = []
                schools_data[school_name].append(description)
    
    return schools_data


def import_from_json(json_file):
    """
    从JSON文件导入数据
    
    JSON格式：
    {
      "学校名称": [
        "描述1",
        "描述2"
      ]
    }
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_school_promotion_descriptions(school, descriptions):
    """
    更新学校的描述性升学数据
    """
    if not descriptions:
        return
    
    # 获取现有的promotion_info
    promotion_info = school.promotion_info or {}
    
    # 解析描述文本
    parsed_descriptions = parse_promotion_descriptions(descriptions)
    
    # 更新promotion_descriptions字段
    promotion_info['promotion_descriptions'] = parsed_descriptions
    
    # 保存
    school.promotion_info = promotion_info
    school.save(update_fields=['promotion_info', 'updated_at'])


def match_school_in_db(school_name):
    """
    在数据库中匹配学校
    """
    # 尝试精确匹配
    school = TbPrimarySchools.objects.filter(school_name=school_name).first()
    if school:
        return school
    
    # 尝试包含匹配
    school = TbPrimarySchools.objects.filter(school_name__icontains=school_name).first()
    if school:
        return school
    
    return None


def import_descriptions(data_source, source_type='csv'):
    """
    导入描述性升学数据
    
    Args:
        data_source: 数据文件路径或字典数据
        source_type: 'csv' 或 'json' 或 'dict'
    """
    if source_type == 'csv':
        schools_data = import_from_csv(data_source)
    elif source_type == 'json':
        schools_data = import_from_json(data_source)
    elif source_type == 'dict':
        schools_data = data_source
    else:
        raise ValueError(f"不支持的源类型: {source_type}")
    
    updated_count = 0
    not_found_count = 0
    
    for school_name, descriptions in schools_data.items():
        school = match_school_in_db(school_name)
        
        if school:
            update_school_promotion_descriptions(school, descriptions)
            updated_count += 1
            print(f"✅ 更新: {school.school_name} - {len(descriptions)} 条描述")
        else:
            not_found_count += 1
            print(f"⚠️  未找到: {school_name}")
    
    print(f"\n完成: 更新 {updated_count} 所，未找到 {not_found_count} 所")


def main():
    """
    主函数 - 示例用法
    """
    # 示例数据
    example_data = {
        "圣保罗书院小学": [
        "约85%学生可升入直属中学圣保罗书院（Band 1A）"
        ],
        "嘉诺撒圣心学校": [
        "约85%学生升入直属中学嘉诺撒圣心书院（Band 1B）"
        ],
        "圣士提反女子中学附属小学": [
        "约85%学生升入直属中学圣士提反女子中学（Band 1A）"
        ],
        "圣嘉勒小学": [
        "约85%学生升入直属中学圣嘉勒女书院（Band 1B）"
        ],
        "慈幼学校": [
        "约64%升入直属中学慈幼英文学校（Band 2B）"
        ],
        "圣罗撒学校": [
        "约85%学生升入直属中学圣罗撒书院（Band 1B）"
        ],
        "香港培正小学": [
        "约85%学生升入直属中学香港培正中学（Band 1B）"
        ],
        "嘉诺撒圣家学校": [
        "约85%学生升入直属中学嘉诺撒圣家书院（Band 1B）"
        ],
        "喇沙小学": [
        "约85%学生升入直属中学喇沙中学（Band 1A）"
        ],
        "玛利诺修院学校（小学部）": [
        "约85%学生升入直属中学玛利诺修院学校（中学部）（Band 1A）"
        ],
        "嘉诺撒圣家学校（九龙塘）": [
        "约85%学生升入直属中学嘉诺撒圣家书院（Band 1B）"
        ],
        "民生书院小学": [
        "约85%学生升入直属中学民生书院（Band 1B）"
        ],
        "圣若瑟英文小学": [
        "55%"
        ],
        "圣士提反书院附属小学": [
        "约85%学生升入直属中学圣士提反书院（Band 1B）"
        ],
        "香港仔圣伯多祂天主教小学": [
        ""
        ],
        "玛利诺神父教会学校（小学部）": [
        "约80%学生升入直属中学玛利诺神父教会学校（中学部）（Band 1A）"
        ],
        "玛利曼小学": [
        "约85%学生升入直属中学玛利曼中学（Band 1B）"
        ],
        "高主教书院小学部": [
        "约85%学生升入直属中学高主教书院（Band 1B）"
        ],
        "嘉诺撒圣方济各学校": [
        "约85%学生升入直属中学嘉诺撒圣方济各书院（Band 1C）"
        ],
        "圣保禄天主教小学": [
        "约85%学生升入直属中学圣保禄中学（Band 1B）"
        ],
        "番禺会所华仁小学": [
        "约85%学生升入直属中学香港华仁书院（Band 1B）"
        ],
        "圣若瑟小学": [
        "约85%学生升入直属中学圣若瑟书院（Band 1B）"
        ],
        "圣保禄学校（小学部）": [
        "约85%学生升入直属中学圣保禄学校（Band 1A）"
        ]
    }
    
    print("导入描述性升学数据")
    print("=" * 80)
    
    # 从字典导入
    import_descriptions(example_data, source_type='dict')
    
    # 或者从文件导入
    # import_descriptions('promotion_descriptions.csv', source_type='csv')
    # import_descriptions('promotion_descriptions.json', source_type='json')


if __name__ == '__main__':
    main()

