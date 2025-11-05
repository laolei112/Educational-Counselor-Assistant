#!/usr/bin/env python3
"""
将英文学校.xlsx文件中的英文学校名称转换为繁体中文
使用中学英文名.xlsx或中学banding信息_new.xlsx作为映射表
输出为中文学校.xlsx文件，保持相同的组织结构
"""

import os
import pandas as pd
from pathlib import Path
import re


def normalize_school_name(name):
    """
    规范化学校名称，用于匹配
    移除多余空格、标点符号等
    """
    if not name or pd.isna(name):
        return None
    
    name = str(name).strip()
    # 移除多余空格
    name = re.sub(r'\s+', ' ', name)
    # 转换为小写用于匹配（但保留原始格式）
    return name


def load_school_name_mapping(mapping_files):
    """
    从映射文件加载英文到繁体中文的学校名称对照表
    
    Args:
        mapping_files: 映射文件路径列表（可以是单个文件或列表）
        
    Returns:
        dict: {英文名称: 繁体中文名称} 的字典
    """
    if isinstance(mapping_files, str):
        mapping_files = [mapping_files]
    
    mapping = {}
    
    for mapping_file in mapping_files:
        if not os.path.exists(mapping_file):
            print(f"⚠️  跳过不存在的映射文件: {mapping_file}")
            continue
        
        print(f"正在读取映射文件: {mapping_file}")
        df = pd.read_excel(mapping_file)
        
        # 检查文件类型
        if 'school_name' in df.columns and '學校名稱' in df.columns:
            # 中学英文名.xlsx 格式
            count = 0
            for _, row in df.iterrows():
                english_name = str(row['school_name']).strip() if pd.notna(row['school_name']) else None
                traditional_name = str(row['學校名稱']).strip() if pd.notna(row['學校名稱']) else None
                
                if english_name and traditional_name:
                    # 创建多个映射键以提高匹配率
                    normalized_english = normalize_school_name(english_name)
                    if normalized_english:
                        mapping[normalized_english.lower()] = traditional_name
                        # 也保存原始大小写的映射
                        mapping[english_name] = traditional_name
                        count += 1
            
            print(f"  ✅ 从此文件加载了 {count} 个映射关系")
        
        elif 'school_name' in df.columns and 'school_name_tranditional' in df.columns:
            # 中学banding信息_new.xlsx 格式
            count = 0
            for _, row in df.iterrows():
                school_name = str(row['school_name']).strip() if pd.notna(row['school_name']) else None
                traditional_name = str(row['school_name_tranditional']).strip() if pd.notna(row['school_name_tranditional']) else None
                
                # 检查是否是英文名称（包含字母）
                if school_name and traditional_name and re.search(r'[A-Za-z]', school_name):
                    normalized_english = normalize_school_name(school_name)
                    if normalized_english:
                        mapping[normalized_english.lower()] = traditional_name
                        mapping[school_name] = traditional_name
                        count += 1
            
            print(f"  ✅ 从此文件加载了 {count} 个映射关系")
        
        else:
            print(f"  ⚠️  无法识别此文件格式，列名: {df.columns.tolist()}")
    
    print(f"\n✅ 总共加载了 {len(mapping)} 个唯一的映射关系")
    return mapping


def normalize_for_matching(name):
    """
    规范化名称用于匹配，处理各种格式差异
    """
    if not name:
        return ""
    
    name = str(name).strip()
    # 移除标点符号和空格差异
    name = re.sub(r'[.,\s]+', ' ', name)  # 将标点和空格统一为单个空格
    name = name.replace("'", "")  # 移除撇号
    name = re.sub(r'\s+', ' ', name).strip()  # 统一空格
    # 处理缩写：HK -> Hong Kong, SKH -> S.K.H.
    name = re.sub(r'\bHK\b', 'Hong Kong', name, flags=re.IGNORECASE)
    name = re.sub(r'\bSKH\b', 'S.K.H.', name, flags=re.IGNORECASE)
    name = re.sub(r'\bKLN\b', 'Kowloon', name, flags=re.IGNORECASE)
    return name.lower()


