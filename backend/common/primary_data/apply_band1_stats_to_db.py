#!/usr/bin/env python3
"""
将小学升学统计结果应用到数据库
从 primary_schools_band1_stats.json 读取统计数据，更新 tb_primary_schools 表的 promotion_info 字段
"""

import os
import sys
import django
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools


def normalize_school_name(name):
    """
    规范化学校名称，便于匹配
    """
    # 移除常见的后缀和前缀
    name = name.strip()
    replacements = {
        '（': '(',
        '）': ')',
        '　': ' ',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def match_school_in_db(school_name, district=None):
    """
    在数据库中匹配小学
    """
    # 规范化名称
    normalized_name = normalize_school_name(school_name)
    
    # 尝试完全匹配
    queryset = TbPrimarySchools.objects.filter(school_name=normalized_name)
    if district:
        queryset = queryset.filter(district__icontains=district.replace('区', ''))
    
    if queryset.exists():
        return queryset.first()
    
    # 尝试包含匹配
    queryset = TbPrimarySchools.objects.filter(school_name__icontains=normalized_name)
    if district:
        queryset = queryset.filter(district__icontains=district.replace('区', ''))
    
    if queryset.exists():
        return queryset.first()
    
    # 反向匹配
    queryset = TbPrimarySchools.objects.filter(school_name__contains=school_name)
    if district:
        queryset = queryset.filter(district__icontains=district.replace('区', ''))
    
    if queryset.exists():
        return queryset.first()
    
    return None


def apply_stats_to_database(stats_file):
    """
    将统计结果应用到数据库
    """
    print(f"正在读取统计结果: {stats_file}")
    
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    schools_data = stats.get('schools', [])
    districts_data = stats.get('districts', [])
    
    print(f"找到 {len(schools_data)} 所小学的统计数据")
    
    # 建立学校名称到区域的映射
    school_to_district = {}
    for district_data in districts_data:
        district = district_data['district']
        for school in district_data['schools']:
            school_to_district[school['primary_school']] = district
    
    # 统计
    updated_count = 0
    not_found_count = 0
    error_count = 0
    not_found_schools = []
    
    for school_stat in schools_data:
        primary_school = school_stat['primary_school']
        district = school_to_district.get(primary_school)
        
        try:
            # 在数据库中查找学校
            db_school = match_school_in_db(primary_school, district)
            
            if db_school:
                # 更新 promotion_info 字段
                db_school.promotion_info = {
                    'band1_rate': school_stat['band1_rate'],
                    'total_graduates': school_stat['total_students'],
                    'band1_graduates': school_stat['band1_students'],
                    'band_distribution': school_stat['band_distribution'],
                    'top_secondary_schools': [
                        {'school': k, 'count': v} 
                        for k, v in list(school_stat['secondary_schools'].items())[:10]
                    ],
                    'data_source': 'excel_import',
                    'last_updated': '2025-10-19'
                }
                db_school.save()
                
                updated_count += 1
                print(f"✅ 更新: {db_school.school_name:35s} - Band 1: {school_stat['band1_rate']}%")
            else:
                not_found_count += 1
                not_found_schools.append(primary_school)
                print(f"⚠️  未找到: {primary_school:35s} (区域: {district})")
        
        except Exception as e:
            error_count += 1
            print(f"❌ 错误: {primary_school:35s} - {str(e)}")
    
    # 打印总结
    print("\n" + "=" * 80)
    print("应用结果")
    print("=" * 80)
    print(f"成功更新: {updated_count} 所")
    print(f"未找到: {not_found_count} 所")
    print(f"错误: {error_count} 所")
    
    if not_found_schools:
        print(f"\n未找到的小学列表:")
        for school in not_found_schools[:20]:
            print(f"  - {school}")
        if len(not_found_schools) > 20:
            print(f"  ... 还有 {len(not_found_schools) - 20} 所")
    
    # 保存未匹配的学校
    if not_found_schools:
        unmatched_file = Path(stats_file).parent / 'unmatched_schools.txt'
        with open(unmatched_file, 'w', encoding='utf-8') as f:
            f.write("未在数据库中找到的小学列表\n")
            f.write("=" * 80 + "\n\n")
            for school in not_found_schools:
                district = school_to_district.get(school, '未知')
                f.write(f"{school} ({district})\n")
        print(f"\n未匹配学校列表已保存到: {unmatched_file}")


def verify_update():
    """
    验证更新结果
    """
    print("\n" + "=" * 80)
    print("验证更新结果")
    print("=" * 80)
    
    # 统计有 promotion_info 的学校
    total_schools = TbPrimarySchools.objects.count()
    with_promotion = TbPrimarySchools.objects.exclude(promotion_info__isnull=True).count()
    
    print(f"\n数据库统计:")
    print(f"  总小学数: {total_schools}")
    print(f"  有升学数据: {with_promotion}")
    print(f"  覆盖率: {(with_promotion/total_schools*100):.2f}%")
    
    # 显示几个示例
    print(f"\n示例数据:")
    schools = TbPrimarySchools.objects.exclude(promotion_info__isnull=True)[:5]
    for school in schools:
        info = school.promotion_info
        print(f"  {school.school_name:30s} - Band 1: {info.get('band1_rate', 0)}%")


def main():
    """
    主函数
    """
    print("=" * 80)
    print("将小学升学统计结果应用到数据库")
    print("=" * 80)
    
    # 统计文件路径
    stats_file = Path(__file__).parent / 'primary_schools_band1_stats.json'
    
    if not stats_file.exists():
        print(f"\n❌ 错误：找不到统计文件: {stats_file}")
        print("请先运行 calculate_primary_band1_rate.py 生成统计数据")
        return
    
    # 应用统计数据到数据库
    apply_stats_to_database(stats_file)
    
    # 验证更新结果
    verify_update()
    
    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()

