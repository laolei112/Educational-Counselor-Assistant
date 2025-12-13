#!/usr/bin/env python3
"""
香港中学详细信息导入脚本
从 Excel 文件读取中学详细数据（教师信息、班级信息、课程设置、学校政策等）并写入 tb_secondary_schools 表

Excel 表头对应：
- 區域 -> district
- 學校名稱 -> school_name (用于匹配)
- 學校佔地面積 -> school_area
- 辦學團體 -> school_sponsor
- 創校年份 -> founded_year
- 校訓 -> school_motto
- 教師總人數 -> teacher_count
- 學士人數百分率、碩士_博士或以上人數百分率、特殊教育培訓人數百分率、
  0至4年經驗人數百分率、5至9年經驗人數百分率、10年經驗或以上人數百分率 -> teacher_info (JSON)
- 2025_2026學年擬開設科目_* (6列) -> curriculum_by_language (JSON)
- 本學年中一至中六班數 (6列) -> classes_by_grade (JSON)
- 備註 -> remarks
- 中一入學 -> admission_info
- 全校語文政策 -> language_policy
- 學習和教學策略 -> teaching_strategy
- 校本課程 -> school_based_curriculum
- 生涯規劃教育 -> career_education
- 全校參與照顧學生的多樣性 -> diversity_support
- 測考及學習調適措施 -> assessment_adaptation
- 全方位學習 -> whole_person_learning
- 學校設施 -> facilities
- 直達學校的公共交通工具 -> transportation
"""

import os
import sys
import json
import pandas as pd
import django
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_secondary_schools import TbSecondarySchools