def match_school_name(english_name, mapping):
    """
    匹配英文学校名称，返回繁体中文名称
    
    Args:
        english_name: 英文学校名称
        mapping: 映射字典
        
    Returns:
        str: 繁体中文名称，如果找不到则返回原英文名称
    """
    if not english_name or pd.isna(english_name):
        return english_name
    
    english_name = str(english_name).strip()
    
    # 1. 精确匹配（原始大小写）
    if english_name in mapping:
        return mapping[english_name]
    
    # 2. 小写匹配
    normalized = normalize_school_name(english_name)
    if normalized and normalized.lower() in mapping:
        return mapping[normalized.lower()]
    
    # 3. 规范化后匹配（处理缩写、标点等）
    normalized_for_match = normalize_for_matching(english_name)
    for key, value in mapping.items():
        normalized_key = normalize_for_matching(key)
        if normalized_for_match == normalized_key:
            return value
    
    # 4. 部分匹配（移除常见后缀）
    # 移除 "School", "College", "Secondary School" 等后缀后再匹配
    patterns_to_remove = [
        r'\s+School\s*$',
        r'\s+College\s*$',
        r'\s+Secondary School\s*$',
        r'\s+Secondary\s*$',
    ]
    
    base_name = english_name
    for pattern in patterns_to_remove:
        base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
    
    if base_name != english_name:
        normalized_base = normalize_school_name(base_name)
        if normalized_base and normalized_base.lower() in mapping:
            return mapping[normalized_base.lower()]
        if base_name in mapping:
            return mapping[base_name]
        
        # 规范化后匹配基础名称
        normalized_base_for_match = normalize_for_matching(base_name)
        for key, value in mapping.items():
            normalized_key = normalize_for_matching(key)
            if normalized_base_for_match == normalized_key:
                return value
    
    # 5. 模糊匹配（包含关系，但要求匹配度较高）
    # 提取关键单词进行匹配
    words = re.findall(r'\b\w+\b', normalize_for_matching(english_name))
    if len(words) >= 2:  # 至少需要2个单词
        best_match = None
        best_score = 0
        for key, value in mapping.items():
            key_words = re.findall(r'\b\w+\b', normalize_for_matching(key))
            # 计算匹配的单词数量
            matched_words = sum(1 for w in words if w in key_words)
            if matched_words >= 2 and matched_words > best_score:
                best_score = matched_words
                best_match = value
        
        if best_match:
            return best_match
    
    # 6. 最后的模糊匹配（简单包含关系）
    for key, value in mapping.items():
        normalized_key = normalize_for_matching(key)
        # 检查是否包含关键部分（至少3个字符）
        if len(normalized_for_match) >= 5 and len(normalized_key) >= 5:
            if normalized_for_match[:5] in normalized_key or normalized_key[:5] in normalized_for_match:
                return value
    
    # 如果都找不到，返回原英文名称
    print(f"⚠️  未找到映射: {english_name}")
    return english_name


def convert_sheet(df, mapping, sheet_name=None):
    """
    转换单个sheet中的英文学校名称为繁体中文
    
    Args:
        df: DataFrame对象
        mapping: 映射字典
        sheet_name: sheet名称（用于显示）
        
    Returns:
        tuple: (转换后的DataFrame, 转换统计信息)
    """
    sheet_info = f" (Sheet: {sheet_name})" if sheet_name else ""
    
    # 检查是否有"升入学校"列
    if '升入学校' not in df.columns:
        print(f"⚠️  警告{sheet_info}：找不到'升入学校'列，跳过此sheet")
        print(f"  可用列: {df.columns.tolist()}")
        return df, {'converted': 0, 'not_found': 0, 'total': len(df)}
    
    # 创建输出DataFrame的副本
    output_df = df.copy()
    
    # 转换学校名称
    converted_count = 0
    not_found_count = 0
    
    for idx, row in df.iterrows():
        english_name = row['升入学校']
        
        if pd.notna(english_name):
            chinese_name = match_school_name(english_name, mapping)
            
            if chinese_name != english_name:
                output_df.at[idx, '升入学校'] = chinese_name
                converted_count += 1
                if converted_count <= 10:  # 只显示前10个转换示例
                    print(f"  {english_name:50s} -> {chinese_name}")
            else:
                not_found_count += 1
    
    return output_df, {'converted': converted_count, 'not_found': not_found_count, 'total': len(df)}


