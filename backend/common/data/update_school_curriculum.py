#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 Excel 中提取教学语言课程数据，更新到数据库的 school_curriculum 字段
格式：{"中文授课": [], "英文授课": []}
"""

import os
import sys
import django
import pandas as pd
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_secondary_schools import TbSecondarySchools


def parse_subjects(subject_str):
    """
    解析科目字符串，提取科目列表
    - 用、分隔科目
    - 忽略 <br> 及其后的内容（非DSE课程）
    """
    if pd.isna(subject_str) or not subject_str:
        return []
    
    # 转换为字符串
    subject_str = str(subject_str)
    
    # 忽略 <br> 及其后的内容
    if '<br>' in subject_str:
        subject_str = subject_str.split('<br>')[0]
    
    # 使用、分隔科目
    subjects = [s.strip() for s in subject_str.split('、') if s.strip()]
    
    return subjects


def main():
    """
    主函数
    """
    # 读取 Excel 文件
    excel_file = os.path.join(os.path.dirname(__file__), '香港各中学信息.xlsx')
    print(f"正在读取 Excel 文件: {excel_file}")
    
    df = pd.read_excel(excel_file)
    
    print(f"共读取 {len(df)} 条学校数据")
    print("\n开始处理课程数据...\n")
    
    update_count = 0
    not_found_count = 0
    no_data_count = 0
    
    # 遍历每所学校
    for idx, row in df.iterrows():
        school_name = row['学校名称']
        
        # 解析中文和英文授课科目
        chinese_subjects = parse_subjects(row['以中文为教学语言_中四至中六'])
        english_subjects = parse_subjects(row['以英文为教学语言_中四至中六'])
        
        # 如果两个都为空，跳过
        if not chinese_subjects and not english_subjects:
            no_data_count += 1
            continue
        
        # 构建课程数据
        curriculum_data = {
            "中文授课": chinese_subjects,
            "英文授课": english_subjects
        }
        
        # 转换为 JSON 字符串
        curriculum_json = json.dumps(curriculum_data, ensure_ascii=False)
        
        # 输出详细信息（前10条）
        if idx < 10:
            print(f"{idx + 1}. {school_name}")
            print(f"   中文授课科目（{len(chinese_subjects)}）: {', '.join(chinese_subjects[:3])}{' ...' if len(chinese_subjects) > 3 else ''}")
            print(f"   英文授课科目（{len(english_subjects)}）: {', '.join(english_subjects[:3])}{' ...' if len(english_subjects) > 3 else ''}")
            print(f"   JSON: {curriculum_json[:100]}...")
            print()
        
        # 更新数据库
        try:
            school = TbSecondarySchools.objects.get(school_name=school_name)
            school.school_curriculum = curriculum_json
            school.save()
            update_count += 1
        except TbSecondarySchools.DoesNotExist:
            not_found_count += 1
            if idx < 10:  # 只打印前10个未找到的
                print(f"   ⚠️  数据库中未找到学校: {school_name}")
        except Exception as e:
            print(f"   ❌ 更新失败: {school_name}, 错误: {str(e)}")
    
    # 输出统计结果
    print("\n" + "="*60)
    print("数据库更新结果:")
    print("="*60)
    print(f"成功更新: {update_count} 所学校")
    print(f"未找到: {not_found_count} 所学校")
    print(f"无课程数据: {no_data_count} 所学校")
    print(f"总计: {len(df)} 所学校")
    print("="*60)
    
    # 验证数据
    print("\n" + "="*60)
    print("验证更新结果（前5条）:")
    print("="*60)
    schools = TbSecondarySchools.objects.exclude(school_curriculum__isnull=True).exclude(school_curriculum='')[:5]
    for school in schools:
        try:
            curriculum = json.loads(school.school_curriculum)
            print(f"\n{school.school_name}:")
            print(f"  中文授课: {len(curriculum.get('中文授课', []))} 科")
            print(f"  英文授课: {len(curriculum.get('英文授课', []))} 科")
        except:
            print(f"{school.school_name}: 数据格式错误")


if __name__ == '__main__':
    main()

