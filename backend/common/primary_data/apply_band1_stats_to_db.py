#!/usr/bin/env python3
"""
将小学升学统计结果应用到数据库
从 primary_schools_band1_stats.json 读取统计数据，更新 tb_primary_schools 表的 promotion_info 字段
"""

import os
import sys
import django
import json
import traceback
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools

# 尝试导入 OpenCC
try:
    from opencc import OpenCC
    cc = OpenCC('t2s')  # 繁体到简体
    USE_OPENCC = True
    print("✅ 使用 OpenCC 进行繁简转换")
except ImportError:
    USE_OPENCC = False
    print("⚠️  未安装 OpenCC，使用内置转换")


# 繁简转换字典（简化版）
TRADITIONAL_TO_SIMPLIFIED = {
    '書': '书', '學': '学', '國': '国', '華': '华', '聖': '圣', '為': '为',
    '醫': '医', '會': '会', '義': '义', '寶': '宝', '協': '协', '慶': '庆',
    '銘': '铭', '賢': '贤', '紀': '纪', '劉': '刘', '張': '张', '陳': '陈',
    '楊': '杨', '黃': '黄', '趙': '赵', '鄭': '郑', '謝': '谢', '鍾': '钟',
    '陸': '陆', '餘': '余', '諸': '诸', '區': '区', '樂': '乐', '藍': '蓝',
    '閻': '阎', '馬': '马', '盧': '卢', '蔣': '蒋', '蘇': '苏', '葉': '叶',
    '緣': '缘', '達': '达', '灣': '湾', '島': '岛', '門': '门', '東': '东',
    '護': '护', '譚': '谭', '鄧': '邓', '範': '范', '潘': '潘', '羅': '罗',
    '梁': '梁', '韋': '韦', '許': '许', '錢': '钱', '湯': '汤', '諾': '诺',
    '瑪': '玛', '麗': '丽', '啟': '启', '導': '导', '濟': '济', '衛': '卫',
    '勵': '励', '壇': '坛', '僑': '侨', '鄉': '乡', '廈': '厦', '廣': '广',
    '漢': '汉', '臺': '台', '師': '师', '資': '资', '館': '馆', '圖': '图',
    '體': '体', '課': '课', '訓': '训', '術': '术', '藝': '艺', '員': '员',
    '園': '园', '獎': '奖', '優': '优', '勝': '胜', '愛': '爱', '總': '总',
    '聯': '联', '辦': '办', '業': '业', '來': '来', '還': '还', '進': '进',
    '運': '运', '關': '关', '開': '开', '閉': '闭', '從': '从', '應': '应',
    '當': '当', '對': '对', '與': '与', '給': '给', '讓': '让', '説': '说',
    '話': '话', '語': '语', '詞': '词', '認': '认', '識': '识', '讀': '读',
    '寫': '写', '聽': '听', '見': '见', '觀': '观', '聞': '闻', '問': '问',
}


def to_simplified(text):
    """
    繁体转简体
    注意：字符 "銶" 不进行转换，保持原样
    """
    if not text:
        return text
    
    # 使用临时标记保护 "銶" 字符，避免被转换
    PLACEHOLDER = "___PROTECT_CHAR_QUIU___"
    
    # 先替换 "銶" 为临时标记
    has_protect_char = "銶" in text
    if has_protect_char:
        text = text.replace("銶", PLACEHOLDER)
    
    if USE_OPENCC:
        try:
            result = cc.convert(text)
        except:
            result = text
    else:
        # 使用内置字典
        result = text
        for trad, simp in TRADITIONAL_TO_SIMPLIFIED.items():
            result = result.replace(trad, simp)
    
    # 恢复 "銶" 字符
    if has_protect_char:
        result = result.replace(PLACEHOLDER, "銶")
    
    return result


