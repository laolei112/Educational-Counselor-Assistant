#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为小学的 secondary_info 字段中的每个学校名称添加 banding 信息。

功能：
1. 遍历所有小学记录
2. 对于 secondary_info 中的 through_train、direct、associated 字段
3. 解析每个学校名称（用"、"分隔）
4. 在中学表中查找对应的 school_group（banding 信息）
5. 将 banding 信息添加到学校名称后面，格式如：嘉诺撒圣心书院（Band 1A）
6. 更新 secondary_info 字段

用法：
    cd backend
    python common/primary_data/add_banding_to_secondary_info.py
"""

import os
import sys
import re
from pathlib import Path
import django

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools
from backend.models.tb_secondary_schools import TbSecondarySchools
from backend.utils.text_converter import to_simplified


def normalize_school_name_for_match(name):
    """
    规范化学校名称，便于匹配
    """
    if not name:
        return ""
    name = name.strip()
    # 移除可能的 banding 信息（如果已经存在）
    name = re.sub(r'\s*\(Band\s+\d+[A-Z]?\)\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*（Band\s+\d+[A-Z]?）\s*$', '', name, flags=re.IGNORECASE)
    return name


def find_secondary_school_banding(school_name):
    """
    在中学表中查找学校名称对应的 banding 信息
    
    Args:
        school_name: 学校名称（可能是简体或繁体）
    
    Returns:
        school_group 字符串，如 "1A", "1B" 等，如果未找到则返回 None
    """
    if not school_name:
        return None
    
    # 规范化名称
    normalized_name = normalize_school_name_for_match(school_name)
    if not normalized_name:
        return None
    
    # 转换为简体（数据库中是简体）
    simplified_name = to_simplified(normalized_name)
    
    # 1. 简体完全匹配
    secondary_school = TbSecondarySchools.objects.filter(school_name=simplified_name).first()
    if secondary_school and secondary_school.school_group:
        return secondary_school.school_group
    
    # 2. 尝试繁体匹配（如果数据库中有繁体字段）
    secondary_school = TbSecondarySchools.objects.filter(school_name_traditional=normalized_name).first()
    if secondary_school and secondary_school.school_group:
        return secondary_school.school_group
    
    # 3. 尝试包含匹配（更宽松的匹配）
    secondary_school = TbSecondarySchools.objects.filter(
        school_name__icontains=simplified_name
    ).first()
    if secondary_school and secondary_school.school_group:
        return secondary_school.school_group
    
    return None


def format_school_name_with_banding(school_name, banding):
    """
    格式化学校名称，添加 banding 信息
    
    Args:
        school_name: 原始学校名称
        banding: banding 信息，如 "1A", "1B" 等
    
    Returns:
        格式化后的名称，如 "嘉诺撒圣心书院（Band 1A）"
    """
    if not banding:
        return school_name
    
    # 移除可能已存在的 banding 信息
    clean_name = re.sub(r'\s*\(Band\s+\d+[A-Z]?\)\s*$', '', school_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s*（Band\s+\d+[A-Z]?）\s*$', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s*（Band Band\s+\d+[A-Z]?）\s*$', '', clean_name, flags=re.IGNORECASE)
    clean_name = clean_name.strip()
    
    # 添加 banding 信息
    return f"{clean_name}（{banding}）"


def update_secondary_info_with_banding():
    """
    更新所有小学的 secondary_info 字段，为每个学校名称添加 banding 信息
    """
    print("=" * 60)
    print("开始更新小学 secondary_info 字段的 banding 信息")
    print("=" * 60)
    
    # 获取所有有 secondary_info 的小学
    primary_schools = TbPrimarySchools.objects.exclude(
        secondary_info__isnull=True
    ).exclude(secondary_info={})
    
    total_count = primary_schools.count()
    print(f"找到 {total_count} 所小学需要处理\n")
    
    updated_count = 0
    no_change_count = 0
    error_count = 0
    not_found_banding_count = 0
    
    # 需要处理的字段
    fields_to_process = ['through_train', 'direct', 'associated']
    
    for idx, primary_school in enumerate(primary_schools, 1):
        try:
            secondary_info = primary_school.secondary_info
            if not secondary_info or not isinstance(secondary_info, dict):
                continue
            
            updated = False
            new_secondary_info = dict(secondary_info)  # 创建副本
            
            # 处理每个字段
            for field in fields_to_process:
                if field not in new_secondary_info:
                    continue
                
                school_names_str = new_secondary_info[field]
                if not school_names_str or school_names_str == '-':
                    continue
                
                # 解析学校名称（用"、"分隔）
                school_names = [name.strip() for name in str(school_names_str).split('、') if name.strip()]
                
                updated_names = []
                for school_name in school_names:
                    # 检查是否已经有 banding 信息
                    # if re.search(r'\(Band\s+\d+[A-Z]?\)|（Band\s+\d+[A-Z]?）', school_name, re.IGNORECASE):
                    #     # 已经有 banding 信息，直接使用
                    #     updated_names.append(school_name)
                    #     continue
                    
                    # 查找 banding 信息
                    clean_name = re.sub(r'\s*\(Band\s+\d+[A-Z]?\)\s*$', '', school_name, flags=re.IGNORECASE)
                    clean_name = re.sub(r'\s*（Band\s+\d+[A-Z]?）\s*$', '', clean_name, flags=re.IGNORECASE)
                    clean_name = re.sub(r'\s*（Band Band\s+\d+[A-Z]?）\s*$', '', clean_name, flags=re.IGNORECASE)
                    clean_school_name = clean_name.strip()

                    banding = find_secondary_school_banding(clean_school_name)
                    if banding:
                        # 添加 banding 信息
                        formatted_name = format_school_name_with_banding(school_name, banding)
                        updated_names.append(formatted_name)
                        updated = True
                    else:
                        # 未找到 banding 信息，保持原样
                        updated_names.append(school_name)
                        not_found_banding_count += 1
                        print(f"  ⚠️  未找到 banding: {school_name}")
                
                # 更新字段
                if updated_names:
                    new_secondary_info[field] = '、'.join(updated_names)
                else:
                    new_secondary_info[field] = school_names_str
            
            # 如果有更新，保存到数据库
            if updated:
                primary_school.secondary_info = new_secondary_info
                primary_school.save(update_fields=['secondary_info'])
                updated_count += 1
                print(f"✅ [{idx}/{total_count}] 已更新: {primary_school.school_name}")
            else:
                no_change_count += 1
                if idx % 100 == 0:
                    print(f"⏭️  [{idx}/{total_count}] 无需更新: {primary_school.school_name}")
        
        except Exception as e:
            error_count += 1
            print(f"❌ [{idx}/{total_count}] 处理失败: {primary_school.school_name} - {str(e)}")
    
    # 输出统计信息
    print("\n" + "=" * 60)
    print("更新完成")
    print("=" * 60)
    print(f"总处理数: {total_count}")
    print(f"成功更新: {updated_count}")
    print(f"无需更新: {no_change_count}")
    print(f"处理失败: {error_count}")
    print(f"未找到 banding 的学校数: {not_found_banding_count}")
    print("=" * 60)


def main():
    """
    主函数
    """
    try:
        update_secondary_info_with_banding()
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

