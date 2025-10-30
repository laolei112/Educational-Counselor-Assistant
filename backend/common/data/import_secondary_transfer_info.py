#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 `中学插班开放时间.xlsx` 导入中学插班与课程体系信息到数据库。

规则：
1) 将 Excel 中的【课程体系】写入 `TbSecondarySchools.school_curriculum`（以 JSON 字符串形式保存）。
   - 结构示例：{"课程体系": ["DSE", "IB"]} 或 {"课程体系": "DSE"}
2) 将以下字段写入 `TbSecondarySchools.transfer_info`（JSON 字段）：
   - S1入学申请开始时间
   - S1入学申请截至时间
   - S1申请详情地址
   - S2以上插班申请开始时间
   - S2以上插班申请截止时间
   - S2以上可插班年级
   - S2以上插班详情链接
3) 学校匹配：使用 Excel 的【学校名称】精确匹配 `TbSecondarySchools.school_name`。

用法：
    cd backend
    python common/data/import_secondary_transfer_info.py [可选: Excel绝对路径]
若未提供路径，则默认读取同目录下的 `中学插班开放时间.xlsx`。
"""

import os
import sys
import json
import django
import pandas as pd


# 追加项目根目录到 sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_secondary_schools import TbSecondarySchools  # noqa: E402


def clean_value(v):
    """将 NaN/None 转为空字符串，去除首尾空白。"""
    if pd.isna(v):
        return ""
    s = str(v).strip()
    # 将明显的占位如 'nan'、'None' 等也视为空
    if s.lower() in {"nan", "none", "null"}:
        return ""
    return s


def parse_curriculum(value):
    """解析【课程体系】列，输出 JSON 可序列化的对象。

    - 若包含常见分隔符（、/，,；;、空格），拆分为去重后的列表；
    - 否则以字符串原样保存。
    """
    text = clean_value(value)
    if not text:
        return None

    return {"课程体系": text}


def build_transfer_info(row):
    """从行构建 transfer_info 字典。空值字段将省略。"""
    s1 = {
        "入学申请开始时间": clean_value(row.get("S1入学申请开始时间")),
        "入学申请截至时间": clean_value(row.get("S1入学申请截至时间")),
        "申请详情地址": clean_value(row.get("S1申请详情地址")),
    }
    s2_plus = {
        "插班申请开始时间": clean_value(row.get("S2以上插班申请开始时间")),
        "插班申请截止时间": clean_value(row.get("S2以上插班申请截止时间")),
        "可插班年级": clean_value(row.get("S2以上可插班年级")),
        "插班详情链接": clean_value(row.get("S2以上插班详情链接")),
    }

    # 去除空字段
    s1 = {k: v for k, v in s1.items() if v}
    s2_plus = {k: v for k, v in s2_plus.items() if v}

    transfer_info = {}
    if s1:
        transfer_info["S1"] = s1
    if s2_plus:
        transfer_info["S2及以上"] = s2_plus

    return transfer_info or None


def import_from_excel(excel_path):
    print(f"正在读取 Excel 文件: {excel_path}")
    df = pd.read_excel(excel_path)

    required_cols = [
        "学校名称",
        "课程体系",
        "S1入学申请开始时间",
        "S1入学申请截至时间",
        "S1申请详情地址",
        "S2以上插班申请开始时间",
        "S2以上插班申请截止时间",
        "S2以上可插班年级",
        "S2以上插班详情链接",
    ]
    for col in ["学校名称"]:
        if col not in df.columns:
            raise ValueError(f"Excel 缺少必需列: {col}")

    update_count = 0
    not_found = 0
    error_count = 0

    for idx, row in df.iterrows():
        school_name = clean_value(row.get("学校名称"))
        if not school_name:
            print(f"第 {idx + 1} 行: 学校名称为空，跳过")
            continue

        curriculum_obj = parse_curriculum(row.get("课程体系"))
        transfer_info_obj = build_transfer_info(row)

        try:
            school = TbSecondarySchools.objects.filter(school_name=school_name).first()
            if not school:
                not_found += 1
                print(f"❌ 未找到学校: {school_name}")
                continue

            # 更新 school_curriculum（存为 JSON 字符串）
            if curriculum_obj is not None:
                db_school_curriculum = school.school_curriculum
                if db_school_curriculum is not None:
                    db_school_curriculum = json.loads(db_school_curriculum)
                    db_school_curriculum["课程体系"] = curriculum_obj["课程体系"]
                    school.school_curriculum = json.dumps(db_school_curriculum, ensure_ascii=False)
                else:
                    school.school_curriculum = json.dumps(curriculum_obj, ensure_ascii=False)

            # 更新 transfer_info（JSON 字段，直接存对象）
            if transfer_info_obj is not None:
                # 合并已有信息（如存在）
                if school.transfer_info and isinstance(school.transfer_info, dict):
                    merged = dict(school.transfer_info)
                    merged.update(transfer_info_obj)
                    school.transfer_info = merged
                else:
                    school.transfer_info = transfer_info_obj

            school.save()
            update_count += 1
        except Exception as e:
            error_count += 1
            print(f"❌ 更新失败: {school_name} - {str(e)}")

    print("\n" + "=" * 60)
    print("导入完成")
    print("=" * 60)
    print(f"成功更新: {update_count}")
    print(f"未找到: {not_found}")
    print(f"错误: {error_count}")


def main():
    # 默认读取当前目录下文件
    default_path = os.path.join(os.path.dirname(__file__), "中学插班开放时间.xlsx")
    excel_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    if not os.path.isabs(excel_path):
        # 允许相对路径（相对 backend/ 工作目录）
        excel_path = os.path.abspath(excel_path)

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"未找到 Excel 文件: {excel_path}")

    import_from_excel(excel_path)


if __name__ == "__main__":
    main()


