#!/usr/bin/env python3
"""
测试 TbSecondarySchools ORM 模型
验证模型是否正常工作
"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_secondary_schools import TbSecondarySchools


def test_model():
    """测试模型基本功能"""
    print("=" * 60)
    print("测试 TbSecondarySchools ORM 模型")
    print("=" * 60)
    print()
    
    # 测试查询
    print("1. 测试查询功能")
    try:
        total_count = TbSecondarySchools.objects.count()
        print(f"   ✓ 数据库中共有 {total_count} 条中学记录")
    except Exception as e:
        print(f"   ✗ 查询失败: {str(e)}")
        return False
    
    # 测试获取前 5 条记录
    print("\n2. 测试获取前 5 条记录")
    try:
        schools = TbSecondarySchools.objects.all()[:5]
        for school in schools:
            print(f"   - {school.school_name} ({school.district})")
        print(f"   ✓ 成功获取 {len(schools)} 条记录")
    except Exception as e:
        print(f"   ✗ 获取记录失败: {str(e)}")
        return False
    
    # 测试按区域查询
    print("\n3. 测试按区域查询")
    try:
        districts = TbSecondarySchools.objects.values('district').distinct()
        district_count = len(districts)
        print(f"   ✓ 共有 {district_count} 个区域")
        
        # 显示前 5 个区域
        for i, item in enumerate(list(districts)[:5], 1):
            district = item['district'] or '未知'
            count = TbSecondarySchools.objects.filter(district=item['district']).count()
            print(f"   {i}. {district}: {count} 所")
    except Exception as e:
        print(f"   ✗ 按区域查询失败: {str(e)}")
        return False
    
    # 测试按学校类别查询
    print("\n4. 测试按学校类别查询")
    try:
        categories = TbSecondarySchools.objects.values('school_category').annotate(
            count=django.db.models.Count('id')
        ).order_by('-count')
        
        print(f"   ✓ 共有 {len(categories)} 个学校类别")
        for item in categories:
            category = item['school_category'] or '未知'
            print(f"   - {category}: {item['count']} 所")
    except Exception as e:
        print(f"   ✗ 按类别查询失败: {str(e)}")
        return False
    
    # 测试获取详细信息
    print("\n5. 测试获取学校详细信息")
    try:
        if total_count > 0:
            school = TbSecondarySchools.objects.first()
            info = school.get_full_info()
            print(f"   ✓ 成功获取 {school.school_name} 的详细信息")
            print(f"   - ID: {info['id']}")
            print(f"   - 区域: {info['district']}")
            print(f"   - 类别: {info['school_category']}")
            print(f"   - 组别: {info['school_group']}")
            print(f"   - 性别: {info['student_gender']}")
        else:
            print("   ⚠ 数据库中没有记录，跳过测试")
    except Exception as e:
        print(f"   ✗ 获取详细信息失败: {str(e)}")
        return False
    
    # 测试模型方法
    print("\n6. 测试模型方法")
    try:
        if total_count > 0:
            # 查找一个 Band 1 学校
            band1_school = TbSecondarySchools.objects.filter(
                school_group__startswith='1'
            ).first()
            
            if band1_school:
                is_band_one = band1_school.is_band_one()
                print(f"   ✓ {band1_school.school_name} 是否为 Band 1: {is_band_one}")
            
            # 查找一个男女校
            coed_school = TbSecondarySchools.objects.filter(
                student_gender='男女'
            ).first()
            
            if coed_school:
                is_coed = coed_school.is_coed()
                print(f"   ✓ {coed_school.school_name} 是否为男女校: {is_coed}")
        else:
            print("   ⚠ 数据库中没有记录，跳过测试")
    except Exception as e:
        print(f"   ✗ 测试模型方法失败: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！ORM 模型工作正常")
    print("=" * 60)
    return True


if __name__ == '__main__':
    try:
        test_model()
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

