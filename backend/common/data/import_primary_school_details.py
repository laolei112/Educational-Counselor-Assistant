#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小学详情数据导入脚本

从 Excel 文件导入小学详情数据到数据库

表头字段映射：
区域 -> district
学校名称 -> school_name (用于匹配)
学校地址 -> address
小一学校网 -> school_net
学校电话 -> phone
学校电邮 -> email
学校网址 -> website
学校类别1 -> school_category
学校类别2 -> school_category_2
学生性别 -> student_gender
办学团体 -> school_sponsor
创校年份 -> founded_year
宗教 -> religion
校训 -> school_motto
学校占地面积 -> school_area
教学语言 -> teaching_language
一条龙中学 -> secondary_info.through_train
直属中学 -> secondary_info.direct
联系中学 -> secondary_info.associated
校车 -> school_bus
保姆车 -> nanny_bus
学费 -> tuition
课室数目 -> classroom_count
礼堂数目 -> hall_count
操场数目 -> playground_count
图书馆数目 -> library_count
特别室 -> special_rooms
上学年教师总人数 -> teacher_count
上学年学士人数百分率 -> teacher_info.bachelor_rate
上学年硕士_博士或以上人数百分率 -> teacher_info.master_phd_rate
上学年0至4年年资人数百分率 -> teacher_info.experience_0_4_years
上学年5至9年年资人数百分率 -> teacher_info.experience_5_9_years
上学年10年年资或以上人数百分率 -> teacher_info.experience_10_plus_years
本学年小一班数 -> classes_by_grade.P1
本学年小二班数 -> classes_by_grade.P2
本学年小三班数 -> classes_by_grade.P3
本学年小四班数 -> classes_by_grade.P4
本学年小五班数 -> classes_by_grade.P5
本学年小六班数 -> classes_by_grade.P6
本学年总班数 -> total_classes
班级教学模式 -> class_teaching_mode
全年全科测验次数_一年级 -> assessment_info.test_count_grade1
全年全科考试次数_一年级 -> assessment_info.exam_count_grade1
全年全科测验次数_二至六年级 -> assessment_info.test_count_grade2_6
全年全科考试次数_二至六年级 -> assessment_info.exam_count_grade2_6
多元学习评估 -> multi_assessment
分班安排 -> class_arrangement
午膳安排 -> lunch_arrangement
学校生活备注 -> school_life_notes
全方位学习 -> whole_person_learning
办学宗旨 -> school_mission
全校参与照顾学生的多样性 -> diversity_support
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

from backend.models.tb_primary_schools import TbPrimarySchools

