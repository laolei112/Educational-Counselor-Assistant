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
import ast

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

SPECIAL_SCHOOL_NAMES = ['嘉诺撒圣心学校私立部', '李志达纪念学校', '灵光小学']
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


def parse_alias_list(alias_text):
    """
    解析别名列表，支持JSON数组格式和分隔符格式
    """
    if not alias_text or not alias_text.strip():
        return []
    
    alias_text = alias_text.strip()
    
    # 尝试解析JSON数组格式
    if alias_text.startswith('[') and alias_text.endswith(']'):
        try:
            # 使用ast.literal_eval解析Python列表格式
            aliases = ast.literal_eval(alias_text)
            if isinstance(aliases, list):
                return [str(alias).strip() for alias in aliases if alias and str(alias).strip()]
        except (ValueError, SyntaxError):
            try:
                # 使用json.loads解析JSON格式
                aliases = json.loads(alias_text)
                if isinstance(aliases, list):
                    return [str(alias).strip() for alias in aliases if alias and str(alias).strip()]
            except (ValueError, json.JSONDecodeError):
                pass
    
    # 如果JSON解析失败，回退到分隔符格式
    # 支持多种分隔符：逗号、分号、竖线、换行符
    aliases = [alias.strip() for alias in alias_text.replace(';', ',').replace('|', ',').replace('\n', ',').split(',') if alias.strip()]
    return aliases


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
            # 优先匹配确切的列名
            if '学校名称' in col:
                school_name_col = col
            elif '小六学生人数（估算）2025届毕业' in col:
                student_count_col = col
            # 备用匹配
            elif any(keyword in col_str for keyword in ['学校', 'school', '名称', 'name']) and school_name_col is None:
                school_name_col = col
            elif any(keyword in col_str for keyword in ['人数', '学生', 'student', '小六', '六年级', '估算']) and student_count_col is None:
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
    加载中学 Band 映射，同时建立繁体和简体两个映射，包含别名支持
    """
    print(f"正在加载中学 Band 信息: {band_file}")
    
    df = pd.read_excel(band_file)
    band_map = {}
    band_map_simplified = {}
    alias_map = {}  # 别名映射
    alias_map_simplified = {}  # 简体别名映射
    
    for idx, row in df.iterrows():
        school_name = row['school_name']
        school_group = row['school_group']
        alias_simple = row.get('alias_simple_name', '')
        alias_traditional = row.get('alias_tranditional_name', '')
        
        if pd.notna(school_name) and pd.notna(school_group):
            school_name = str(school_name).strip()
            school_group = str(school_group).strip()
            
            # 原始名称（繁体）
            band_map[school_name] = school_group
            
            # 简体名称
            school_name_simplified = to_simplified(school_name)
            band_map_simplified[school_name_simplified] = school_group
            
            # 处理别名（支持JSON数组格式和列表格式）
            if pd.notna(alias_simple) and alias_simple.strip():
                alias_simple = str(alias_simple).strip()
                aliases_simple = parse_alias_list(alias_simple)
                for alias in aliases_simple:
                    alias_map[alias] = school_group
                    alias_map_simplified[to_simplified(alias)] = school_group
            
            if pd.notna(alias_traditional) and alias_traditional.strip():
                alias_traditional = str(alias_traditional).strip()
                aliases_traditional = parse_alias_list(alias_traditional)
                for alias in aliases_traditional:
                    alias_map[alias] = school_group
                    alias_map_simplified[to_simplified(alias)] = school_group
    
    print(f"已加载 {len(band_map)} 所中学的 Band 信息")
    print(f"建立简体映射 {len(band_map_simplified)} 条")
    print(f"建立别名映射 {len(alias_map)} 条")
    print(f"建立简体别名映射 {len(alias_map_simplified)} 条")
    
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
    
    return band_map, band_map_simplified, alias_map, alias_map_simplified


def is_band_1(band_str):
    """
    判断是否为 Band 1
    """
    if not band_str:
        return False
    return 'Band 1' in band_str or band_str.startswith('1')


def match_school_name(target_name, band_map, band_map_simplified, alias_map=None, alias_map_simplified=None):
    """
    匹配学校名称，支持繁简转换、别名和模糊匹配
    """
    target_name = target_name.strip()
    
    # 1. 完全匹配（繁体）
    if target_name in band_map:
        return band_map[target_name]
    
    # 2. 转换为简体后完全匹配
    target_simplified = to_simplified(target_name)
    if target_simplified in band_map_simplified:
        return band_map_simplified[target_simplified]
    
    # 3. 别名匹配（繁体）
    if alias_map and target_name in alias_map:
        return alias_map[target_name]
    
    # 4. 别名匹配（简体）
    if alias_map_simplified and target_simplified in alias_map_simplified:
        return alias_map_simplified[target_simplified]
    
    # 5. 添加"香港"前缀匹配
    hk_target = f"香港{target_name}"
    if hk_target in band_map:
        return band_map[hk_target]
    
    hk_target_simplified = to_simplified(hk_target)
    if hk_target_simplified in band_map_simplified:
        return band_map_simplified[hk_target_simplified]
 
    # 6. 添加"粉岭"前缀匹配
    fenlin_target = f"粉岭{target_name}"
    if fenlin_target in band_map:
        return band_map[fenlin_target]
    
    fenling_target_simplified = to_simplified(fenlin_target)
    if fenling_target_simplified in band_map_simplified:
        return band_map_simplified[fenling_target_simplified]   
 
    fenlin_target = f"{target_name[0:2]}" + "粉岭" + f"{target_name[3:]}"
    if fenlin_target in band_map:
        return band_map[fenlin_target]
    
    fenling_target_simplified = to_simplified(fenlin_target)
    if fenling_target_simplified in band_map_simplified:
        return band_map_simplified[fenling_target_simplified] 
    
    # 7. 括号转换匹配（半角转全角）
    bracket_target = target_name.replace('(', '（').replace(')', '）')
    if bracket_target in band_map:
        return band_map[bracket_target]
    
    bracket_target_simplified = to_simplified(bracket_target)
    if bracket_target_simplified in band_map_simplified:
        return band_map_simplified[bracket_target_simplified]
    
    # 8. 部分匹配（移除"中學"后缀）
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
    
    # 在别名映射中部分匹配
    if alias_map:
        for alias, band in alias_map.items():
            alias_base = alias.replace('中學', '').replace('中学', '').strip()
            if base_name == alias_base:
                return band
            if len(base_name) >= 5 and (base_name in alias or alias in target_name):
                return band
    
    if alias_map_simplified:
        for alias_simp, band in alias_map_simplified.items():
            alias_base_simp = alias_simp.replace('中学', '').strip()
            if base_name_simplified == alias_base_simp:
                return band
            if len(base_name_simplified) >= 5 and (base_name_simplified in alias_simp or alias_simp in target_simplified):
                return band
    
    return None


def process_primary_school_sheet(sheet_name, df, band_map, band_map_simplified, school_totals=None, alias_map=None, alias_map_simplified=None):
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
            elif len(sheet_name) >= 5 and (sheet_name in school_name or school_name in sheet_name) and sheet_name != "嘉诺撒圣心学校私立部":
                school_total_from_excel = total_count
                break
    
    for idx, row in df.iterrows():
        secondary_school = row.get('升入学校')
        count = row.get('人数')
        year = row.get('年份')
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
        
        # 匹配中学 Band（使用繁简双映射和别名）
        band = match_school_name(secondary_school, band_map, band_map_simplified, alias_map, alias_map_simplified)
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
            # 使用Excel中的总人数作为该年的总人数
            if school_total_from_excel and to_simplified(school_name) not in SPECIAL_SCHOOL_NAMES:
                yearly_stats[year]['total'] = school_total_from_excel
            else:
                # 如果没有Excel总人数，使用升学数据中的总人数
                yearly_stats[year]['total'] += count
            
            yearly_stats[year]['schools'][secondary_school] += count
            if band:
                yearly_stats[year]['band_dist'][band] += count
            else:
                yearly_stats[year]['band_dist']['未知'] += count
                yearly_stats[year]['unmatched'].append(secondary_school)
    
    # 计算所有年份的平均 Band 1 比例
    band1_rate = (band1_students / total_students * 100) if total_students > 0 else 0
    
    # 计算每年的 Band 1 比例
    yearly_band1_rates = {}
    for year, stats in yearly_stats.items():
        rate = (stats['band1'] / stats['total'] * 100) if stats['total'] > 0 else 0
        yearly_band1_rates[year] = {
            'total': stats['total'],
            'band1': stats['band1'],
            'rate': round(rate, 2),
            'schools': dict(stats['schools']),  # 保存升学中学信息
            'band_dist': dict(stats['band_dist']),  # 保存Band分布
            'unmatched': list(stats['unmatched'])  # 保存未匹配学校
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


def process_excel_file(file_path, band_map, band_map_simplified, school_totals=None, alias_map=None, alias_map_simplified=None):
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
                result = process_primary_school_sheet(sheet_name, df, band_map, band_map_simplified, school_totals, alias_map, alias_map_simplified)
                
                if result['total_students'] > 0:
                    result['district'] = district
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
    
    band_map, band_map_simplified, alias_map, alias_map_simplified = load_secondary_band_map(band_file)
    
    # 获取所有升学数据文件
    excel_files = list(data_dir.glob('*升学数据.xlsx'))
    print(f"\n找到 {len(excel_files)} 个升学数据文件")
    
    # 处理每个文件
    all_districts = []
    all_schools = []
    
    for file_path in sorted(excel_files):
        result = process_excel_file(file_path, band_map, band_map_simplified, school_totals, alias_map, alias_map_simplified)
        if result:
            all_districts.append(result)
            all_schools.extend(result['schools'])
    
    # 数据验证
    print("\n" + "=" * 80)
    print("数据验证")
    print("=" * 80)
    
    if not all_schools:
        print("没有找到任何有效的小学数据！")
        return
    
    print(f"找到 {len(all_schools)} 所小学的升学数据")
    
    # 按Band 1比例降序排序，比例相同时按学校名称排序
    sorted_schools = sorted(all_schools, key=lambda x: (-x['band1_rate'], x['primary_school']))
    
    # 保存结果到 JSON
    output_file = data_dir / 'primary_schools_band1_stats.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': pd.Timestamp.now().isoformat(),
            'total_schools': len(all_schools),
            'schools': sorted_schools
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 统计结果已保存到: {output_file}")
    
    # 生成历年详细数据 CSV
    csv_file = data_dir / 'primary_schools_yearly_details.csv'
    with open(csv_file, 'w', encoding='utf-8-sig') as f:
        # CSV 表头
        f.write("小学名称,年份,升学总人数,Band 1人数,Band 1比例,主要升学中学及Band信息\n")
        
        for school in sorted_schools:
            # 查找该小学所在区域
            district = "未知"
            for d_data in all_districts:
                if any(s['primary_school'] == school['primary_school'] for s in d_data['schools']):
                    district = d_data['district']
                    break
            
            # 输出每年的详细数据
            yearly_stats = school.get('yearly_stats', {})
            if yearly_stats:
                for year in sorted(yearly_stats.keys()):
                    year_data = yearly_stats[year]
                    total = year_data.get('total', 0)
                    band1 = year_data.get('band1', 0)
                    rate = year_data.get('rate', 0)
                    
                    # 获取该年度的主要升学中学信息
                    secondary_info = []
                    if 'schools' in year_data:
                        for sec_school, count in year_data['schools'].items():
                            band = match_school_name(sec_school, band_map, band_map_simplified, alias_map, alias_map_simplified)
                            band_str = f"({band})" if band else "(未知)"
                            secondary_info.append(f"{sec_school}{band_str}:{count}人")
                    
                    secondary_str = "; ".join(secondary_info[:5])  # 只显示前5个
                    f.write(f"{school['primary_school']},{year},{total},{band1},{rate}%,{secondary_str}\n")
            else:
                # 如果没有年度数据，输出总体数据
                f.write(f"{school['primary_school']},总体,{school['total_students']},{school['band1_students']},{school['band1_rate']}%,无年度数据\n")
    
    print(f"✅ CSV 报告已保存到: {csv_file}")
    
    # 生成历年详细报告
    detail_file = data_dir / 'primary_schools_yearly_report.txt'
    with open(detail_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("小学升中历年详细报告（按年份统计）\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"统计小学数量: {len(all_schools)} 所\n")
        f.write(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 按学校分组，显示历年数据
        for school in sorted_schools:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"{school['primary_school']}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"区域: {school['district']}\n")
            # 年度详细数据
            yearly_stats = school.get('yearly_stats', {})
            if yearly_stats:
                for year in sorted(yearly_stats.keys()):
                    year_data = yearly_stats[year]
                    total = year_data.get('total', 0)
                    band1 = year_data.get('band1', 0)
                    rate = year_data.get('rate', 0)
                    
                    f.write(f"\n{year}年:\n")
                    f.write(f"  升学总人数: {total}\n")
                    f.write(f"  Band 1 人数: {band1}\n")
                    f.write(f"  Band 1 比例: {rate:.2f}%\n")
                    
                    # 该年度的升学中学详情
                    if 'schools' in year_data and year_data['schools']:
                        f.write(f"  升学中学详情:\n")
                        for sec_school, count in sorted(year_data['schools'].items(), key=lambda x: x[1], reverse=True):
                            band = match_school_name(sec_school, band_map, band_map_simplified, alias_map, alias_map_simplified)
                            band_str = f"({band})" if band else "(未知Band)"
                            f.write(f"    {sec_school} {band_str}: {count} 人\n")
                    
                    # 该年度的Band分布
                    if 'band_dist' in year_data and year_data['band_dist']:
                        f.write(f"  Band 分布:\n")
                        for band, count in sorted(year_data['band_dist'].items()):
                            f.write(f"    {band}: {count} 人\n")
                    
                    # 未匹配的学校
                    if 'unmatched' in year_data and year_data['unmatched']:
                        f.write(f"  ⚠️ 未匹配到 Band 的学校: {len(year_data['unmatched'])} 所\n")
                        for sch in year_data['unmatched'][:3]:
                            f.write(f"    - {sch}\n")
            else:
                f.write(f"\n⚠️ 无年度数据，只有总体统计:\n")
                f.write(f"  升学总人数: {school['total_students']}\n")
                f.write(f"  Band 1 人数: {school['band1_students']}\n")
                f.write(f"  Band 1 比例: {school['band1_rate']:.2f}%\n")
    
    print(f"✅ 详细报告已保存到: {detail_file}")
    
    print("\n" + "=" * 80)
    print("统计完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()

