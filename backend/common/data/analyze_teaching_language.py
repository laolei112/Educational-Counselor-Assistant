#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析 Excel 中的授课语言数据，统计英文授课占比
不需要数据库连接，仅做数据分析
"""

import pandas as pd
import os


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
        '英文': [],
        '主要英文': [],
        '中英文并重': [],
        '主要中文': [],
        '中文': [],
        '无数据': []
    }
    
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
            stats[teaching_language].append({
                'name': school_name,
                'chinese_count': chinese_count,
                'english_count': english_count,
                'total_count': total_count,
                'english_ratio': english_ratio
            })
        else:
            stats['无数据'].append({'name': school_name})
        
        # 输出详细信息（前20条）
        if idx < 20:
            print(f"{idx + 1}. {school_name}")
            print(f"   中文科目数: {chinese_count}, 英文科目数: {english_count}")
            print(f"   总科目数: {total_count}, 英文占比: {english_ratio:.1f}%")
            print(f"   教学语言: {teaching_language or '无数据'}")
            if idx < 5:
                print(f"   中文科目: {', '.join(chinese_subjects[:5])}{' ...' if len(chinese_subjects) > 5 else ''}")
                print(f"   英文科目: {', '.join(english_subjects[:5])}{' ...' if len(english_subjects) > 5 else ''}")
            print()
    
    # 输出统计结果
    print("\n" + "="*80)
    print("统计结果汇总:")
    print("="*80)
    for label in ['英文', '主要英文', '中英文并重', '主要中文', '中文', '无数据']:
        count = len(stats[label])
        percentage = (count / len(df)) * 100 if len(df) > 0 else 0
        print(f"\n{label} ({count} 所学校, {percentage:.1f}%):")
        print("-" * 80)
        
        # 显示前5所学校的详细信息
        for i, school in enumerate(stats[label][:5]):
            if 'english_ratio' in school:
                print(f"  {i+1}. {school['name']}: "
                      f"中文{school['chinese_count']}科, 英文{school['english_count']}科, "
                      f"英文占比{school['english_ratio']:.1f}%")
            else:
                print(f"  {i+1}. {school['name']}: 无数据")
        
        if count > 5:
            print(f"  ... 还有 {count - 5} 所学校")
    
    print("\n" + "="*80)
    print("分析完成!")
    print("="*80)
    
    # 生成 SQL 更新语句
    print("\n生成 SQL 更新语句到文件...")
    sql_file = os.path.join(os.path.dirname(__file__), 'update_teaching_language.sql')
    
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- 更新中学授课语言数据\n")
        f.write("-- 根据 Excel 文件中的授课语言数据统计生成\n\n")
        
        for label in ['英文', '主要英文', '中英文并重', '主要中文', '中文']:
            if stats[label]:
                f.write(f"\n-- {label} ({len(stats[label])} 所学校)\n")
                for school in stats[label]:
                    school_name = school['name'].replace("'", "''")  # SQL 转义
                    f.write(f"UPDATE tb_secondary_schools SET teaching_language = '{label}' "
                           f"WHERE school_name = '{school_name}';\n")
    
    print(f"SQL 更新语句已保存到: {sql_file}")
    print("您可以执行该 SQL 文件来更新数据库。")


if __name__ == '__main__':
    main()