# 繁体转简体映射表（常用字）
TRADITIONAL_TO_SIMPLIFIED = {
    '書': '书', '學': '学', '會': '会', '國': '国', '區': '区',
    '師': '师', '紀': '纪', '業': '业', '聖': '圣', '華': '华',
    '協': '协', '團': '团', '體': '体', '廠': '厂', '廣': '广',
    '東': '东', '馬': '马', '進': '进', '遠': '远', '運': '运',
    '過': '过', '還': '还', '這': '这', '邊': '边', '達': '达',
    '選': '选', '連': '连', '關': '关', '開': '开', '門': '门',
    '間': '间', '閱': '阅', '陽': '阳', '電': '电', '雲': '云',
    '頭': '头', '風': '风', '飛': '飞', '駐': '驻',
    '驗': '验', '魚': '鱼', '鳥': '鸟', '麗': '丽', '黃': '黄',
    '點': '点', '齊': '齐', '齒': '齿', '龍': '龙', '龜': '龟',
    '傳': '传', '優': '优', '億': '亿', '儀': '仪', '價': '价',
    '創': '创', '則': '则', '劃': '划', '動': '动', '務': '务',
    '勞': '劳', '勝': '胜', '醫': '医', '衛': '卫',
    '縣': '县', '參': '参', '雙': '双', '發': '发', '變': '变',
    '號': '号', '問': '问', '啟': '启', '園': '园', '場': '场',
    '報': '报', '壓': '压', '夢': '梦', '獎': '奖', '將': '将',
    '專': '专', '導': '导', '層': '层', '歲': '岁', '帶': '带',
    '歸': '归', '張': '张', '強': '强', '當': '当',
    '彙': '汇', '徑': '径', '從': '从', '復': '复', '應': '应',
    '態': '态', '總': '总', '戰': '战', '戲': '戏', '擁': '拥',
    '據': '据', '損': '损', '換': '换', '擴': '扩', '擔': '担',
    '擇': '择', '擊': '击', '擾': '扰', '攝': '摄', '敗': '败',
    '數': '数', '條': '条', '標': '标', '樣': '样', '機': '机',
    '權': '权', '歡': '欢', '殘': '残', '氣': '气', '決': '决',
    '沒': '没', '濟': '济', '測': '测', '準': '准', '滿': '满',
    '漢': '汉', '滅': '灭', '燈': '灯', '營': '营', '獨': '独',
    '獲': '获', '產': '产', '異': '异', '療': '疗',
    '監': '监', '盡': '尽', '碼': '码', '礦': '矿', '確': '确',
    '禮': '礼', '稱': '称', '積': '积', '穩': '稳', '競': '竞',
    '節': '节', '範': '范', '築': '筑', '類': '类', '紅': '红',
    '約': '约', '純': '纯', '紙': '纸', '級': '级', '結': '结',
    '統': '统', '經': '经', '綠': '绿', '維': '维', '網': '网',
    '緊': '紧', '線': '线', '練': '练', '組': '组', '織': '织',
    '終': '终', '給': '给', '絕': '绝', '繼': '继', '續': '续',
    '義': '义', '習': '习', '聯': '联', '職': '职', '聲': '声',
    '與': '与', '興': '兴', '舊': '旧', '藝': '艺',
    '蘇': '苏', '處': '处', '蟲': '虫', '術': '术',
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
    '農': '农', '遲': '迟', '適': '适',
    '遺': '遗', '鄉': '乡', '鄰': '邻', '錄': '录', '錢': '钱',
    '錯': '错', '鍵': '键', '鎮': '镇', '長': '长',
    '閉': '闭', '閒': '闲',
    '陰': '阴', '陳': '陈', '陸': '陆', '險': '险', '隨': '随',
    '隱': '隐', '隸': '隶', '難': '难', '雜': '杂', '離': '离',
    '靈': '灵', '靜': '静', '響': '响', '頁': '页',
    '預': '预', '領': '领', '頻': '频', '題': '题', '願': '愿',
    '顯': '显', '飯': '饭', '養': '养', '餘': '余',
    '館': '馆', '駕': '驾', '髮': '发',
    '鬥': '斗', '鬧': '闹', '魯': '鲁', '鮮': '鲜', '麥': '麦',
    '麼': '么', '黨': '党', '齡': '龄', '蔭': '荫', '託': '托',
    '僑': '侨', '儲': '储', '勵': '励', '勳': '勋',
    '嶺': '岭', '廈': '厦', '彌': '弥', '徵': '征', '憲': '宪',
    '慶': '庆', '憶': '忆', '懷': '怀', '攜': '携', '斷': '断',
    '歷': '历', '濱': '滨', '瀾': '澜', '燦': '灿',
    '獻': '献', '環': '环', '畢': '毕', '盧': '卢', '瞭': '了',
    '礎': '础', '禪': '禅', '簡': '简',
    '籌': '筹', '籍': '籍', '紮': '扎', '繩': '绳', '繪': '绘',
    '繳': '缴', '罰': '罚', '羅': '罗', '翹': '翘',
    '聰': '聪', '膽': '胆', '臨': '临', '舉': '举',
    '艷': '艳', '蘭': '兰', '蠟': '蜡',
    '覽': '览', '觸': '触', '訂': '订', '詳': '详',
    '諮': '咨', '謀': '谋', '謝': '谢', '謹': '谨',
    '譜': '谱', '讚': '赞', '貓': '猫', '賀': '贺',
    '贈': '赠', '趙': '赵', '跡': '迹', '躍': '跃', '軌': '轨',
    '輯': '辑', '辭': '辞', '遷': '迁', '邏': '逻',
    '鄭': '郑', '鑑': '鉴', '鑒': '鉴', '鑽': '钻', '閃': '闪',
    '閣': '阁', '闆': '板', '陣': '阵', '階': '阶',
    '際': '际', '隊': '队', '雞': '鸡',
    '霸': '霸', '頓': '顿', '顧': '顾', '飾': '饰',
    '驅': '驱', '驚': '惊', '骯': '肮', '髒': '脏',
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
    if pd.isna(value) or value == '' or value == '-' or value == '不適用' or value == '不适用':
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def parse_int(value):
    """解析整数"""
    if pd.isna(value) or value == '' or value == '-':
        return None
    try:
        # 处理可能的百分比或带单位的数字
        if isinstance(value, str):
            value = value.replace('%', '').replace('人', '').replace('個', '').replace('间', '').strip()
        return int(float(value))
    except (ValueError, TypeError):
        return None


def parse_float(value):
    """解析浮点数（百分比）"""
    if pd.isna(value) or value == '' or value == '-':
        return None
    try:
        if isinstance(value, str):
            value = value.replace('%', '').strip()
        return float(value)
    except (ValueError, TypeError):
        return None


def import_primary_school_details(excel_path, create_if_not_exists=False):
    """
    导入小学详情数据
    
    Args:
        excel_path: Excel 文件路径
        create_if_not_exists: 如果学校不存在是否创建新记录
    """
    print(f"开始导入小学详情数据: {excel_path}")
    
    # 读取 Excel 文件
    df = pd.read_excel(excel_path)
    print(f"读取到 {len(df)} 条记录")
    print(f"列名: {list(df.columns)}")
    
    updated_count = 0
    created_count = 0
    not_found_count = 0
    error_count = 0
    not_found_schools = []
    
    for index, row in df.iterrows():
        try:
            # 获取学校名称用于匹配（Excel中是繁体）
            school_name_traditional = clean_value(row.get('学校名称') or row.get('學校名稱'))
            if not school_name_traditional:
                error_count += 1
                print(f"第 {index + 2} 行: 学校名称为空，跳过")
                continue
            
            # 将繁体转换为简体用于匹配
            school_name_simplified = traditional_to_simplified(school_name_traditional)
            
            # 查找现有学校记录（用简体名称匹配）
            existing_school = TbPrimarySchools.objects.filter(school_name=school_name_simplified).first()
            
            # 如果没找到，尝试用繁体名称字段查找
            if not existing_school:
                existing_school = TbPrimarySchools.objects.filter(
                    school_name_traditional=school_name_traditional
                ).first()
            
            # 如果还是没找到，尝试模糊匹配（去掉括号内容）
            if not existing_school:
                import re
                simplified_clean = re.sub(r'[（(][^）)]*[）)]', '', school_name_simplified).strip()
                if simplified_clean != school_name_simplified:
                    existing_school = TbPrimarySchools.objects.filter(
                        school_name__contains=simplified_clean
                    ).first()
            
            # 构建教师信息 JSON
            teacher_info = {}
            bachelor_rate = parse_float(row.get('上学年学士人数百分率'))
            if bachelor_rate is not None:
                teacher_info['bachelor_rate'] = bachelor_rate
            master_phd_rate = parse_float(row.get('上学年硕士_博士或以上人数百分率'))
            if master_phd_rate is not None:
                teacher_info['master_phd_rate'] = master_phd_rate
            exp_0_4 = parse_float(row.get('上学年0至4年年资人数百分率'))
            if exp_0_4 is not None:
                teacher_info['experience_0_4_years'] = exp_0_4
            exp_5_9 = parse_float(row.get('上学年5至9年年资人数百分率'))
            if exp_5_9 is not None:
                teacher_info['experience_5_9_years'] = exp_5_9
            exp_10_plus = parse_float(row.get('上学年10年年资或以上人数百分率'))
            if exp_10_plus is not None:
                teacher_info['experience_10_plus_years'] = exp_10_plus
            
            # 构建班级信息 JSON
            classes_by_grade = {}
            p1 = parse_int(row.get('本学年小一班数'))
            if p1 is not None:
                classes_by_grade['P1'] = p1
            p2 = parse_int(row.get('本学年小二班数'))
            if p2 is not None:
                classes_by_grade['P2'] = p2
            p3 = parse_int(row.get('本学年小三班数'))
            if p3 is not None:
                classes_by_grade['P3'] = p3
            p4 = parse_int(row.get('本学年小四班数'))
            if p4 is not None:
                classes_by_grade['P4'] = p4
            p5 = parse_int(row.get('本学年小五班数'))
            if p5 is not None:
                classes_by_grade['P5'] = p5
            p6 = parse_int(row.get('本学年小六班数'))
            if p6 is not None:
                classes_by_grade['P6'] = p6
            
            # 构建评估信息 JSON
            assessment_info = {}
            test_g1 = parse_int(row.get('全年全科测验次数_一年级'))
            if test_g1 is not None:
                assessment_info['test_count_grade1'] = test_g1
            exam_g1 = parse_int(row.get('全年全科考试次数_一年级'))
            if exam_g1 is not None:
                assessment_info['exam_count_grade1'] = exam_g1
            test_g26 = parse_int(row.get('全年全科测验次数_二至六年级'))
            if test_g26 is not None:
                assessment_info['test_count_grade2_6'] = test_g26
            exam_g26 = parse_int(row.get('全年全科考试次数_二至六年级'))
            if exam_g26 is not None:
                assessment_info['exam_count_grade2_6'] = exam_g26
            
            # 构建中学联系信息 JSON
            secondary_info = {}
            through_train = clean_value(row.get('一条龙中学'))
            if through_train:
                secondary_info['through_train'] = through_train
            direct = clean_value(row.get('直属中学'))
            if direct:
                secondary_info['direct'] = direct
            associated = clean_value(row.get('联系中学'))
            if associated:
                secondary_info['associated'] = associated
            
            # 构建更新数据
            update_data = {
                'district': clean_value(row.get('区域') or row.get('區域')),
                'address': clean_value(row.get('学校地址') or row.get('學校地址')),
                'school_net': clean_value(row.get('小一学校网') or row.get('小一學校網')),
                'phone': clean_value(row.get('学校电话') or row.get('學校電話')),
                'email': clean_value(row.get('学校电邮') or row.get('學校電郵')),
                'website': clean_value(row.get('学校网址') or row.get('學校網址')),
                'school_category': clean_value(row.get('学校类别1') or row.get('學校類別1')),
                'school_category_2': clean_value(row.get('学校类别2') or row.get('學校類別2')),
                'student_gender': clean_value(row.get('学生性别') or row.get('學生性別')),
                'school_sponsor': clean_value(row.get('办学团体') or row.get('辦學團體')),
                'founded_year': clean_value(row.get('创校年份') or row.get('創校年份')),
                'religion': clean_value(row.get('宗教')),
                'school_motto': clean_value(row.get('校训') or row.get('校訓')),
                'school_area': clean_value(row.get('学校占地面积') or row.get('學校佔地面積')),
                'teaching_language': clean_value(row.get('教学语言') or row.get('教學語言')),
                'school_bus': clean_value(row.get('校车') or row.get('校車')),
                'nanny_bus': clean_value(row.get('保姆车') or row.get('保姆車')),
                'tuition': clean_value(row.get('学费') or row.get('學費')),
                'classroom_count': parse_int(row.get('课室数目') or row.get('課室數目')),
                'hall_count': parse_int(row.get('礼堂数目') or row.get('禮堂數目')),
                'playground_count': parse_int(row.get('操场数目') or row.get('操場數目')),
                'library_count': parse_int(row.get('图书馆数目') or row.get('圖書館數目')),
                'special_rooms': clean_value(row.get('特别室') or row.get('特別室')),
                'teacher_count': parse_int(row.get('上学年教师总人数') or row.get('上學年教師總人數')),
                'total_classes': parse_int(row.get('本学年总班数') or row.get('本學年總班數')),
                'class_teaching_mode': clean_value(row.get('班级教学模式') or row.get('班級教學模式')),
                'multi_assessment': clean_value(row.get('多元学习评估') or row.get('多元學習評估')),
                'class_arrangement': clean_value(row.get('分班安排')),
                'lunch_arrangement': clean_value(row.get('午膳安排')),
                'school_life_notes': clean_value(row.get('学校生活备注') or row.get('學校生活備註')),
                'whole_person_learning': clean_value(row.get('全方位学习') or row.get('全方位學習')),
                'school_mission': clean_value(row.get('办学宗旨') or row.get('辦學宗旨')),
                'diversity_support': clean_value(row.get('全校参与照顾学生的多样性') or row.get('全校參與照顧學生的多樣性')),
            }
            
            # 添加 JSON 字段
            if teacher_info:
                update_data['teacher_info'] = teacher_info
            if classes_by_grade:
                update_data['classes_by_grade'] = classes_by_grade
            if assessment_info:
                update_data['assessment_info'] = assessment_info
            if secondary_info:
                update_data['secondary_info'] = secondary_info
            
            # 移除 None 值
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if existing_school:
                # 更新现有记录
                for key, value in update_data.items():
                    setattr(existing_school, key, value)
                # 同时保存繁体名称
                existing_school.school_name_traditional = school_name_traditional
                existing_school.save()
                updated_count += 1
                if updated_count <= 5:
                    print(f"✅ 更新学校: {school_name_traditional}")
            elif create_if_not_exists:
                # 创建新记录
                update_data['school_name'] = school_name_simplified
                update_data['school_name_traditional'] = school_name_traditional
                TbPrimarySchools.objects.create(**update_data)
                created_count += 1
                if created_count <= 5:
                    print(f"➕ 创建学校: {school_name_traditional}")
            else:
                not_found_count += 1
                not_found_schools.append(f"{school_name_traditional} -> {school_name_simplified}")
                if not_found_count <= 10:
                    print(f"⚠️  未找到学校: {school_name_traditional} (简体: {school_name_simplified})")
                    
        except Exception as e:
            error_count += 1
            print(f"❌ 第 {index + 2} 行处理失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"导入完成!")
    print(f"  更新: {updated_count} 条")
    print(f"  创建: {created_count} 条")
    print(f"  未找到: {not_found_count} 条")
    print(f"  错误: {error_count} 条")
    
    if not_found_schools and len(not_found_schools) <= 50:
        print(f"\n未找到的学校列表:")
        for school in not_found_schools:
            print(f"  - {school}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='导入小学详情数据')
    parser.add_argument('excel_file', nargs='?', default='common/data/小学数据.xlsx',
                        help='Excel 文件路径 (默认: common/data/小学数据.xlsx)')
    parser.add_argument('--create', action='store_true',
                        help='如果学校不存在则创建新记录')
    
    args = parser.parse_args()
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(args.excel_file):
        excel_path = os.path.join(os.path.dirname(script_dir), args.excel_file.replace('common/', ''))
        if not os.path.exists(excel_path):
            excel_path = os.path.join(script_dir, os.path.basename(args.excel_file))
    else:
        excel_path = args.excel_file
    
    if not os.path.exists(excel_path):
        print(f"错误: 文件不存在 - {excel_path}")
        print(f"请将 Excel 文件放到 {script_dir} 目录下")
        sys.exit(1)
    
    import_primary_school_details(excel_path, create_if_not_exists=args.create)