def normalize_school_name(name):
    """
    规范化学校名称，便于匹配
    """
    # 移除常见的后缀和前缀
    name = name.strip()
    replacements = {
        '（': '(',
        '）': ')',
        '　': ' ',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def match_school_in_db(school_name, district=None):
    """
    在数据库中匹配小学（支持繁简转换）
    """
    # 规范化名称
    normalized_name = normalize_school_name(school_name)
    
    # 转换为简体（数据库中是简体）
    simplified_name = to_simplified(normalized_name)
    
    # 1. 简体完全匹配
    queryset = TbPrimarySchools.objects.filter(school_name=simplified_name)
    if queryset.exists():
        return queryset.first()
    
    print(f"未找到 {normalized_name} school_name {school_name} simplified_name {simplified_name}")
    
    return None


def apply_stats_to_database(stats_file):
    """
    将统计结果应用到数据库
    """
    print(f"正在读取统计结果: {stats_file}")
    
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    schools_data = stats.get('schools', [])
    districts_data = stats.get('districts', [])
    
    print(f"找到 {len(schools_data)} 所小学的统计数据")
    
    # 建立学校名称到区域的映射
    school_to_district = {}
    for district_data in districts_data:
        district = district_data['district']
        for school in district_data['schools']:
            school_to_district[school['primary_school']] = district
    
    # 统计
    updated_count = 0
    not_found_count = 0
    error_count = 0
    not_found_schools = []
    
    for school_stat in schools_data:
        primary_school = school_stat['primary_school']
        district = school_to_district.get(primary_school)
        
        # 转换为简体
        primary_school_simplified = to_simplified(primary_school)
        
        try:
            # 在数据库中查找学校（支持繁简转换）
            db_school = match_school_in_db(primary_school, district)
            
            # 安全获取最新年份
            yearly_keys = school_stat.get('yearly_stats', {}).keys()
            if yearly_keys:
                latest_year = max(yearly_keys)
            else:
                # 如果没有年份数据，默认使用当前年份
                latest_year = '2025'
                
            if db_school:
                # 确定最新年份 - 这一步已经在上面做了，这里只是为了兼容后续逻辑变量名
                # available_years 逻辑可以简化，因为我们已经有了 latest_year
                
                # 获取该年份的 band1_rate，如果没有则使用总体 rate
                if yearly_keys:
                    latest_band1_rate = school_stat['yearly_stats'][latest_year].get('rate', 0)
                else:
                    latest_band1_rate = school_stat.get('band1_rate', 0)

                # 显式排序
                raw_stats = school_stat.get('yearly_stats', {})
                # 确保按年份字符串降序排序
                sorted_items = sorted(raw_stats.items(), key=lambda x: str(x[0]), reverse=True)
                sorted_stats = dict(sorted_items)
                
                # 更新 promotion_info 字段
                db_school.promotion_info = {
                    'latest_year': latest_year,
                    'band1_rate': latest_band1_rate,
                    'total_graduates': school_stat['total_students'],
                    'school_total_from_excel': school_stat.get('school_total_from_excel'),  # 新增：Excel读取的总人数
                    'band1_graduates': school_stat['band1_students'],
                    'band_distribution': school_stat['band_distribution'],
                    'top_secondary_schools': [
                        {'school': k, 'count': v} 
                        for k, v in list(school_stat['secondary_schools'].items())
                    ],
                    # 为了兼容前端 promotionSummary，添加 schools 字段
                    # 这样即使没有年份数据，前端也能显示总体升学中学列表
                    'schools': school_stat['secondary_schools'],
                    'yearly_stats': sorted_stats,
                    # 注意：yearly_stats下的schools格式为 {学校名: {'count': 人数, 'band': banding}}
                    # 旧格式 {学校名: 人数} 已废弃，但代码会兼容处理
                    'data_source': 'excel_import',
                    'last_updated': '2025-10-19'
                }
                db_school.save(update_fields=['promotion_info', 'updated_at'])
                
                updated_count += 1
                match_info = f"(繁:{primary_school}→简:{primary_school_simplified})" if primary_school != primary_school_simplified else ""
                print(f"✅ 更新: {db_school.school_name:35s} - Band 1: {latest_band1_rate}% {match_info}, 最新年份: {latest_year}")
            else:
                not_found_count += 1
                not_found_schools.append(primary_school)
                print(f"⚠️  未找到: {primary_school:35s} (简体:{primary_school_simplified[:20]}) (区域: {district})")
        
        except Exception as e:
            error_count += 1
            print(f"❌ 错误: {primary_school:35s} - {traceback.format_exc()}")
    
    # 打印总结
    print("\n" + "=" * 80)
    print("应用结果")
    print("=" * 80)
    print(f"成功更新: {updated_count} 所")
    print(f"未找到: {not_found_count} 所")
    print(f"错误: {error_count} 所")
    
    if not_found_schools:
        print(f"\n未找到的小学列表:")
        for school in not_found_schools[:20]:
            print(f"  - {school}")
        if len(not_found_schools) > 20:
            print(f"  ... 还有 {len(not_found_schools) - 20} 所")
    
    # 保存未匹配的学校
    if not_found_schools:
        unmatched_file = Path(stats_file).parent / 'unmatched_schools.txt'
        with open(unmatched_file, 'w', encoding='utf-8') as f:
            f.write("未在数据库中找到的小学列表\n")
            f.write("=" * 80 + "\n\n")
            for school in not_found_schools:
                district = school_to_district.get(school, '未知')
                f.write(f"{school} ({district})\n")
        print(f"\n未匹配学校列表已保存到: {unmatched_file}")


def verify_update():
    """
    验证更新结果
    """
    print("\n" + "=" * 80)
    print("验证更新结果")
    print("=" * 80)
    
    # 统计有 promotion_info 的学校
    total_schools = TbPrimarySchools.objects.count()
    with_promotion = TbPrimarySchools.objects.exclude(promotion_info__isnull=True).count()
    
    print(f"\n数据库统计:")
    print(f"  总小学数: {total_schools}")
    print(f"  有升学数据: {with_promotion}")
    print(f"  覆盖率: {(with_promotion/total_schools*100):.2f}%")
    
    # 显示几个示例
    print(f"\n示例数据:")
    schools = TbPrimarySchools.objects.exclude(promotion_info__isnull=True)[:5]
    for school in schools:
        info = school.promotion_info
        print(f"  {school.school_name:30s} - Band 1: {info.get('band1_rate', 0)}%")


def main():
    """
    主函数
    """
    print("=" * 80)
    print("将小学升学统计结果应用到数据库")
    print("=" * 80)
    
    # 统计文件路径
    stats_file = Path(__file__).parent / 'primary_schools_band1_stats.json'
    
    if not stats_file.exists():
        print(f"\n❌ 错误：找不到统计文件: {stats_file}")
        print("请先运行 calculate_primary_band1_rate.py 生成统计数据")
        return
    
    # 应用统计数据到数据库
    apply_stats_to_database(stats_file)
    
    # 验证更新结果
    verify_update()
    
    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()