# 繁体转简体映射表（常用字）
TRADITIONAL_TO_SIMPLIFIED = {
    '書': '书', '學': '学', '會': '会', '國': '国', '區': '区',
    '師': '师', '紀': '纪', '業': '业', '聖': '圣', '華': '华',
    '協': '协', '團': '团', '體': '体', '廠': '厂', '廣': '广',
    '東': '东', '馬': '马', '進': '进', '遠': '远', '運': '运',
    '過': '过', '還': '还', '這': '这', '邊': '边', '達': '达',
    '選': '选', '連': '连', '關': '关', '開': '开', '門': '门',
    '間': '间', '閱': '阅', '陽': '阳', '電': '电', '雲': '云',
    '頭': '头', '風': '风', '飛': '飞', '馬': '马', '駐': '驻',
    '驗': '验', '魚': '鱼', '鳥': '鸟', '麗': '丽', '黃': '黄',
    '點': '点', '齊': '齐', '齒': '齿', '龍': '龙', '龜': '龟',
    '傳': '传', '優': '优', '億': '亿', '儀': '仪', '價': '价',
    '創': '创', '則': '则', '劃': '划', '動': '动', '務': '务',
    '勞': '劳', '勝': '胜', '區': '区', '醫': '医', '衛': '卫',
    '縣': '县', '參': '参', '雙': '双', '發': '发', '變': '变',
    '號': '号', '問': '问', '啟': '启', '園': '园', '場': '场',
    '報': '报', '壓': '压', '夢': '梦', '獎': '奖', '將': '将',
    '專': '专', '導': '导', '層': '层', '歲': '岁', '帶': '带',
    '師': '师', '歸': '归', '張': '张', '強': '强', '當': '当',
    '彙': '汇', '徑': '径', '從': '从', '復': '复', '應': '应',
    '態': '态', '總': '总', '戰': '战', '戲': '戏', '擁': '拥',
    '據': '据', '損': '损', '換': '换', '擴': '扩', '擔': '担',
    '擇': '择', '擊': '击', '擾': '扰', '攝': '摄', '敗': '败',
    '數': '数', '條': '条', '標': '标', '樣': '样', '機': '机',
    '權': '权', '歡': '欢', '殘': '残', '氣': '气', '決': '决',
    '沒': '没', '濟': '济', '測': '测', '準': '准', '滿': '满',
    '漢': '汉', '滅': '灭', '燈': '灯', '營': '营', '獨': '独',
    '獲': '获', '產': '产', '異': '异', '療': '疗', '發': '发',
    '監': '监', '盡': '尽', '碼': '码', '礦': '矿', '確': '确',
    '禮': '礼', '稱': '称', '積': '积', '穩': '稳', '競': '竞',
    '節': '节', '範': '范', '築': '筑', '類': '类', '紅': '红',
    '約': '约', '純': '纯', '紙': '纸', '級': '级', '結': '结',
    '統': '统', '經': '经', '綠': '绿', '維': '维', '網': '网',
    '緊': '紧', '線': '线', '練': '练', '組': '组', '織': '织',
    '終': '终', '給': '给', '絕': '绝', '繼': '继', '續': '续',
    '義': '义', '習': '习', '聯': '联', '職': '职', '聲': '声',
    '與': '与', '興': '兴', '舊': '旧', '節': '节', '藝': '艺',
    '蘇': '苏', '處': '处', '號': '号', '蟲': '虫', '術': '术',
    '補': '补', '裝': '装', '製': '制', '複': '复', '規': '规',
    '視': '视', '覺': '觉', '親': '亲', '觀': '观', '記': '记',
    '設': '设', '許': '许', '訊': '讯', '診': '诊', '評': '评',
    '詞': '词', '詢': '询', '試': '试', '話': '话', '該': '该',
    '語': '语', '說': '说', '課': '课', '調': '调', '談': '谈',
    '請': '请', '論': '论', '諸': '诸', '證': '证', '識': '识',
    '譯': '译', '議': '议', '護': '护', '讀': '读', '讓': '让',
    '貝': '贝', '負': '负', '財': '财', '責': '责', '質': '质',
    '貿': '贸', '費': '费', '資': '资', '賓': '宾', '賽': '赛',
    '購': '购', '貴': '贵', '賣': '卖', '賞': '赏', '贊': '赞',
    '軍': '军', '軟': '软', '較': '较', '載': '载', '輕': '轻',
    '輔': '辅', '輪': '轮', '輸': '输', '轉': '转', '辦': '办',
    '農': '农', '邊': '边', '遲': '迟', '適': '适', '選': '选',
    '遺': '遗', '鄉': '乡', '鄰': '邻', '錄': '录', '錢': '钱',
    '錯': '错', '鍵': '键', '鎮': '镇', '長': '长', '門': '门',
    '閉': '闭', '開': '开', '閒': '闲', '間': '间', '關': '关',
    '陰': '阴', '陳': '陈', '陸': '陆', '險': '险', '隨': '随',
    '隱': '隐', '隸': '隶', '難': '难', '雜': '杂', '離': '离',
    '電': '电', '靈': '灵', '靜': '静', '響': '响', '頁': '页',
    '預': '预', '領': '领', '頻': '频', '題': '题', '願': '愿',
    '顯': '显', '類': '类', '飯': '饭', '養': '养', '餘': '余',
    '館': '馆', '駕': '驾', '驗': '验', '體': '体', '髮': '发',
    '鬥': '斗', '鬧': '闹', '魯': '鲁', '鮮': '鲜', '麥': '麦',
    '麼': '么', '黨': '党', '齡': '龄', '蔭': '荫', '託': '托',
    '僑': '侨', '儲': '储', '優': '优', '勵': '励', '勳': '勋',
    '嶺': '岭', '廈': '厦', '彌': '弥', '徵': '征', '憲': '宪',
    '慶': '庆', '憶': '忆', '懷': '怀', '攜': '携', '斷': '断',
    '歷': '历', '歸': '归', '濱': '滨', '瀾': '澜', '燦': '灿',
    '獻': '献', '環': '环', '畢': '毕', '盧': '卢', '瞭': '了',
    '礎': '础', '禪': '禅', '競': '竞', '築': '筑', '簡': '简',
    '籌': '筹', '籍': '籍', '紮': '扎', '繩': '绳', '繪': '绘',
    '繳': '缴', '續': '续', '罰': '罚', '羅': '罗', '翹': '翘',
    '聯': '联', '聰': '聪', '膽': '胆', '臨': '临', '舉': '举',
    '舊': '旧', '艷': '艳', '蘭': '兰', '處': '处', '蠟': '蜡',
    '補': '补', '覽': '览', '觸': '触', '訂': '订', '詳': '详',
    '諮': '咨', '謀': '谋', '謝': '谢', '謹': '谨', '議': '议',
    '譜': '谱', '護': '护', '讚': '赞', '貓': '猫', '賀': '贺',
    '贈': '赠', '趙': '赵', '跡': '迹', '躍': '跃', '軌': '轨',
    '輯': '辑', '辭': '辞', '農': '农', '遷': '迁', '邏': '逻',
    '鄭': '郑', '鑑': '鉴', '鑒': '鉴', '鑽': '钻', '閃': '闪',
    '閣': '阁', '閱': '阅', '闆': '板', '陣': '阵', '階': '阶',
    '際': '际', '隊': '队', '隸': '隶', '雞': '鸡', '雜': '杂',
    '霸': '霸', '靈': '灵', '頓': '顿', '顧': '顾', '飾': '饰',
    '駐': '驻', '驅': '驱', '驚': '惊', '骯': '肮', '髒': '脏',
    '鬆': '松', '鳳': '凤', '鴻': '鸿', '鵬': '鹏', '麵': '面',
    '齋': '斋', '龐': '庞',
}