def convert_excel_file(input_file, output_file, mapping_files):
    """
    转换Excel文件中的英文学校名称为繁体中文（支持多个sheet）
    
    Args:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径
        mapping_files: 映射文件路径（可以是单个文件或列表）
    """
    print("=" * 80)
    print("英文学校名称转繁体中文")
    print("=" * 80)
    
    # 加载映射表
    mapping = load_school_name_mapping(mapping_files)
    
    if not mapping:
        print("❌ 错误：无法加载映射表")
        return
    
    # 读取输入文件的所有sheet
    print(f"\n正在读取输入文件: {input_file}")
    if not os.path.exists(input_file):
        print(f"❌ 错误：找不到输入文件: {input_file}")
        return
    
    # 读取所有sheet
    excel_file = pd.ExcelFile(input_file)
    sheet_names = excel_file.sheet_names
    print(f"✅ 找到 {len(sheet_names)} 个sheet: {sheet_names}")
    
    # 转换每个sheet
    converted_sheets = {}
    total_stats = {'converted': 0, 'not_found': 0, 'total': 0}
    
    print("\n开始转换学校名称...")
    for sheet_name in sheet_names:
        print(f"\n--- 处理 Sheet: {sheet_name} ---")
        df = pd.read_excel(input_file, sheet_name=sheet_name)
        print(f"  读取了 {len(df)} 行数据")
        print(f"  列名: {df.columns.tolist()}")
        
        output_df, stats = convert_sheet(df, mapping, sheet_name)
        converted_sheets[sheet_name] = output_df
        
        total_stats['converted'] += stats['converted']
        total_stats['not_found'] += stats['not_found']
        total_stats['total'] += stats['total']
        
        print(f"  ✅ Sheet '{sheet_name}': 转换 {stats['converted']} 个，未找到 {stats['not_found']} 个")
    
    # 保存输出文件（所有sheet）
    print(f"\n正在保存输出文件: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in converted_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"✅ 文件已保存，包含 {len(converted_sheets)} 个sheet")
    
    # 打印统计信息
    print("\n" + "=" * 80)
    print("转换结果总结")
    print("=" * 80)
    print(f"处理的Sheet数量: {len(sheet_names)}")
    print(f"总行数: {total_stats['total']}")
    print(f"成功转换: {total_stats['converted']} 个")
    print(f"未找到映射: {total_stats['not_found']} 个")
    print(f"输出文件: {output_file}")
    print("=" * 80)


def main():
    """
    主函数
    """
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    
    # 文件路径
    input_file = script_dir / '英文学校.xlsx'
    
    # 使用两个映射文件（如果存在）
    mapping_file_1 = Path(__file__).parent.parent / 'data' / '中学英文名.xlsx'
    mapping_file_2 = script_dir / '中学banding信息_new.xlsx'
    
    mapping_files = []
    if mapping_file_1.exists():
        mapping_files.append(mapping_file_1)
        print(f"找到映射文件: {mapping_file_1}")
    if mapping_file_2.exists():
        mapping_files.append(mapping_file_2)
        print(f"找到映射文件: {mapping_file_2}")
    
    if not mapping_files:
        print(f"❌ 错误：找不到映射文件")
        print(f"  尝试查找: {mapping_file_1}")
        print(f"  尝试查找: {mapping_file_2}")
        return
    
    output_file = script_dir / '中文学校.xlsx'
    
    # 执行转换
    convert_excel_file(input_file, output_file, mapping_files)
    
    print("\n完成!")


if __name__ == '__main__':
    main()

