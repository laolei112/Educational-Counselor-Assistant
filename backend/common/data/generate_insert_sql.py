#!/usr/bin/env python3
"""
生成 INSERT SQL 语句脚本
从 JSON 文件读取学校数据并生成 SQL 插入语句
"""

import json
import os
from datetime import datetime


def escape_sql_string(value):
    """转义 SQL 字符串"""
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        # 转义单引号
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return str(value)


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


def create_promotion_rate_json(school_data, is_secondary=False):
    """创建升学比例 JSON 数据"""
    promotion_rate = {}
    
    if is_secondary and 'banding' in school_data:
        # 中学数据：提取 banding 信息
        banding = school_data.get('banding', '')
        if 'BAND 1' in banding:
            promotion_rate['band1_rate'] = 90
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
    
    return json.dumps(promotion_rate, ensure_ascii=False)


def generate_sql_for_primary_schools(json_file_path, output_file):
    """为小学数据生成 SQL"""
    print(f"正在处理小学数据文件: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        schools_data = json.load(f)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- 小学数据 INSERT 语句\n")
        f.write(f"-- 生成时间: {datetime.now()}\n")
        f.write(f"-- 数据条数: {len(schools_data)}\n\n")
        
        for school_data in schools_data:
            try:
                sql = f"""INSERT INTO tb_schools (
    name, url, level, category, net_name, religion, gender, 
    address, district, official_website, promotion_rate, 
    application_status, tuition, remarks, created_at, updated_at
) VALUES (
    {escape_sql_string(school_data['name'])},
    {escape_sql_string(school_data.get('url', ''))},
    'primary',
    {escape_sql_string(map_category(school_data.get('type', '')))},
    {escape_sql_string(map_network(school_data.get('network', '')))},
    {escape_sql_string(map_religion(school_data.get('religion', '')))},
    {escape_sql_string(map_gender(school_data.get('gender', '')))},
    {escape_sql_string(school_data.get('address', ''))},
    {escape_sql_string(school_data.get('district', ''))},
    {escape_sql_string(school_data.get('official_website', ''))},
    {escape_sql_string(create_promotion_rate_json(school_data, False))},
    'open',
    0,
    {escape_sql_string(school_data.get('secondary_note', ''))},
    NOW(),
    NOW()
);

"""
                f.write(sql)
                
            except Exception as e:
                print(f"处理小学数据时出错: {school_data.get('name', 'Unknown')} - {str(e)}")
                continue


def generate_sql_for_secondary_schools(json_file_path, output_file):
    """为中学数据生成 SQL"""
    print(f"正在处理中学数据文件: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        schools_data = json.load(f)
    
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\n-- 中学数据 INSERT 语句\n")
        f.write(f"-- 生成时间: {datetime.now()}\n")
        f.write(f"-- 数据条数: {len(schools_data)}\n\n")
        
        for school_data in schools_data:
            try:
                remarks = f"语言: {school_data.get('language', '')}, 等级: {school_data.get('banding', '')}"
                
                sql = f"""INSERT INTO tb_schools (
    name, url, level, category, net_name, religion, gender, 
    address, district, official_website, promotion_rate, 
    application_status, tuition, remarks, created_at, updated_at
) VALUES (
    {escape_sql_string(school_data['name'])},
    {escape_sql_string(school_data.get('url', ''))},
    'secondary',
    {escape_sql_string(map_category(school_data.get('type', '')))},
    NULL,
    {escape_sql_string(map_religion(school_data.get('religion', '')))},
    {escape_sql_string(map_gender(school_data.get('gender', '')))},
    {escape_sql_string(school_data.get('address', ''))},
    {escape_sql_string(school_data.get('district', ''))},
    {escape_sql_string(school_data.get('official_website', ''))},
    {escape_sql_string(create_promotion_rate_json(school_data, True))},
    'open',
    0,
    {escape_sql_string(remarks)},
    NOW(),
    NOW()
);

"""
                f.write(sql)
                
            except Exception as e:
                print(f"处理中学数据时出错: {school_data.get('name', 'Unknown')} - {str(e)}")
                continue


def main():
    """主函数"""
    print("开始生成学校数据 INSERT SQL 语句...")
    print(f"开始时间: {datetime.now()}")
    
    # 文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    primary_file = os.path.join(current_dir, 'all_primary_schools.json')
    secondary_file = os.path.join(current_dir, 'all_secondary_schools.json')
    output_file = os.path.join(current_dir, 'insert_schools_data.sql')
    
    # 检查文件是否存在
    if not os.path.exists(primary_file):
        print(f"错误: 找不到小学数据文件 {primary_file}")
        return
    
    if not os.path.exists(secondary_file):
        print(f"错误: 找不到中学数据文件 {secondary_file}")
        return
    
    try:
        # 生成小学数据 SQL
        print("\n=== 生成小学数据 SQL ===")
        generate_sql_for_primary_schools(primary_file, output_file)
        
        # 生成中学数据 SQL
        print("\n=== 生成中学数据 SQL ===")
        generate_sql_for_secondary_schools(secondary_file, output_file)
        
        print(f"\n=== SQL 生成完成 ===")
        print(f"输出文件: {output_file}")
        print(f"结束时间: {datetime.now()}")
        
        # 显示文件大小
        file_size = os.path.getsize(output_file)
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"生成 SQL 过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