def traditional_to_simplified(text):
    """将繁体中文转换为简体中文"""
    if not text:
        return text
    result = []
    for char in text:
        result.append(TRADITIONAL_TO_SIMPLIFIED.get(char, char))
    return ''.join(result)


def clean_value(value):
    """清理数据值"""
    if pd.isna(value) or value == 'nan' or value == '-' or value == '':
        return None
    return str(value).strip()


def clean_percentage(value):
    """清理百分比值"""
    if pd.isna(value) or value == 'nan' or value == '-' or value == '':
        return None
    # 如果是数字，直接返回
    if isinstance(value, (int, float)):
        return str(value)
    # 如果是字符串，去除百分号
    return str(value).strip().replace('%', '')


def clean_int(value):
    """清理整数值"""
    if pd.isna(value) or value == 'nan' or value == '-' or value == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def build_teacher_info(row):
    """
    构建教师信息 JSON
    """
    teacher_info = {}
    
    # 学历信息
    bachelor_rate = clean_percentage(row.get('學士人數百分率'))
    if bachelor_rate:
        teacher_info['bachelor_rate'] = bachelor_rate
    
    master_phd_rate = clean_percentage(row.get('碩士_博士或以上人數百分率'))
    if master_phd_rate:
        teacher_info['master_phd_rate'] = master_phd_rate
    
    special_ed_rate = clean_percentage(row.get('特殊教育培訓人數百分率'))
    if special_ed_rate:
        teacher_info['special_education_rate'] = special_ed_rate
    
    # 经验信息
    exp_0_4 = clean_percentage(row.get('0至4年經驗人數百分率'))
    if exp_0_4:
        teacher_info['experience_0_4_years'] = exp_0_4
    
    exp_5_9 = clean_percentage(row.get('5至9年經驗人數百分率'))
    if exp_5_9:
        teacher_info['experience_5_9_years'] = exp_5_9
    
    exp_10_plus = clean_percentage(row.get('10年經驗或以上人數百分率'))
    if exp_10_plus:
        teacher_info['experience_10_plus_years'] = exp_10_plus
    
    return teacher_info if teacher_info else None


