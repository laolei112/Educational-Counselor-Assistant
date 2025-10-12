#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根据 Excel 中的授课语言数据统计英文授课占比，并更新到数据库
"""

import os
import sys
import django
import pandas as pd
import re

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
    - 忽略 <br> 及其后的内容
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


def calculate_english_ratio(chinese_subjects, english_subjects):
    """
    计算英文授课占比
    """
    chinese_count = len(chinese_subjects)
    english_count = len(english_subjects)
    total_count = chinese_count + english_count
    
    if total_count == 0:
        return 0, 0, 0, 0
    
    english_ratio = (english_count / total_count) * 100
    
    return chinese_count, english_count, total_count, english_ratio


def get_teaching_language_label(english_ratio, chinese_count, english_count):
    """
    根据英文授课占比返回教学语言标签
    """
    if chinese_count == 0 and english_count == 0:
        return None
    
    if english_ratio >= 80:
        return "英文"
    elif english_ratio >= 60:
        return "主要英文"
    elif english_ratio >= 40:
        return "中英文并重"
    elif english_ratio >= 20:
        return "主要中文"
    else:
        return "中文"


def main():
    """
    主函数
    """
    # 读取 Excel 文件
    excel_file = os.path.join(os.path.dirname(__file__), '香港各中学信息.xlsx')
    print(f"正在读取 Excel 文件: {excel_file}")
    
    df = pd.read_excel(excel_file)
    
    print(f"共读取 {len(df)} 条学校数据")
    print("\n开始分析授课语言数据...\n")
    
    # 统计信息
    stats = {
        '英文': 0,
        '主要英文': 0,
        '中英文并重': 0,
        '主要中文': 0,
        '中文': 0,
        '无数据': 0
    }
    
    update_count = 0
    not_found_count = 0
    
    # 遍历每所学校
    for idx, row in df.iterrows():
        school_name = row['学校名称']
        
        # 解析中文和英文授课科目
        chinese_subjects = parse_subjects(row['以中文为教学语言_中四至中六'])
        english_subjects = parse_subjects(row['以英文为教学语言_中四至中六'])
        
        # 计算英文授课占比
        chinese_count, english_count, total_count, english_ratio = calculate_english_ratio(
            chinese_subjects, english_subjects
        )
        
        # 获取教学语言标签
        teaching_language = get_teaching_language_label(english_ratio, chinese_count, english_count)
        
        # 更新统计
        if teaching_language:
            stats[teaching_language] += 1
        else:
            stats['无数据'] += 1
        
        # 输出详细信息（前10条）
        if idx < 10:
            print(f"{idx + 1}. {school_name}")
            print(f"   中文科目数: {chinese_count}, 英文科目数: {english_count}")
            print(f"   总科目数: {total_count}, 英文占比: {english_ratio:.1f}%")
            print(f"   教学语言: {teaching_language or '无数据'}")
            print()
        
        # 更新数据库
        try:
            school = TbSecondarySchools.objects.get(school_name=school_name)
            school.teaching_language = teaching_language
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
    print("统计结果:")
    print("="*60)
    for label, count in stats.items():
        percentage = (count / len(df)) * 100 if len(df) > 0 else 0
        print(f"{label:12s}: {count:3d} 所学校 ({percentage:5.1f}%)")
    
    print("\n" + "="*60)
    print("数据库更新结果:")
    print("="*60)
    print(f"成功更新: {update_count} 所学校")
    print(f"未找到: {not_found_count} 所学校")
    print(f"总计: {len(df)} 所学校")
    print("="*60)


if __name__ == '__main__':
    main()

