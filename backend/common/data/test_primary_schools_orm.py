#!/usr/bin/env python3
"""
测试小学 ORM 模型
"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools


def test_create_school():
    """测试创建小学"""
    print("\n=== 测试创建小学 ===")
    
    school_data = {
        'school_name': '测试小学',
        'district': '中西区',
        'school_net': '11',
        'address': '香港中环测试街1号',
        'phone': '12345678',
        'email': 'test@test.edu.hk',
        'website': 'http://test.edu.hk',
        'school_category': '资助',
        'student_gender': '男女',
        'religion': '基督教',
        'teaching_language': '中文',
        'tuition': '-',
        'school_basic_info': {
            'school_sponsor': '测试办学团体',
            'establish_year': '2000',
            'school_motto': '勤学善思',
            'area_size': '5000',
            'school_category_2': '全日',
            'school_bus': '有',
            'num_classrooms': 24
        },
        'secondary_info': {
            'through_train': '-',
            'direct': '测试中学',
            'associated': '-'
        },
        'total_classes_info': {
            'current_year_p1_classes': 4,
            'current_year_p2_classes': 4,
            'current_year_p3_classes': 4,
            'current_year_p4_classes': 4,
            'current_year_p5_classes': 4,
            'current_year_p6_classes': 4,
            'current_year_total_classes': 24
        },
        'class_teaching_info': {
            'class_teaching_mode': '小班教学',
            'class_arrangement': '平均分班'
        },
        'assessment_info': {
            'p1_tests_per_year': '0',
            'p1_exams_per_year': '2',
            'p2_to_p6_tests_per_year': '2',
            'p2_to_p6_exams_per_year': '2'
        }
    }
    
    try:
        # 先删除可能存在的测试数据
        TbPrimarySchools.objects.filter(school_name='测试小学').delete()
        
        # 创建新学校
        school = TbPrimarySchools.objects.create(**school_data)
        print(f"✅ 成功创建学校: {school.school_name} (ID: {school.id})")
        
        return school
    except Exception as e:
        print(f"❌ 创建学校失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_query_schools():
    """测试查询小学"""
    print("\n=== 测试查询小学 ===")
    
    try:
        # 查询所有小学
        total = TbPrimarySchools.objects.count()
        print(f"总共有 {total} 所小学")
        
        # 按区域查询
        districts = TbPrimarySchools.objects.values('district').distinct()
        print(f"\n涵盖 {len(districts)} 个区域:")
        for d in list(districts)[:5]:
            count = TbPrimarySchools.objects.filter(district=d['district']).count()
            print(f"  - {d['district']}: {count} 所")
        
        # 按学校类别查询
        categories = TbPrimarySchools.objects.values('school_category').distinct()
        print(f"\n学校类别分布:")
        for c in categories:
            if c['school_category']:
                count = TbPrimarySchools.objects.filter(school_category=c['school_category']).count()
                print(f"  - {c['school_category']}: {count} 所")
        
        # 查询有直属中学的小学
        with_direct_secondary = TbPrimarySchools.objects.exclude(
            secondary_info__isnull=True
        ).filter(
            secondary_info__has_key='direct'
        ).count()
        print(f"\n有直属中学的小学: {with_direct_secondary} 所")
        
        print("✅ 查询测试通过")
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_school_methods():
    """测试学校方法"""
    print("\n=== 测试学校方法 ===")
    
    try:
        # 获取第一所学校
        school = TbPrimarySchools.objects.first()
        
        if not school:
            print("⚠️  数据库中没有学校数据")
            return
        
        print(f"\n测试学校: {school.school_name}")
        
        # 测试 __str__ 方法
        print(f"  __str__: {school}")
        
        # 测试获取总班数
        total_classes = school.get_total_classes()
        print(f"  总班数: {total_classes}")
        
        # 测试获取关联中学
        linked_schools = school.get_linked_secondary_schools()
        print(f"  关联中学: {len(linked_schools)} 所")
        if linked_schools:
            for s in linked_schools[:3]:
                print(f"    - {s['name']} ({s['type']})")
        
        # 测试是否为全日制
        is_full_day = school.is_full_day()
        print(f"  是否全日制: {is_full_day}")
        
        # 测试是否为男女校
        is_coed = school.is_coed()
        print(f"  是否男女校: {is_coed}")
        
        # 测试获取完整信息
        full_info = school.get_full_info()
        print(f"  完整信息字段数: {len(full_info)}")
        
        print("✅ 方法测试通过")
        
    except Exception as e:
        print(f"❌ 方法测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_update_school():
    """测试更新小学"""
    print("\n=== 测试更新小学 ===")
    
    try:
        # 查找测试学校
        school = TbPrimarySchools.objects.filter(school_name='测试小学').first()
        
        if not school:
            print("⚠️  找不到测试学校")
            return
        
        # 更新学校信息
        school.phone = '87654321'
        school.school_basic_info['num_classrooms'] = 30
        school.save()
        
        # 重新查询验证
        updated_school = TbPrimarySchools.objects.get(id=school.id)
        assert updated_school.phone == '87654321'
        assert updated_school.school_basic_info['num_classrooms'] == 30
        
        print("✅ 更新学校成功")
        
    except Exception as e:
        print(f"❌ 更新学校失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_filter_schools():
    """测试过滤查询"""
    print("\n=== 测试过滤查询 ===")
    
    try:
        # 按关键词搜索
        keyword = "圣"
        schools = TbPrimarySchools.objects.filter(school_name__icontains=keyword)[:5]
        print(f"\n学校名称包含 '{keyword}' 的学校 (前5所):")
        for school in schools:
            print(f"  - {school.school_name} ({school.district})")
        
        # 按多个条件过滤
        schools = TbPrimarySchools.objects.filter(
            district='中西区',
            student_gender='男女'
        )
        print(f"\n中西区男女校: {schools.count()} 所")
        
        # 按 JSON 字段过滤
        schools = TbPrimarySchools.objects.filter(
            school_basic_info__has_key='school_bus'
        )
        print(f"\n有校车信息的学校: {schools.count()} 所")
        
        print("✅ 过滤查询测试通过")
        
    except Exception as e:
        print(f"❌ 过滤查询失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_delete_school():
    """测试删除小学"""
    print("\n=== 测试删除小学 ===")
    
    try:
        # 删除测试学校
        deleted_count = TbPrimarySchools.objects.filter(school_name='测试小学').delete()[0]
        print(f"✅ 成功删除 {deleted_count} 所测试学校")
        
    except Exception as e:
        print(f"❌ 删除学校失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("=" * 60)
    print("小学 ORM 模型测试")
    print("=" * 60)
    
    # 运行测试
    test_create_school()
    test_query_schools()
    test_school_methods()
    test_update_school()
    test_filter_schools()
    test_delete_school()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

