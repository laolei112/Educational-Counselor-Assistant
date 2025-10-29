#!/usr/bin/env python3
"""
更新中学数据库中的中英文名称
从 中学名称中英文对照.xlsx 读取中英文名称对照，更新 tb_secondary_schools 表
"""

import os
import sys
import django
import pandas as pd
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


from backend.models.tb_secondary_schools import TbSecondarySchools


def normalize_school_name(name):
    """
    规范化学校名称，便于匹配
    """
    if not name:
        return name
    
    # 移除常见的后缀和前缀
    name = str(name).strip()
    replacements = {
        '（': '(',
        '）': ')',
        '　': ' ',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def load_school_name_mapping(excel_file):
    """
    从Excel文件加载学校名称对照表
    """
    print(f"正在读取Excel文件: {excel_file}")
    school_map = []
    # 读取Excel文件
    df = pd.read_excel(excel_file)

    i = 0
    while i < len(df):
        english_name = str(df.iloc[i]['school_name']).strip()
        simple_school_name = str(df.iloc[i]['学校名称']).strip()
        school_map.append({
            'english_name': english_name,
            'simple_school_name': simple_school_name,
        })
        i += 1

    print(f"成功解析 {len(school_map)} 所学校的中英文对照")
    return school_map


def match_school_in_db(simple_school_name):
    """
    在数据库中匹配中学
    """
    if not simple_school_name:
        return None
    
    # 1. 简体完全匹配（优先）
    queryset = TbSecondarySchools.objects.filter(school_name=simple_school_name)
    if queryset.exists():
        return queryset.first()
    print(f"未找到 {simple_school_name}")
    return None


def update_school_names(school_map):
    """
    更新数据库中的学校名称
    """
    print("\n开始更新数据库...")
    
    # 统计
    updated_count = 0
    not_found_count = 0
    error_count = 0
    not_found_schools = []
    
    for i, school_info in enumerate(school_map):
        simple_school_name = school_info['simple_school_name']
        english_name = school_info['english_name']
        
        try:
            # 在数据库中查找学校
            db_school = match_school_in_db(simple_school_name)
            if db_school:
                # 更新英文名称
                db_school.school_name_english = english_name
                db_school.save()
                updated_count += 1
                print(f"✅ 更新: {db_school.school_name:35s} - 英文: {english_name[:30]}")
            else:
                not_found_count += 1
                not_found_schools.append(simple_school_name)
                print(f"❌ 未找到: {simple_school_name:35s}")
        except Exception as e:
            error_count += 1
            print(f"❌ 错误: {simple_school_name:35s} - {str(e)}")
    
    # 打印总结
    print("\n" + "=" * 80)
    print("更新结果")
    print("=" * 80)
    print(f"成功更新: {updated_count} 所")
    print(f"未找到: {not_found_count} 所")

    return updated_count, not_found_count


def main():
    """
    主函数
    """
    print("=" * 80)
    print("更新小学数据库中的中英文名称")
    print("=" * 80)
    
    # Excel文件路径
    excel_file = Path(__file__).parent / '中学英文名.xlsx'
    
    if not excel_file.exists():
        print(f"\n❌ 错误：找不到Excel文件: {excel_file}")
        return
    
    # 加载学校名称对照表
    school_map = load_school_name_mapping(excel_file)
    
    if not school_map:
        print("\n❌ 错误：未能从Excel文件中解析出学校名称")
        return

    # 更新数据库
    updated_count, not_found_count = update_school_names(school_map)
    
    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()
