#!/usr/bin/env python3
"""
更新小学数据库中的中英文名称
从 小学名称中英文对照.xlsx 读取中英文名称对照，更新 tb_primary_schools 表
"""

import os
import sys
import django
import pandas as pd
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 设置工作目录为backend目录
backend_dir = project_root / 'backend'
os.chdir(str(backend_dir))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


from backend.models.tb_primary_schools import TbPrimarySchools
from django.db import transaction


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
    english_name = ""
    while i < len(df):
        simple_school_name = str(df.iloc[i]['学校名称']).strip()
        traditional_school_name = str(df.iloc[i]['學校名稱']).strip()
        # 前两行是学校名称，不属于正式的学校名称，跳过
        if i < 1:
            i += 1
            continue
        # 奇数行为英文名称，偶数行为中文名称
        if i % 2 == 1:
            english_name = simple_school_name
        
        if i % 2 == 0:
            school_map.append({
                'traditional_school_name': traditional_school_name,
                'simple_school_name': simple_school_name,
                'english_name': english_name
            })
        i += 1

    print(f"成功解析 {len(school_map)} 所学校的中英文对照")
    return school_map


def match_school_in_db(simple_school_name):
    """
    在数据库中匹配小学
    """
    if not simple_school_name:
        return None
    
    # 1. 简体完全匹配（优先）
    queryset = TbPrimarySchools.objects.filter(school_name=simple_school_name)
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
    
    # 使用事务确保数据一致性
    with transaction.atomic():
        for i, school_info in enumerate(school_map):
            traditional_school_name = school_info['traditional_school_name']
            simple_school_name = school_info['simple_school_name']
            english_name = school_info['english_name']
            
            try:
                # 在数据库中查找学校
                db_school = match_school_in_db(simple_school_name)
                if db_school:
                    # 检查是否需要更新
                    needs_update = (
                        db_school.school_name_traditional != traditional_school_name or
                        db_school.school_name_english != english_name
                    )
                    
                    if needs_update:
                        # 更新英文名称，使用 update_fields 明确指定要更新的字段
                        db_school.school_name_traditional = traditional_school_name
                        db_school.school_name_english = english_name
                        db_school.save(update_fields=['school_name_traditional', 'school_name_english'])
                        
                        # 验证更新是否成功
                        db_school.refresh_from_db()
                        if (db_school.school_name_traditional == traditional_school_name and 
                            db_school.school_name_english == english_name):
                            updated_count += 1
                            print(f"✅ 更新: {db_school.school_name:35s} - 繁体: {traditional_school_name} - 英文: {english_name[:30]}")
                        else:
                            error_count += 1
                            print(f"⚠️  更新失败: {db_school.school_name:35s} - 数据未正确保存")
                    else:
                        print(f"⏭️  跳过: {db_school.school_name:35s} - 数据已是最新")
                else:
                    not_found_count += 1
                    not_found_schools.append(simple_school_name)
                    print(f"❌ 未找到: {simple_school_name:35s}")
            except Exception as e:
                error_count += 1
                print(f"❌ 错误: {simple_school_name:35s} - {str(e)}")
                import traceback
                traceback.print_exc()
    
    # 打印总结
    print("\n" + "=" * 80)
    print("更新结果")
    print("=" * 80)
    print(f"成功更新: {updated_count} 所")
    print(f"未找到: {not_found_count} 所")
    print(f"错误: {error_count} 所")
    
    if not_found_schools and len(not_found_schools) <= 20:
        print("\n未找到的学校列表:")
        for school in not_found_schools:
            print(f"  - {school}")

    return updated_count, not_found_count


def main():
    """
    主函数
    """
    print("=" * 80)
    print("更新小学数据库中的中英文名称")
    print("=" * 80)
    
    # Excel文件路径
    excel_file = Path(__file__).parent / '小学名称中英文对照.xlsx'
    
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
