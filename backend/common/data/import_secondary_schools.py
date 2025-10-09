#!/usr/bin/env python3
"""
香港中学数据导入脚本
从 Excel 文件读取中学数据并写入 tb_secondary_schools 表
"""

import os
import sys
import pandas as pd
import django
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_secondary_schools import TbSecondarySchools


def clean_value(value):
    """清理数据值"""
    if pd.isna(value) or value == 'nan' or value == '-':
        return None
    return str(value).strip()


def parse_phone(phone_value):
    """解析电话号码"""
    if pd.isna(phone_value):
        return None
    # 转换为字符串并去除小数点
    phone_str = str(int(phone_value)) if isinstance(phone_value, (int, float)) else str(phone_value)
    return phone_str.strip()


def process_excel_data(excel_file_path):
    """处理 Excel 数据"""
    print(f"正在读取 Excel 文件: {excel_file_path}")
    
    try:
        df = pd.read_excel(excel_file_path)
        print(f"成功读取 {len(df)} 条记录")
        return df
    except Exception as e:
        print(f"读取 Excel 文件失败: {str(e)}")
        sys.exit(1)


def import_secondary_schools_from_excel(excel_file_path):
    """从 Excel 导入中学数据"""
    print(f"正在处理中学数据文件: {excel_file_path}")
    
    # 读取 Excel 数据
    df = process_excel_data(excel_file_path)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            # 检查学校是否已存在
            school_name = clean_value(row['学校名称'])
            if not school_name:
                error_count += 1
                print(f"第 {index + 1} 行: 学校名称为空，跳过")
                continue
            
            existing_school = TbSecondarySchools.objects.filter(school_name=school_name).first()
            
            # 准备数据（不包括 school_curriculum）
            school_obj_data = {
                'school_name': school_name,
                'district': clean_value(row['区域']),
                'school_net': clean_value(row['对应校网']),
                'religion': clean_value(row['宗教']) if clean_value(row['宗教']) != "不适用" else "",
                'student_gender': clean_value(row['学生性别']),
                'tuition': clean_value(row['学费（相同的概括，不同的独立罗列）']),
                'school_category': clean_value(row['学校类别']),
                'school_group': f"Band {clean_value(row['学校组别'])}" if clean_value(row['学校组别']) else None,
                'transfer_open_time': clean_value(row['插班开放时间']),
                'total_classes': int(row['全校总班数']) if pd.notna(row['全校总班数']) else None,
                'admission_info': clean_value(row['中一入学']),
                'address': clean_value(row['学校地址']),
                'phone': parse_phone(row['电话']),
                'email': clean_value(row['电邮']),
                'website': clean_value(row['网站']),
            }
            
            if existing_school:
                # 更新现有记录
                for key, value in school_obj_data.items():
                    setattr(existing_school, key, value)
                existing_school.save()
                updated_count += 1
                print(f"更新中学: {school_name}")
            else:
                # 创建新记录
                TbSecondarySchools.objects.create(**school_obj_data)
                created_count += 1
                print(f"创建中学: {school_name}")
            
            # 每处理 10 条输出进度
            if (created_count + updated_count) % 10 == 0:
                print(f"已处理 {created_count + updated_count} 条记录...")
                
        except Exception as e:
            error_count += 1
            school_name = row.get('学校名称', 'Unknown')
            print(f"处理中学数据时出错: {school_name} - {str(e)}")
    
    return created_count, updated_count, error_count


def main():
    """主函数"""
    print("=" * 60)
    print("香港中学数据导入工具")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Excel 文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(current_dir, '香港各中学信息.xlsx')
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误: 找不到 Excel 文件 {excel_file}")
        sys.exit(1)
    
    try:
        # 导入数据
        print("\n开始导入数据...")
        created_count, updated_count, error_count = import_secondary_schools_from_excel(excel_file)
        
        # 输出统计信息
        print("\n" + "=" * 60)
        print("导入完成")
        print("=" * 60)
        print(f"成功创建: {created_count} 条记录")
        print(f"成功更新: {updated_count} 条记录")
        print(f"失败记录: {error_count} 条")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示数据库中的总记录数
        total_count = TbSecondarySchools.objects.count()
        print(f"\n数据库中共有 {total_count} 条中学记录")
        
        # 显示按区域统计
        print("\n区域分布:")
        districts = TbSecondarySchools.objects.values('district').annotate(
            count=django.db.models.Count('id')
        ).order_by('-count')[:10]
        
        for item in districts:
            district = item['district'] or '未知'
            print(f"  {district}: {item['count']} 所")
        
        # 显示按类别统计
        print("\n学校类别分布:")
        categories = TbSecondarySchools.objects.values('school_category').annotate(
            count=django.db.models.Count('id')
        ).order_by('-count')
        
        for item in categories:
            category = item['school_category'] or '未知'
            print(f"  {category}: {item['count']} 所")
        
    except Exception as e:
        print(f"\n导入过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
