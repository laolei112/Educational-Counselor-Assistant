#!/usr/bin/env python3
"""
解析升学描述性文本，提取结构化数据

示例输入：
- "约85%学生可升入直属中学圣保罗书院（Band 1A）"
- "约85%学生升入直属中学嘉诺撒圣心书院（Band 1B）"
- "约64%升入直属中学慈幼英文学校（Band 2B）"

输出结构化数据：
{
    "text": "原始文本",
    "parsed": {
        "rate": 85,
        "rate_type": "约",
        "school_name": "圣保罗书院",
        "relationship": "直属",
        "band": "1A"
    }
}
"""

import re
from typing import Dict, List, Optional, Union


def parse_promotion_description(text: str) -> Dict:
    """
    解析单条升学描述文本
    
    Args:
        text: 描述文本，如 "约85%学生可升入直属中学圣保罗书院（Band 1A）"
    
    Returns:
        包含原始文本和解析结果的字典
    """
    if not text or not isinstance(text, str):
        return {"text": text, "parsed": None}
    
    result = {
        "text": text,
        "parsed": {
            "rate": None,
            "rate_type": None,
            "school_name": None,
            "relationship": None,
            "band": None
        }
    }
    
    # 提取百分比
    rate_pattern = r'([约大约]?)(\d+(?:\.\d+)?)%'
    rate_match = re.search(rate_pattern, text)
    if rate_match:
        rate_type = rate_match.group(1) or "精确"
        rate_value = float(rate_match.group(2))
        result["parsed"]["rate"] = rate_value
        result["parsed"]["rate_type"] = rate_type if rate_type else "精确"
    
    # 提取关系类型（直属/联系/一条龙）
    relationship_pattern = r'(直属|联系|一条龙)'
    relationship_match = re.search(relationship_pattern, text)
    if relationship_match:
        result["parsed"]["relationship"] = relationship_match.group(1)
    
    # 提取Band等级
    band_pattern = r'Band\s*(\d+[A-C]?)'
    band_match = re.search(band_pattern, text, re.IGNORECASE)
    if band_match:
        result["parsed"]["band"] = band_match.group(1).upper()
    
    # 提取学校名称（在"中学"之后，括号之前）
    # 模式1: "升入直属中学圣保罗书院（Band 1A）"
    # 模式2: "升入联系中学XXX"
    school_pattern1 = r'(?:升入|可升入)(?:直属|联系|一条龙)?中学([^（(]+?)(?:（|\(|$)'
    school_match1 = re.search(school_pattern1, text)
    if school_match1:
        school_name = school_match1.group(1).strip()
        # 清理可能的标点符号
        school_name = re.sub(r'[，,。.]$', '', school_name)
        result["parsed"]["school_name"] = school_name
    
    # 如果还没找到学校名，尝试更宽泛的模式
    if not result["parsed"]["school_name"]:
        # 查找"中学"后面的内容
        school_pattern2 = r'中学([^（(]+?)(?:（|\(|$)'
        school_match2 = re.search(school_pattern2, text)
        if school_match2:
            school_name = school_match2.group(1).strip()
            school_name = re.sub(r'[，,。.]$', '', school_name)
            result["parsed"]["school_name"] = school_name
    
    return result


def parse_promotion_descriptions(texts: List[str]) -> List[Dict]:
    """
    批量解析升学描述文本
    
    Args:
        texts: 描述文本列表
    
    Returns:
        解析结果列表
    """
    return [parse_promotion_description(text) for text in texts]


def format_promotion_descriptions_for_db(texts: List[str], include_parsed: bool = True) -> List[Union[str, Dict]]:
    """
    格式化描述文本为数据库存储格式
    
    Args:
        texts: 原始描述文本列表
        include_parsed: 是否包含解析后的结构化数据
    
    Returns:
        格式化后的列表，每个元素可以是字符串或包含解析数据的字典
    """
    if not include_parsed:
        return texts
    
    return parse_promotion_descriptions(texts)


# 示例使用
if __name__ == "__main__":
    test_texts = [
        "约85%学生可升入直属中学圣保罗书院（Band 1A）",
        "约85%学生升入直属中学嘉诺撒圣心书院（Band 1B）",
        "约85%学生升入直属中学圣士提反女子中学（Band 1A）",
        "约85%学生升入直属中学圣嘉勒女书院（Band 1B）",
        "约64%升入直属中学慈幼英文学校（Band 2B）",
        "约85%学生升入直属中学圣罗撒书院（Band 1B）"
    ]
    
    results = parse_promotion_descriptions(test_texts)
    
    print("解析结果：")
    print("=" * 80)
    for result in results:
        print(f"\n原始文本: {result['text']}")
        if result['parsed']:
            parsed = result['parsed']
            print(f"  百分比: {parsed['rate']}% ({parsed['rate_type']})")
            print(f"  学校名: {parsed['school_name']}")
            print(f"  关系: {parsed['relationship']}")
            print(f"  Band: {parsed['band']}")