def build_classes_by_grade(row):
    """
    构建各年级班数 JSON
    """
    classes_info = {}
    
    # 中一到中六班数
    s1 = clean_int(row.get('本學年中一班數'))
    if s1 is not None:
        classes_info['S1'] = s1
    
    s2 = clean_int(row.get('本學年中二班數'))
    if s2 is not None:
        classes_info['S2'] = s2
    
    s3 = clean_int(row.get('本學年中三班數'))
    if s3 is not None:
        classes_info['S3'] = s3
    
    s4 = clean_int(row.get('本學年中四班數'))
    if s4 is not None:
        classes_info['S4'] = s4
    
    s5 = clean_int(row.get('本學年中五班數'))
    if s5 is not None:
        classes_info['S5'] = s5
    
    s6 = clean_int(row.get('本學年中六班數'))
    if s6 is not None:
        classes_info['S6'] = s6
    
    # 计算总班数
    if classes_info:
        total = sum(v for v in classes_info.values() if v is not None)
        classes_info['total'] = total
    
    return classes_info if classes_info else None


def build_curriculum_by_language(row):
    """
    构建按教学语言分类的课程 JSON
    """
    curriculum = {
        'junior': {  # 中一至中三
            'chinese_medium': None,
            'english_medium': None,
            'mixed_medium': None
        },
        'senior': {  # 中四至中六
            'chinese_medium': None,
            'english_medium': None,
            'mixed_medium': None
        }
    }
    
    # 中一至中三
    junior_chinese = clean_value(row.get('2025_2026學年擬開設科目_以中文為教學語言_中一至中三'))
    if junior_chinese:
        curriculum['junior']['chinese_medium'] = junior_chinese
    
    junior_english = clean_value(row.get('2025_2026學年擬開設科目_以英文為教學語言_中一至中三'))
    if junior_english:
        curriculum['junior']['english_medium'] = junior_english
    
    junior_mixed = clean_value(row.get('2025_2026學年擬開設科目_按班別_組別訂定教學語言_中一至中三'))
    if junior_mixed:
        curriculum['junior']['mixed_medium'] = junior_mixed
    
    # 中四至中六
    senior_chinese = clean_value(row.get('2025_2026學年擬開設科目_以中文為教學語言_中四至中六'))
    if senior_chinese:
        curriculum['senior']['chinese_medium'] = senior_chinese
    
    senior_english = clean_value(row.get('2025_2026學年擬開設科目_以英文為教學語言_中四至中六'))
    if senior_english:
        curriculum['senior']['english_medium'] = senior_english
    
    senior_mixed = clean_value(row.get('2025_2026學年擬開設科目_按班別_組別訂定教學語言_中四至中六'))
    if senior_mixed:
        curriculum['senior']['mixed_medium'] = senior_mixed
    
    # 检查是否有任何有效数据
    has_data = any([
        curriculum['junior']['chinese_medium'],
        curriculum['junior']['english_medium'],
        curriculum['junior']['mixed_medium'],
        curriculum['senior']['chinese_medium'],
        curriculum['senior']['english_medium'],
        curriculum['senior']['mixed_medium']
    ])
    
    return curriculum if has_data else None


