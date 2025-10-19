#!/usr/bin/env python3
"""
香港小学数据导入脚本
从 Excel 文件读取小学数据并写入 tb_primary_schools 表
"""

import os
import sys
import pandas as pd
import django
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools


def clean_value(value):
    """清理数据值"""
    if pd.isna(value) or value == 'nan' or value == '-':
        return None
    value_str = str(value).strip()
    return value_str if value_str else None


def parse_phone(phone_value):
    """解析电话号码"""
    if pd.isna(phone_value):
        return None
    # 转换为字符串并去除小数点
    phone_str = str(int(phone_value)) if isinstance(phone_value, (int, float)) else str(phone_value)
    return phone_str.strip()


def parse_time(time_value):
    """解析时间字符串"""
    if pd.isna(time_value):
        return None
    try:
        if isinstance(time_value, str):
            # 假设格式为 HH:MM:SS
            return time_value
        # 如果是 datetime 对象，提取时间部分
        return time_value.strftime('%H:%M:%S')
    except:
        return None


def build_school_basic_info(row):
    """构建学校基础信息 JSON"""
    info = {}
    
    # 办学团体
    if clean_value(row.get('办学团体')):
        info['school_sponsor'] = clean_value(row['办学团体'])
    
    # 创校年份
    if clean_value(row.get('创校年份')):
        info['establish_year'] = clean_value(row['创校年份'])
    
    # 校训
    if clean_value(row.get('校训')):
        info['school_motto'] = clean_value(row['校训'])
    
    # 学校占地面积
    if clean_value(row.get('学校占地面积')):
        info['area_size'] = clean_value(row['学校占地面积'])
    
    # 学校类别2（全日/半日）
    if clean_value(row.get('学校类别2')):
        info['school_category_extra'] = clean_value(row['学校类别2'])
    
    
    return info if info else None


def build_secondary_info(row):
    """构建中学联系信息 JSON"""
    info = {}
    
    if clean_value(row.get('一条龙中学')):
        info['through_train'] = clean_value(row['一条龙中学'])
    
    if clean_value(row.get('直属中学')):
        info['direct'] = clean_value(row['直属中学'])
    
    if clean_value(row.get('联系中学')):
        info['associated'] = clean_value(row['联系中学'])
    
    return info if info else None


def build_total_classes_info(row):
    """构建总班数信息 JSON"""
    info = {}
    
    # 上学年班数
    for i in range(1, 7):
        key = f'上学年小{["一", "二", "三", "四", "五", "六"][i-1]}班数'
        if pd.notna(row.get(key)):
            info[f'last_year_p{i}_classes'] = int(row[key])
    
    if pd.notna(row.get('上学年总班数')):
        info['last_year_total_classes'] = int(row['上学年总班数'])
    
    # 本学年班数
    for i in range(1, 7):
        key = f'本学年小{["一", "二", "三", "四", "五", "六"][i-1]}班数'
        if pd.notna(row.get(key)):
            info[f'current_year_p{i}_classes'] = int(row[key])
    
    if pd.notna(row.get('本学年总班数')):
        info['current_year_total_classes'] = int(row['本学年总班数'])
    
    # 小六学生人数估算
    if clean_value(row.get('小六学生人数（估算）2025届毕业')):
        info['p6_graduates_estimate'] = clean_value(row['小六学生人数（估算）2025届毕业'])
    
    return info if info else None


def build_class_teaching_info(row):
    """构建班级教学信息 JSON"""
    info = {}
    
    if clean_value(row.get('班级教学模式')):
        info['class_teaching_mode'] = clean_value(row['班级教学模式'])
    
    if clean_value(row.get('班级结构备注')):
        info['class_structure_note'] = clean_value(row['班级结构备注'])
    
    if clean_value(row.get('分班安排')):
        info['class_arrangement'] = clean_value(row['分班安排'])
    
    return info if info else None


