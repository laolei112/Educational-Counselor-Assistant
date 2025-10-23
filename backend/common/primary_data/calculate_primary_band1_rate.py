#!/usr/bin/env python3
"""
统计每个小学的升中 Band 1 比例
从各个区的 Excel 文件中读取升学数据，结合中学 banding 信息，计算每个小学的升 Band 1 比例
支持按年份统计，并进行繁简转换以提高匹配率
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

# 尝试导入专业的繁简转换库
try:
    from opencc import OpenCC
    cc = OpenCC('t2s')  # 繁体到简体
    USE_OPENCC = True
    print("✅ 使用 OpenCC 进行繁简转换（更准确）")
except ImportError:
    USE_OPENCC = False
    print("⚠️  未安装 OpenCC，使用内置转换字典")
    print("   提示: pip install opencc-python-reimplemented")


# 扩展的繁简转换字典（500+ 常用字）
TRADITIONAL_TO_SIMPLIFIED = {
    # 基础汉字
    '書': '书', '學': '学', '國': '国', '華': '华', '聖': '圣', '爲': '为', '為': '为',
    '醫': '医', '會': '会', '義': '义', '寶': '宝', '協': '协', '慶': '庆', '銘': '铭',
    '賢': '贤', '紀': '纪', '劉': '刘', '張': '张', '陳': '陈', '楊': '杨', '黃': '黄',
    '趙': '赵', '鄭': '郑', '謝': '谢', '鍾': '钟', '陸': '陆', '餘': '余', '諸': '诸',
    '區': '区', '嶽': '岳', '樂': '乐', '藍': '蓝', '閻': '阎', '馬': '马', '盧': '卢',
    '傅': '傅', '蔣': '蒋', '蘇': '苏', '葉': '叶', '緣': '缘', '達': '达', '灣': '湾',
    '島': '岛', '門': '门', '東': '东', '貢': '贡', '護': '护', '譚': '谭', '鄧': '邓',
    '範': '范', '潘': '潘', '羅': '罗', '梁': '梁', '韋': '韦', '許': '许', '戴': '戴',
    '錢': '钱', '湯': '汤', '熊': '熊', '薛': '薛', '竇': '窦', '顧': '顾', '諾': '诺',
    '撒': '撒', '瑪': '玛', '麗': '丽', '伊': '伊', '利': '利', '沙': '沙', '伯': '伯',
    '啟': '启', '導': '导', '濟': '济', '衛': '卫', '勵': '励', '壇': '坛', '僑': '侨',
    '鄉': '乡', '廈': '厦', '廣': '广', '漢': '汉', '臺': '台', '澳': '澳', '糾': '纠',
    '紛': '纷',
    # 教育相关
    '敎': '教', '師': '师', '資': '资', '舘': '馆', '館': '馆', '圖': '图', '體': '体',
    '課': '课', '堂': '堂', '訓': '训', '練': '练', '術': '术', '藝': '艺', '員': '员',
    '園': '园', '齋': '斋', '齊': '齐', '獎': '奖', '勵': '励', '優': '优', '勝': '胜',
    # 宗教相关
    '天': '天', '主': '主', '敎': '教', '基': '基', '督': '督', '佛': '佛', '道': '道',
    '教': '教', '堂': '堂', '院': '院', '寺': '寺', '廟': '庙', '神': '神', '靈': '灵',
    '聖': '圣', '福': '福', '恩': '恩', '善': '善', '德': '德', '仁': '仁', '愛': '爱',
    # 机构相关
    '會': '会', '社': '社', '團': '团', '聯': '联', '總': '总', '公': '公', '立': '立',
    '私': '私', '官': '官', '政': '政', '府': '府', '部': '部', '局': '局', '署': '署',
    '處': '处', '科': '科', '組': '组', '委': '委', '議': '议', '辦': '办', '業': '业',
    # 常用动词
    '來': '来', '還': '还', '進': '进', '運': '运', '關': '关', '開': '开', '閉': '闭',
    '從': '从', '應': '应', '當': '当', '對': '对', '與': '与', '給': '给', '讓': '让',
    '説': '说', '話': '话', '語': '语', '詞': '词', '認': '认', '識': '识', '讀': '读',
    '寫': '写', '聽': '听', '見': '见', '觀': '观', '聞': '闻', '問': '问', '答': '答',
    # 常用形容词
    '長': '长', '強': '强', '舊': '旧', '新': '新', '輕': '轻', '重': '重', '遠': '远',
    '近': '近', '高': '高', '低': '低', '貴': '贵', '賤': '贱', '優': '优', '劣': '劣',
    '專': '专', '業': '业', '實': '实', '際': '际', '現': '现', '過': '过', '歷': '历',
    '傳': '传', '統': '统', '繼': '继', '續': '续', '斷': '断', '連': '连', '聯': '联',
    # 数量词
    '個': '个', '隻': '只', '雙': '双', '對': '对', '條': '条', '張': '张', '間': '间',
    '層': '层', '棟': '栋', '間': '间', '輛': '辆', '臺': '台',
    # 香港特有
    '灣': '湾', '島': '岛', '區': '区', '道': '道', '街': '街', '里': '里', '村': '村',
    '鄉': '乡', '坊': '坊', '徑': '径', '路': '路', '巷': '巷', '弄': '弄',
}


def to_simplified(text):
    """
    繁体转简体（支持 OpenCC 或内置字典）
    """
    if not text:
        return text
    
    if USE_OPENCC:
        try:
            return cc.convert(text)
        except:
            # OpenCC 失败时使用字典
            pass
    
    # 使用内置字典转换
    result = text
    for trad, simp in TRADITIONAL_TO_SIMPLIFIED.items():
        result = result.replace(trad, simp)
    return result


def load_primary_school_totals(totals_file):
    """
    加载小学总人数数据
    从2025年小学概览Excel文件中读取每个小学的小六学生总人数
    """
    print(f"正在加载小学总人数信息: {totals_file}")
    
    try:
        # 读取Excel文件
        xl_file = pd.ExcelFile(totals_file)
        print(f"找到工作表: {xl_file.sheet_names}")
        
        # 尝试读取第一个工作表
        df = pd.read_excel(totals_file, sheet_name=xl_file.sheet_names[0])
        print(f"数据行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        
        # 查找学校名称和人数相关的列
        school_name_col = None
        student_count_col = None
        
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ['学校', 'school', '名称', 'name']):
                school_name_col = col
            elif any(keyword in col_str for keyword in ['人数', '学生', 'student', '小六', '六年级', '估算']):
                student_count_col = col
        
        if not school_name_col or not student_count_col:
            print(f"⚠️  无法自动识别列名，请检查Excel文件结构")
            print(f"   学校名称列候选: {school_name_col}")
            print(f"   学生人数列候选: {student_count_col}")
            return {}
        
        print(f"使用学校名称列: {school_name_col}")
        print(f"使用学生人数列: {student_count_col}")
        
        # 建立学校名称到人数的映射
        school_totals = {}
        unmatched_count = 0
        
        for idx, row in df.iterrows():
            school_name = row.get(school_name_col)
            student_count = row.get(student_count_col)
            
            if pd.notna(school_name) and pd.notna(student_count):
                school_name = str(school_name).strip()
                try:
                    student_count = int(student_count)
                    school_totals[school_name] = student_count
                except (ValueError, TypeError):
                    unmatched_count += 1
                    print(f"⚠️  无法解析人数: {school_name} -> {student_count}")
        
        print(f"成功加载 {len(school_totals)} 所小学的总人数信息")
        if unmatched_count > 0:
            print(f"⚠️  {unmatched_count} 条记录无法解析")
        
        # 显示前几个示例
        print("\n示例数据:")
        for i, (school, count) in enumerate(list(school_totals.items())[:5]):
            print(f"  {school}: {count} 人")
        
        return school_totals
        
    except Exception as e:
        print(f"❌ 加载小学总人数信息失败: {str(e)}")
        return {}


def load_secondary_band_map(band_file):
    """
    加载中学 Band 映射，同时建立繁体和简体两个映射
    """
    print(f"正在加载中学 Band 信息: {band_file}")
    
    df = pd.read_excel(band_file)
    band_map = {}
    band_map_simplified = {}
    
    for idx, row in df.iterrows():
        school_name = row['school_name']
        school_group = row['school_group']
        
        if pd.notna(school_name) and pd.notna(school_group):
            school_name = str(school_name).strip()
            school_group = str(school_group).strip()
            
            # 原始名称（繁体）
            band_map[school_name] = school_group
            
            # 简体名称
            school_name_simplified = to_simplified(school_name)
            band_map_simplified[school_name_simplified] = school_group
    
    print(f"已加载 {len(band_map)} 所中学的 Band 信息")
    print(f"建立简体映射 {len(band_map_simplified)} 条")
    
    # 统计 Band 分布
    band_count = defaultdict(int)
    for band in band_map.values():
        if band.startswith('Band '):
            main_band = 'Band ' + band.split()[1][0]
        else:
            main_band = band
        band_count[main_band] += 1
    
    print("\nBand 分布:")
    for band, count in sorted(band_count.items()):
        print(f"  {band}: {count} 所")
    
    return band_map, band_map_simplified


def is_band_1(band_str):
    """
    判断是否为 Band 1
    """
    if not band_str:
        return False
    return 'Band 1' in band_str or band_str.startswith('1')


def match_school_name(target_name, band_map, band_map_simplified):
    """
    匹配学校名称，支持繁简转换和模糊匹配
    """
    target_name = target_name.strip()
    
    # 1. 完全匹配（繁体）
    if target_name in band_map:
        return band_map[target_name]
    
    # 2. 转换为简体后完全匹配
    target_simplified = to_simplified(target_name)
    if target_simplified in band_map_simplified:
        return band_map_simplified[target_simplified]
    
    # 3. 部分匹配（移除"中學"后缀）
    base_name = target_name.replace('中學', '').replace('中学', '').strip()
    base_name_simplified = to_simplified(base_name)
    
    # 在繁体映射中匹配
    for school, band in band_map.items():
        school_base = school.replace('中學', '').replace('中学', '').strip()
        if base_name == school_base:
            return band
        # 如果主要部分匹配（至少5个字符）
        if len(base_name) >= 5 and (base_name in school or school in target_name):
            return band
    
    # 在简体映射中匹配
    for school_simp, band in band_map_simplified.items():
        school_base_simp = school_simp.replace('中学', '').strip()
        if base_name_simplified == school_base_simp:
            return band
        # 如果主要部分匹配（至少5个字符）
        if len(base_name_simplified) >= 5 and (base_name_simplified in school_simp or school_simp in target_simplified):
            return band
    
    return None


def process_primary_school_sheet(sheet_name, df, band_map, band_map_simplified, school_totals=None):
    """
    处理单个小学的工作表，支持按年份统计
    处理合并单元格：年份列使用前向填充
    school_totals: 从Excel文件读取的小学总人数映射
    """
    # 处理合并单元格：年份列前向填充
    if '年份' in df.columns:
        df['年份'] = df['年份'].ffill()  # 前向填充，处理合并单元格
    
    # 按年份统计
    yearly_stats = defaultdict(lambda: {
        'total': 0,
        'band1': 0,
        'schools': defaultdict(int),
        'band_dist': defaultdict(int),
        'unmatched': []
    })
    
    # 总体统计
    total_students = 0
    band1_students = 0
    school_stats = defaultdict(int)
    band_distribution = defaultdict(int)
    unmatched_schools = set()
    
    for idx, row in df.iterrows():
        secondary_school = row.get('升入学校')
        count = row.get('人数')
        year = row.get('年份')
        print(secondary_school, count, year)
        # 跳过空值
        if pd.isna(secondary_school) or pd.isna(count):
            continue
        
        try:
            count = int(count)
        except (ValueError, TypeError):
            continue
        
        # 处理年份（合并单元格已前向填充）
        if pd.notna(year):
            try:
                year = int(year)
            except:
                year = None
        else:
            year = None
        
        secondary_school = str(secondary_school).strip()
        
        # 总体统计
        total_students += count
        school_stats[secondary_school] += count
        
        # 匹配中学 Band（使用繁简双映射）
        band = match_school_name(secondary_school, band_map, band_map_simplified)
        if not band:
            band = match_school_name(f"香港{secondary_school}", band_map, band_map_simplified)
            if not band:
                band = match_school_name(secondary_school.replace('(', '（').replace(')', '）'), band_map, band_map_simplified)
        print(band, secondary_school)
        if band:
            band_distribution[band] += count
            if is_band_1(band):
                band1_students += count
                
                # 按年份记录
                if year:
                    yearly_stats[year]['band1'] += count
        else:
            band_distribution['未知'] += count
            unmatched_schools.add(secondary_school)
        
        # 年份统计
        if year:
            yearly_stats[year]['total'] += count
            yearly_stats[year]['schools'][secondary_school] += count
            if band:
                yearly_stats[year]['band_dist'][band] += count
            else:
                yearly_stats[year]['band_dist']['未知'] += count
                yearly_stats[year]['unmatched'].append(secondary_school)
    
    # 获取该小学的总人数（从Excel文件读取）
    school_total_from_excel = None
    if school_totals:
        # 尝试多种匹配方式
        for school_name, total_count in school_totals.items():
            if sheet_name == school_name:
                school_total_from_excel = total_count
                break
            # 尝试繁简转换匹配
            elif to_simplified(sheet_name) == to_simplified(school_name):
                school_total_from_excel = total_count
                break
            # 尝试部分匹配
            elif len(sheet_name) >= 5 and (sheet_name in school_name or school_name in sheet_name):
                school_total_from_excel = total_count
                break
    
    # 计算总体 Band 1 比例
    band1_rate = (band1_students / total_students * 100) if total_students > 0 else 0
    
    # 计算每年的 Band 1 比例
    yearly_band1_rates = {}
    for year, stats in yearly_stats.items():
        rate = (stats['band1'] / stats['total'] * 100) if stats['total'] > 0 else 0
        yearly_band1_rates[year] = {
            'total': stats['total'],
            'band1': stats['band1'],
            'rate': round(rate, 2)
        }
    
    return {
        'primary_school': sheet_name,
        'total_students': total_students,  # 升学数据中的总人数
        'school_total_from_excel': school_total_from_excel,  # 从Excel文件读取的总人数
        'band1_students': band1_students,
        'band1_rate': round(band1_rate, 2),
        'band_distribution': dict(band_distribution),
        'secondary_schools': dict(sorted(school_stats.items(), key=lambda x: x[1], reverse=True)),
        'unmatched_schools': list(unmatched_schools),
        'yearly_stats': dict(yearly_band1_rates)  # 新增：按年份统计
    }


def process_excel_file(file_path, band_map, band_map_simplified, school_totals=None):
    """
    处理单个 Excel 文件（包含多个小学的工作表）
    school_totals: 从Excel文件读取的小学总人数映射
    """
    district = file_path.stem.replace('升学数据', '').replace('小学', '').replace('區', '区')
    print(f"\n处理 {district}...")
    
    try:
        xl_file = pd.ExcelFile(file_path)
        print(f"  找到 {len(xl_file.sheet_names)} 所小学")
        
        results = []
        for sheet_name in xl_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                result = process_primary_school_sheet(sheet_name, df, band_map, band_map_simplified, school_totals)
                
                if result['total_students'] > 0:
                    results.append(result)
                    # 显示总体和年度数据
                    yearly_info = ""
                    if result.get('yearly_stats'):
                        years = sorted(result['yearly_stats'].keys())
                        yearly_parts = []
                        for y in years:
                            y_stat = result['yearly_stats'][y]
                            yearly_parts.append(f"{y}年:{y_stat['rate']:.1f}%")
                        yearly_info = " [" + ", ".join(yearly_parts) + "]"
                    
                    excel_total_info = ""
                    if result.get('school_total_from_excel'):
                        excel_total_info = f" [Excel总人数:{result['school_total_from_excel']}]"
                    print(f"    ✅ {sheet_name:30s} - 总体:{result['band1_rate']:5.2f}% ({result['band1_students']}/{result['total_students']}){yearly_info}{excel_total_info}")
                else:
                    print(f"    ⚠️  {sheet_name:30s} - 无数据")
                    
            except Exception as e:
                print(f"    ❌ {sheet_name:30s} - 处理失败: {str(e)}")
        
        return {
            'district': district,
            'schools': results
        }
        
    except Exception as e:
        print(f"  ❌ 文件处理失败: {str(e)}")
        return None


def main():
    """
    主函数
    """
    print("=" * 80)
    print("小学升中 Band 1 比例统计工具（支持按年份统计 + 繁简转换）")
    print("=" * 80)
    
    data_dir = Path(__file__).parent
    
    # 加载小学总人数信息
    totals_file = data_dir.parent / 'data' / '2025年小学概览-估算小六学生人数.xlsx'
    if not totals_file.exists():
        print(f"\n❌ 错误：找不到小学总人数信息文件: {totals_file}")
        return
    
    school_totals = load_primary_school_totals(totals_file)
    
    # 加载中学 Band 映射
    band_file = data_dir / '中学banding信息_new.xlsx'
    if not band_file.exists():
        print(f"\n❌ 错误：找不到中学 banding 信息文件: {band_file}")
        return
    
    band_map, band_map_simplified = load_secondary_band_map(band_file)
    
    # 获取所有升学数据文件
    excel_files = list(data_dir.glob('*升学数据.xlsx'))
    print(f"\n找到 {len(excel_files)} 个升学数据文件")
    
    # 处理每个文件
    all_districts = []
    all_schools = []
    
    for file_path in sorted(excel_files):
        result = process_excel_file(file_path, band_map, band_map_simplified, school_totals)
        if result:
            all_districts.append(result)
            all_schools.extend(result['schools'])
    
    # 汇总统计
    print("\n" + "=" * 80)
    print("汇总统计")
    print("=" * 80)
    
    if not all_schools:
        print("没有找到任何有效的小学数据！")
        return
    
    total_students = sum(s['total_students'] for s in all_schools)
    band1_students = sum(s['band1_students'] for s in all_schools)
    band1_rate = (band1_students / total_students * 100) if total_students > 0 else 0
    
    print(f"\n总计:")
    print(f"  小学数量: {len(all_schools)} 所")
    print(f"  升学总人数: {total_students}")
    print(f"  升入 Band 1: {band1_students} 人")
    print(f"  Band 1 比例: {band1_rate:.2f}%")
    
    # 年度汇总统计
    yearly_total_stats = defaultdict(lambda: {'total': 0, 'band1': 0})
    for school in all_schools:
        if school.get('yearly_stats'):
            for year, stats in school['yearly_stats'].items():
                yearly_total_stats[year]['total'] += stats['total']
                yearly_total_stats[year]['band1'] += stats['band1']
    
    if yearly_total_stats:
        print(f"\n年度 Band 1 比例:")
        for year in sorted(yearly_total_stats.keys()):
            stats = yearly_total_stats[year]
            rate = (stats['band1'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {year}年: {rate:.2f}% ({stats['band1']}/{stats['total']})")
    
    # 按 Band 1 比例排序
    print(f"\nBand 1 比例 Top 20 小学:")
    sorted_schools = sorted([s for s in all_schools if s['total_students'] >= 10], 
                           key=lambda x: x['band1_rate'], reverse=True)
    
    for i, school in enumerate(sorted_schools[:20], 1):
        print(f"  {i:2d}. {school['primary_school']:35s} - {school['band1_rate']:5.2f}% "
              f"({school['band1_students']:3d}/{school['total_students']:3d})")
    
    # 按区域汇总
    print(f"\n各区域 Band 1 比例:")
    for district_data in all_districts:
        district = district_data['district']
        district_schools = district_data['schools']
        if district_schools:
            total = sum(s['total_students'] for s in district_schools)
            band1 = sum(s['band1_students'] for s in district_schools)
            rate = (band1 / total * 100) if total > 0 else 0
            print(f"  {district:10s} - {rate:5.2f}% ({band1:4d}/{total:4d}) - {len(district_schools)} 所小学")
    
    # 保存结果到 JSON
    output_file = data_dir / 'primary_schools_band1_stats.json'
    
    # 准备年度汇总统计
    yearly_summary = {}
    for year in sorted(yearly_total_stats.keys()):
        stats = yearly_total_stats[year]
        rate = (stats['band1'] / stats['total'] * 100) if stats['total'] > 0 else 0
        yearly_summary[year] = {
            'total': stats['total'],
            'band1': stats['band1'],
            'rate': round(rate, 2)
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_schools': len(all_schools),
                'total_students': total_students,
                'band1_students': band1_students,
                'band1_rate': round(band1_rate, 2),
                'generated_at': pd.Timestamp.now().isoformat(),
                'yearly_summary': yearly_summary  # 新增：年度汇总
            },
            'schools': sorted_schools,
            'districts': all_districts
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 统计结果已保存到: {output_file}")
    
    # 生成 CSV 报告（按小学，包含年度数据）
    csv_file = data_dir / 'primary_schools_band1_rate.csv'
    with open(csv_file, 'w', encoding='utf-8-sig') as f:
        # CSV 表头
        f.write("小学名称,区域,升学总人数,Excel总人数,Band 1人数,Band 1比例,2023年比例,2024年比例,2025年比例\n")
        
        for school in sorted_schools:
            # 查找该小学所在区域
            district = "未知"
            for d_data in all_districts:
                if any(s['primary_school'] == school['primary_school'] for s in d_data['schools']):
                    district = d_data['district']
                    break
            
            # 获取年度数据
            year_2023 = school.get('yearly_stats', {}).get(2023, {}).get('rate', '')
            year_2024 = school.get('yearly_stats', {}).get(2024, {}).get('rate', '')
            year_2025 = school.get('yearly_stats', {}).get(2025, {}).get('rate', '')
            
            year_2023_str = f"{year_2023}%" if year_2023 else "-"
            year_2024_str = f"{year_2024}%" if year_2024 else "-"
            year_2025_str = f"{year_2025}%" if year_2025 else "-"
            
            excel_total = school.get('school_total_from_excel', '')
            f.write(f"{school['primary_school']},{district},{school['total_students']},{excel_total},"
                   f"{school['band1_students']},{school['band1_rate']}%,"
                   f"{year_2023_str},{year_2024_str},{year_2025_str}\n")
    
    print(f"✅ CSV 报告已保存到: {csv_file}")
    
    # 生成详细报告
    detail_file = data_dir / 'primary_schools_detailed_report.txt'
    with open(detail_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("小学升中 Band 1 比例详细报告（按小学统计）\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"总计:\n")
        f.write(f"  小学数量: {len(all_schools)} 所\n")
        f.write(f"  升学总人数: {total_students}\n")
        f.write(f"  升入 Band 1: {band1_students} 人\n")
        f.write(f"  Band 1 比例: {band1_rate:.2f}%\n\n")
        
        # 按区域分组
        for district_data in all_districts:
            district = district_data['district']
            district_schools = district_data['schools']
            
            if not district_schools:
                continue
            
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{district}\n")
            f.write(f"{'=' * 80}\n")
            
            # 按 Band 1 比例排序
            sorted_district_schools = sorted(district_schools, key=lambda x: x['band1_rate'], reverse=True)
            
            for school in sorted_district_schools:
                f.write(f"\n{school['primary_school']}\n")
                f.write(f"  升学总人数: {school['total_students']}\n")
                if school.get('school_total_from_excel'):
                    f.write(f"  Excel总人数: {school['school_total_from_excel']}\n")
                f.write(f"  Band 1 人数: {school['band1_students']}\n")
                f.write(f"  Band 1 比例: {school['band1_rate']:.2f}%\n")
                
                # 年度统计
                if school.get('yearly_stats'):
                    f.write(f"  年度统计:\n")
                    for year in sorted(school['yearly_stats'].keys()):
                        y_stat = school['yearly_stats'][year]
                        f.write(f"    {year}年: {y_stat['rate']:.2f}% ({y_stat['band1']}/{y_stat['total']})\n")
                
                # Band 分布
                if school['band_distribution']:
                    f.write(f"  Band 分布:\n")
                    for band, count in sorted(school['band_distribution'].items()):
                        f.write(f"    {band}: {count} 人\n")
                
                # 主要升学中学（Top 5）
                if school['secondary_schools']:
                    f.write(f"  主要升学中学:\n")
                    for sec_school, count in list(school['secondary_schools'].items())[:5]:
                        band = match_school_name(sec_school, band_map, band_map_simplified)
                        band_str = f"({band})" if band else "(未知Band)"
                        f.write(f"    {sec_school} {band_str}: {count} 人\n")
                
                # 未匹配的学校
                if school['unmatched_schools']:
                    f.write(f"  ⚠️ 未匹配到 Band 的学校: {len(school['unmatched_schools'])} 所\n")
                    for sch in school['unmatched_schools'][:3]:
                        f.write(f"    - {sch}\n")
    
    print(f"✅ 详细报告已保存到: {detail_file}")
    
    print("\n" + "=" * 80)
    print("统计完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()