def process_excel_data(excel_file_path):
    """处理 Excel 数据"""
    print(f"正在读取 Excel 文件: {excel_file_path}")
    
    try:
        df = pd.read_excel(excel_file_path)
        print(f"成功读取 {len(df)} 条记录")
        print(f"Excel 列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"读取 Excel 文件失败: {str(e)}")
        sys.exit(1)


def import_secondary_school_details(excel_file_path, create_if_not_exists=False):
    """
    从 Excel 导入中学详细数据
    
    Args:
        excel_file_path: Excel 文件路径
        create_if_not_exists: 如果学校不存在是否创建新记录
    """
    print(f"正在处理中学详细数据文件: {excel_file_path}")
    
    # 读取 Excel 数据
    df = process_excel_data(excel_file_path)
    
    updated_count = 0
    created_count = 0
    not_found_count = 0
    error_count = 0
    not_found_schools = []
    
    for index, row in df.iterrows():
        try:
            # 获取学校名称用于匹配（Excel中是繁体）
            school_name_traditional = clean_value(row.get('學校名稱'))
            if not school_name_traditional:
                error_count += 1
                print(f"第 {index + 2} 行: 学校名称为空，跳过")
                continue
            
            # 将繁体转换为简体用于匹配
            school_name_simplified = traditional_to_simplified(school_name_traditional)
            
            # 查找现有学校记录（用简体名称匹配）
            existing_school = TbSecondarySchools.objects.filter(school_name=school_name_simplified).first()
            
            # 如果没找到，尝试用繁体名称字段查找
            if not existing_school:
                existing_school = TbSecondarySchools.objects.filter(
                    school_name_traditional=school_name_traditional
                ).first()
            
            # 如果还是没找到，尝试模糊匹配（去掉括号内容）
            if not existing_school:
                # 去掉括号及其内容
                import re
                simplified_clean = re.sub(r'[（(][^）)]*[）)]', '', school_name_simplified).strip()
                if simplified_clean != school_name_simplified:
                    existing_school = TbSecondarySchools.objects.filter(
                        school_name__contains=simplified_clean
                    ).first()
            
            # 准备更新数据
            update_data = {}
            
            # 基本信息
            district = clean_value(row.get('區域'))
            if district:
                update_data['district'] = district
            
            school_area = clean_value(row.get('學校佔地面積'))
            if school_area:
                update_data['school_area'] = school_area
            
            school_sponsor = clean_value(row.get('辦學團體'))
            if school_sponsor:
                update_data['school_sponsor'] = school_sponsor
            
            founded_year = clean_value(row.get('創校年份'))
            if founded_year:
                update_data['founded_year'] = founded_year
            
            school_motto = clean_value(row.get('校訓'))
            if school_motto:
                update_data['school_motto'] = school_motto
            
            # 教师信息
            teacher_count = clean_int(row.get('教師總人數'))
            if teacher_count is not None:
                update_data['teacher_count'] = teacher_count
            
            teacher_info = build_teacher_info(row)
            if teacher_info:
                update_data['teacher_info'] = teacher_info
            
            # 班级信息
            classes_by_grade = build_classes_by_grade(row)
            if classes_by_grade:
                update_data['classes_by_grade'] = classes_by_grade
                # 同时更新 total_classes
                update_data['total_classes'] = classes_by_grade.get('total')
            
            # 课程信息
            curriculum_by_language = build_curriculum_by_language(row)
            if curriculum_by_language:
                update_data['curriculum_by_language'] = curriculum_by_language
            
            # 入学信息
            admission_info = clean_value(row.get('中一入學'))
            if admission_info:
                update_data['admission_info'] = admission_info
            
            # 学校政策与特色
            language_policy = clean_value(row.get('全校語文政策'))
            if language_policy:
                update_data['language_policy'] = language_policy
            
            teaching_strategy = clean_value(row.get('學習和教學策略'))
            if teaching_strategy:
                update_data['teaching_strategy'] = teaching_strategy
            
            school_based_curriculum = clean_value(row.get('校本課程'))
            if school_based_curriculum:
                update_data['school_based_curriculum'] = school_based_curriculum
            
            career_education = clean_value(row.get('生涯規劃教育'))
            if career_education:
                update_data['career_education'] = career_education
            
            diversity_support = clean_value(row.get('全校參與照顧學生的多樣性'))
            if diversity_support:
                update_data['diversity_support'] = diversity_support
            
            assessment_adaptation = clean_value(row.get('測考及學習調適措施'))
            if assessment_adaptation:
                update_data['assessment_adaptation'] = assessment_adaptation
            
            whole_person_learning = clean_value(row.get('全方位學習'))
            if whole_person_learning:
                update_data['whole_person_learning'] = whole_person_learning
            
            # 设施与交通
            facilities = clean_value(row.get('學校設施'))
            if facilities:
                update_data['facilities'] = facilities
            
            transportation = clean_value(row.get('直達學校的公共交通工具'))
            if transportation:
                update_data['transportation'] = transportation
            
            remarks = clean_value(row.get('備註'))
            if remarks:
                update_data['remarks'] = remarks
            
            if existing_school:
                # 更新现有记录
                for key, value in update_data.items():
                    setattr(existing_school, key, value)
                existing_school.save()
                updated_count += 1
                if updated_count <= 5:
                    print(f"✅ 更新学校: {school_name_traditional}")
            elif create_if_not_exists:
                # 创建新记录
                update_data['school_name'] = school_name_simplified
                update_data['school_name_traditional'] = school_name_traditional
                TbSecondarySchools.objects.create(**update_data)
                created_count += 1
                if created_count <= 5:
                    print(f"➕ 创建学校: {school_name_traditional}")
            else:
                not_found_count += 1
                not_found_schools.append(f"{school_name_traditional} -> {school_name_simplified}")
                if not_found_count <= 10:
                    print(f"⚠️  未找到学校: {school_name_traditional} (简体: {school_name_simplified})")
            
            # 每处理 50 条输出进度
            processed = updated_count + created_count + not_found_count
            if processed % 50 == 0:
                print(f"已处理 {processed} 条记录...")
                
        except Exception as e:
            error_count += 1
            school_name = row.get('學校名稱', 'Unknown')
            print(f"❌ 处理数据时出错: {school_name} - {str(e)}")
            import traceback
            traceback.print_exc()
    
    return updated_count, created_count, not_found_count, error_count, not_found_schools


def main():
    """主函数"""
    print("=" * 60)
    print("香港中学详细信息导入工具")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 从命令行参数获取 Excel 文件路径，或使用默认路径
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        # 默认路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        excel_file = os.path.join(current_dir, '中学数据.xlsx')
    
    # 检查是否需要创建不存在的学校
    create_if_not_exists = '--create' in sys.argv
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误: 找不到 Excel 文件 {excel_file}")
        print("\n用法:")
        print("  python import_secondary_school_details.py [Excel文件路径] [--create]")
        print("\n选项:")
        print("  --create  如果学校不存在则创建新记录")
        sys.exit(1)
    
    try:
        # 导入数据
        print("\n开始导入数据...")
        print(f"创建不存在的学校: {'是' if create_if_not_exists else '否'}")
        print()
        
        updated_count, created_count, not_found_count, error_count, not_found_schools = \
            import_secondary_school_details(excel_file, create_if_not_exists)
        
        # 输出统计信息
        print("\n" + "=" * 60)
        print("导入完成")
        print("=" * 60)
        print(f"成功更新: {updated_count} 条记录")
        print(f"成功创建: {created_count} 条记录")
        print(f"未找到学校: {not_found_count} 条")
        print(f"失败记录: {error_count} 条")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示数据库中的总记录数
        total_count = TbSecondarySchools.objects.count()
        print(f"\n数据库中共有 {total_count} 条中学记录")
        
        # 如果有未找到的学校，输出到文件
        if not_found_schools:
            output_file = os.path.join(os.path.dirname(excel_file), 'not_found_schools.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(not_found_schools))
            print(f"\n未找到的学校列表已保存到: {output_file}")
        
        # 显示更新后的数据示例
        print("\n" + "=" * 60)
        print("更新后的数据示例（前3条有教师信息的学校）:")
        print("=" * 60)
        
        sample_schools = TbSecondarySchools.objects.exclude(
            teacher_info__isnull=True
        )[:3]
        
        for school in sample_schools:
            print(f"\n学校: {school.school_name}")
            print(f"  区域: {school.district}")
            print(f"  办学团体: {school.school_sponsor}")
            print(f"  创校年份: {school.founded_year}")
            print(f"  教师总数: {school.teacher_count}")
            if school.teacher_info:
                print(f"  教师信息: {json.dumps(school.teacher_info, ensure_ascii=False, indent=4)}")
            if school.classes_by_grade:
                print(f"  班级信息: {json.dumps(school.classes_by_grade, ensure_ascii=False, indent=4)}")
        
    except Exception as e:
        print(f"\n导入过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
