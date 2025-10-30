#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 Excel 文件为小学表新增/更新 total_classes 字段。

来源：backend/common/data/2025年小学概览-估算小六学生人数.xlsx
取列：【小六学生人数（估算）2025届毕业】
匹配：按【学校名称】匹配 TbPrimarySchools.school_name（精确匹配）

用法：
  cd backend
  python common/data/update_primary_total_classes.py [可选: Excel绝对路径]
"""

import os
import sys
import django
import pandas as pd


# 将项目根目录加入路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.models.tb_primary_schools import TbPrimarySchools  # noqa: E402


EXCEL_DEFAULT = os.path.join(
    os.path.dirname(__file__),
    '2025年小学概览-估算小六学生人数.xlsx'
)

COLUMN_NAME_SCHOOL = '学校名称'
COLUMN_NAME_VALUE = '本学年总班数'


def to_int_or_none(v):
    if pd.isna(v):
        return None
    try:
        s = str(v).strip().replace(',', '')
        if s == '':
            return None
        return int(float(s))
    except Exception:
        return None


def main():
    excel_path = sys.argv[1] if len(sys.argv) > 1 else EXCEL_DEFAULT
    if not os.path.isabs(excel_path):
        excel_path = os.path.abspath(excel_path)
    if not os.path.exists(excel_path):
        print(f"未找到Excel: {excel_path}")
        sys.exit(1)

    print(f"读取: {excel_path}")
    df = pd.read_excel(excel_path)
    if COLUMN_NAME_SCHOOL not in df.columns or COLUMN_NAME_VALUE not in df.columns:
        print(f"Excel 缺少列: {COLUMN_NAME_SCHOOL} 或 {COLUMN_NAME_VALUE}")
        sys.exit(1)

    updated, not_found, skipped = 0, 0, 0
    for _, row in df.iterrows():
        school_name = str(row.get(COLUMN_NAME_SCHOOL) or '').strip()
        if not school_name:
            skipped += 1
            continue

        value = to_int_or_none(row.get(COLUMN_NAME_VALUE))
        if value is None:
            skipped += 1
            continue

        school = TbPrimarySchools.objects.filter(school_name=school_name).first()
        if not school:
            not_found += 1
            continue

        school.total_classes = value
        school.save(update_fields=['total_classes'])
        updated += 1

    print("\n=== 更新完成 ===")
    print(f"成功更新: {updated}")
    print(f"未找到学校: {not_found}")
    print(f"跳过(无效/空值): {skipped}")


if __name__ == '__main__':
    main()