def build_assessment_info(row):
    """构建学习评估信息 JSON"""
    info = {}
    
    if clean_value(row.get('全年全科测验次数_一年级')):
        info['p1_tests_per_year'] = clean_value(row['全年全科测验次数_一年级'])
    if clean_value(row.get('全年全科考试次数_一年级')):
        info['p1_exams_per_year'] = clean_value(row['全年全科考试次数_一年级'])
    if clean_value(row.get('小一上学期以多元化的进展性评估代替测验及考试')):
        info['p1_alternative_assessment'] = clean_value(row['小一上学期以多元化的进展性评估代替测验及考试'])
    if clean_value(row.get('全年全科测验次数_二至六年级')):
        info['p2_to_p6_tests_per_year'] = clean_value(row['全年全科测验次数_二至六年级'])
    if clean_value(row.get('全年全科考试次数_二至六年级')):
        info['p2_to_p6_exams_per_year'] = clean_value(row['全年全科考试次数_二至六年级'])
    if clean_value(row.get('多元学习评估')):
        info['diverse_assessment'] = clean_value(row['多元学习评估'])
    
    return info if info else None


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


def import_primary_schools_from_excel(excel_file_path):
    """从 Excel 导入小学数据"""
    print(f"正在处理小学数据文件: {excel_file_path}")
    
    # 读取 Excel 数据
    df = process_excel_data(excel_file_path)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        try:
            # 检查学校是否已存在
            school_name = clean_value(row.get('学校名称'))
            if not school_name:
                error_count += 1
                print(f"第 {index + 1} 行: 学校名称为空，跳过")
                continue
            
            existing_school = TbPrimarySchools.objects.filter(school_name=school_name).first()
            
            # 准备数据
            school_obj_data = {
                'school_name': school_name,
                'district': clean_value(row.get('区域')),
                'school_net': clean_value(row.get('小一学校网')),
                'address': clean_value(row.get('学校地址')),
                'phone': parse_phone(row.get('学校电话')),
                'fax': parse_phone(row.get('学校传真')),
                'email': clean_value(row.get('学校电邮')),
                'website': clean_value(row.get('学校网址')),
                'school_category': clean_value(row.get('学校类别1')),
                'student_gender': clean_value(row.get('学生性别')),
                'religion': clean_value(row.get('宗教')) if clean_value(row.get('宗教')) != "不适用" else "",
                'teaching_language': clean_value(row.get('教学语言')),
                'tuition': clean_value(row.get('学费')),
                'school_basic_info': build_school_basic_info(row),
                'secondary_info': build_secondary_info(row),
                'total_classes_info': build_total_classes_info(row),
                'class_teaching_info': build_class_teaching_info(row),
                'assessment_info': build_assessment_info(row),
            }
            
            if existing_school:
                # 更新现有记录
                for key, value in school_obj_data.items():
                    setattr(existing_school, key, value)
                existing_school.save()
                updated_count += 1
                print(f"更新小学: {school_name}")
            else:
                # 创建新记录
                TbPrimarySchools.objects.create(**school_obj_data)
                created_count += 1
                print(f"创建小学: {school_name}")
        
        except Exception as e:
            error_count += 1
            print(f"第 {index + 1} 行处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n导入完成:")
    print(f"  新建: {created_count} 条")
    print(f"  更新: {updated_count} 条")
    print(f"  失败: {error_count} 条")


def main():
    """主函数"""
    # Excel 文件路径
    excel_file_path = os.path.join(
        os.path.dirname(__file__),
        '2025年小学概览-估算小六学生人数.xlsx'
    )
    
    if not os.path.exists(excel_file_path):
        print(f"错误: Excel 文件不存在: {excel_file_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("香港小学数据导入工具")
    print("=" * 60)
    
    # 导入小学数据
    import_primary_schools_from_excel(excel_file_path)
    
    print("\n所有数据导入完成！")


if __name__ == '__main__':
    main()

