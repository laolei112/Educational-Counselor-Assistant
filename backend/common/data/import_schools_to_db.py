#!/usr/bin/env python3
"""
学校数据导入脚本
从 JSON 文件读取学校数据并写入数据库
"""

import os
import sys
import json
import django
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_schools import TbSchools


def map_gender(gender_str):
    """映射性别字段"""
    gender_mapping = {
        '男女': 'coed',
        '男校': 'boys', 
        '女校': 'girls',
        '男': 'boys',
        '女': 'girls'
    }
    return gender_mapping.get(gender_str, 'coed')


def map_category(type_str):
    """映射学校分类字段"""
    category_mapping = {
        '官立': 'government',
        '資助': 'traditional',
        '直資': 'direct',
        '私立': 'private',
        '政府': 'government',
        '资助': 'traditional',
        '直资': 'direct',
        '私立': 'private'
    }
    return category_mapping.get(type_str, 'traditional')


def map_religion(religion_str):
    """映射宗教字段"""
    if not religion_str or religion_str in ['無', '无', '-', '']:
        return None
    return religion_str


def map_network(network_str):
    """映射校网字段"""
    if not network_str or network_str in ['-', '']:
        return None
    return network_str


def create_promotion_rate_data(school_data, is_secondary=False):
    """创建升学比例数据"""
    promotion_rate = {}
    
    if is_secondary and 'banding' in school_data:
        # 中学数据：提取 banding 信息
        banding = school_data.get('banding', '')
        if 'BAND 1' in banding:
            promotion_rate['band1_rate'] = 90  # 默认值，实际需要具体数据
        elif 'BAND 2' in banding:
            promotion_rate['band1_rate'] = 70
        else:
            promotion_rate['band1_rate'] = 50
    else:
        # 小学数据：默认值
        promotion_rate['band1_rate'] = 85
    
    # 添加联系学校信息
    promotion_rate['feeder_schools'] = []
    promotion_rate['linked_universities'] = []
    
    return promotion_rate


def process_primary_schools(json_file_path):
    """处理小学数据"""
    print(f"正在处理小学数据文件: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        schools_data = json.load(f)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for school_data in schools_data:
        try:
            # 检查学校是否已存在
            existing_school = TbSchools.objects.filter(name=school_data['name']).first()
            
            # 准备数据
            school_obj_data = {
                'name': school_data['name'],
                'url': school_data.get('url', ''),
                'level': 'primary',
                'category': map_category(school_data.get('type', '')),
                'net_name': map_network(school_data.get('network', '')),
                'religion': map_religion(school_data.get('religion', '')),
                'gender': map_gender(school_data.get('gender', '')),
                'address': school_data.get('address', ''),
                'district': school_data.get('district', ''),
                'official_website': school_data.get('official_website', ''),
                'promotion_rate': create_promotion_rate_data(school_data, False),
                'application_status': 'open',
                'tuition': 0,  # 默认学费
                'remarks': school_data.get('secondary_note', '')
            }
            
            if existing_school:
                # 更新现有记录
                for key, value in school_obj_data.items():
                    setattr(existing_school, key, value)
                existing_school.save()
                updated_count += 1
                print(f"更新小学: {school_data['name']}")
            else:
                # 创建新记录
                TbSchools.objects.create(**school_obj_data)
                created_count += 1
                print(f"创建小学: {school_data['name']}")
                
        except Exception as e:
            error_count += 1
            print(f"处理小学数据时出错: {school_data.get('name', 'Unknown')} - {str(e)}")
    
    return created_count, updated_count, error_count


def process_secondary_schools(json_file_path):
    """处理中学数据"""
    print(f"正在处理中学数据文件: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        schools_data = json.load(f)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for school_data in schools_data:
        try:
            # 检查学校是否已存在
            existing_school = TbSchools.objects.filter(name=school_data['name']).first()
            
            # 准备数据
            school_obj_data = {
                'name': school_data['name'],
                'url': school_data.get('url', ''),
                'level': 'secondary',
                'category': map_category(school_data.get('type', '')),
                'net_name': None,  # 中学数据中没有 network 字段
                'religion': map_religion(school_data.get('religion', '')),
                'gender': map_gender(school_data.get('gender', '')),
                'address': school_data.get('address', ''),
                'district': school_data.get('district', ''),
                'official_website': school_data.get('official_website', ''),
                'promotion_rate': create_promotion_rate_data(school_data, True),
                'application_status': 'open',
                'tuition': 0,  # 默认学费
                'remarks': f"语言: {school_data.get('language', '')}, 等级: {school_data.get('banding', '')}"
            }
            
            if existing_school:
                # 更新现有记录
                for key, value in school_obj_data.items():
                    setattr(existing_school, key, value)
                existing_school.save()
                updated_count += 1
                print(f"更新中学: {school_data['name']}")
            else:
                # 创建新记录
                TbSchools.objects.create(**school_obj_data)
                created_count += 1
                print(f"创建中学: {school_data['name']}")
                
        except Exception as e:
            error_count += 1
            print(f"处理中学数据时出错: {school_data.get('name', 'Unknown')} - {str(e)}")
    
    return created_count, updated_count, error_count


def main():
    """主函数"""
    print("开始导入学校数据到数据库...")
    print(f"开始时间: {datetime.now()}")
    
    # 文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    primary_file = os.path.join(current_dir, 'all_primary_schools.json')
    secondary_file = os.path.join(current_dir, 'all_secondary_schools.json')
    
    # 检查文件是否存在
    if not os.path.exists(primary_file):
        print(f"错误: 找不到小学数据文件 {primary_file}")
        return
    
    if not os.path.exists(secondary_file):
        print(f"错误: 找不到中学数据文件 {secondary_file}")
        return
    
    total_created = 0
    total_updated = 0
    total_errors = 0
    
    try:
        # 处理小学数据
        print("\n=== 处理小学数据 ===")
        created, updated, errors = process_primary_schools(primary_file)
        total_created += created
        total_updated += updated
        total_errors += errors
        
        # 处理中学数据
        print("\n=== 处理中学数据 ===")
        created, updated, errors = process_secondary_schools(secondary_file)
        total_created += created
        total_updated += updated
        total_errors += errors
        
        # 输出统计信息
        print("\n=== 导入完成 ===")
        print(f"总创建记录数: {total_created}")
        print(f"总更新记录数: {total_updated}")
        print(f"总错误数: {total_errors}")
        print(f"结束时间: {datetime.now()}")
        
        # 显示数据库中的总记录数
        total_schools = TbSchools.objects.count()
        primary_count = TbSchools.objects.filter(level='primary').count()
        secondary_count = TbSchools.objects.filter(level='secondary').count()
        
        print(f"\n数据库统计:")
        print(f"总学校数: {total_schools}")
        print(f"小学数: {primary_count}")
        print(f"中学数: {secondary_count}")
        
    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
