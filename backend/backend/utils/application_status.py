"""
申请状态计算工具函数
用于计算学校申请开放状态，与前端逻辑保持一致
"""
from datetime import datetime, date, timedelta
import re
from typing import Optional, Dict, Any
from common.logger import loginfo


def get_utc8_now() -> datetime:
    """
    获取 UTC+8 时区的当前时间
    """
    utc_now = datetime.utcnow()
    delta = timedelta(hours=8)
    return utc_now + delta


def parse_date_string(date_str: str) -> Optional[date]:
    """
    解析日期字符串，支持多种格式
    与前端 parseDate 函数保持一致
    
    支持的格式：
    - 2025-01-02
    - 2025-01-02 00:00:00 (带时间部分)
    - 2025.1.2
    - 2025/1/2
    - 2025年1月2日
    - 20250102
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    if not date_str:
        return None
    
    # 🔥 格式1: 2025-01-02 或 2025-01-02 00:00:00 (带时间部分)
    # 先尝试匹配带时间部分的格式
    match = re.match(r'^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})(?:\s+\d{1,2}:\d{1,2}:\d{1,2})?$', date_str)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return date(year, month, day)
        except ValueError:
            pass
    
    # 格式2: 2025.1.2
    match = re.match(r'^(\d{4})\.(\d{1,2})\.(\d{1,2})(?:\s+\d{1,2}:\d{1,2}:\d{1,2})?$', date_str)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return date(year, month, day)
        except ValueError:
            pass
    
    # 格式3: 2025年1月2日
    match = re.match(r'^(\d{4})年(\d{1,2})月(\d{1,2})日$', date_str)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return date(year, month, day)
        except ValueError:
            pass
    
    # 格式4: 20250102
    match = re.match(r'^(\d{4})(\d{2})(\d{2})$', date_str)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return date(year, month, day)
        except ValueError:
            pass
    
    # 🔥 尝试使用 datetime.strptime 解析（兼容更多格式）
    try:
        # 尝试 ISO 格式
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.date()
    except ValueError:
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.date()
        except ValueError:
            pass
    
    return None


def is_text_open_status(text: str) -> bool:
    """
    检查文本是否表示"开放申请"状态
    
    支持的文本：
    - "开放申请"
    - "开放中"
    - "現正接受申請" (繁体)
    - "現正接受申请" (简体)
    """
    if not text or not isinstance(text, str):
        return False
    text_lower = text.lower().strip()
    # 🔥 扩展支持的文本状态
    return ('开放申请' in text_lower or 
            '开放中' in text_lower or
            '現正接受' in text_lower or
            '现正接受' in text_lower or
            '接受申請' in text_lower or
            '接受申请' in text_lower)


def is_text_closed_status(text: str) -> bool:
    """
    检查文本是否表示"未开放"状态
    """
    if not text or not isinstance(text, str):
        return False
    text_lower = text.lower().strip()
    return '未开放' in text_lower or '暂未开放' in text_lower


def parse_month_from_text(text: str) -> Optional[int]:
    """
    从"每年X月X日"格式中解析月份
    返回月份（1-12），如果无法解析返回 None
    """
    if not text or not isinstance(text, str):
        return None
    
    match = re.match(r'^每年(\d{1,2})月', text)
    if match:
        try:
            month = int(match.group(1))
            if 1 <= month <= 12:
                return month
        except ValueError:
            pass
    
    return None


def calculate_s1_p1_status(p1_info: Dict[str, Any]) -> Optional[str]:
    """
    计算小一/S1申请状态
    
    支持字段名：
    - 小一: 小一入学申请开始时间, 小一入学申请截至时间, 小一入学申请截止时间
    - S1: 入学申请开始时间, 入学申请截至时间, 入学申请截止时间
    
    返回: 'open', 'closed', 'deadline' 或 None
    """
    if not p1_info or not isinstance(p1_info, dict):
        return None
    
    now = get_utc8_now()
    today = now.date()
    
    # 获取开始和截止时间（兼容小一和S1的字段名）
    start_str = p1_info.get('小一入学申请开始时间') or p1_info.get('入学申请开始时间')
    end_str = p1_info.get('小一入学申请截至时间') or p1_info.get('小一入学申请截止时间') or \
              p1_info.get('入学申请截至时间') or p1_info.get('入学申请截止时间')
    
    # 检查是否为文本状态
    if start_str and isinstance(start_str, str):
        if is_text_open_status(start_str):
            # 如果有截止时间，检查是否已过期
            if end_str:
                end_date = parse_date_string(end_str)
                if end_date:
                    if today <= end_date:
                        days_left = (end_date - today).days
                        return 'deadline' if days_left <= 7 else 'open'
                    else:
                        return 'closed'
            # 没有截止时间，认为是开放的
            return 'open'
    
    # 解析日期
    start_date = parse_date_string(start_str) if start_str else None
    end_date = parse_date_string(end_str) if end_str else None
    
    # 有开始和截止时间，检查是否在范围内
    if start_date and end_date:
        if start_date <= today <= end_date:
            days_left = (end_date - today).days
            return 'deadline' if days_left <= 7 else 'open'
        elif today < start_date:
            return 'closed'
        else:
            return 'closed'
    
    # 只有开始时间，没有截止时间（90天内认为是开放）
    if start_date and not end_date:
        days_since_start = (today - start_date).days
        if 0 <= days_since_start <= 90:
            return 'open'
        else:
            return 'closed'
    
    return None


def calculate_transfer_status(transfer_info: Dict[str, Any], debug_school_id: Optional[int] = None) -> Optional[str]:
    """
    计算插班申请状态
    
    返回: 'open', 'closed', 'deadline' 或 None
    
    Args:
        transfer_info: 插班信息字典
        debug_school_id: 调试用的学校ID（可选）
    """
    if not transfer_info or not isinstance(transfer_info, dict):
        return None
    
    now = get_utc8_now()
    today = now.date()
    
    # 检查是否明确标记为"未开放"
    start1_str = transfer_info.get('插班申请开始时间1')
    start2_str = transfer_info.get('插班申请开始时间2')
    end1_str = transfer_info.get('插班申请截止时间1')
    end2_str = transfer_info.get('插班申请截止时间2')
    
    # 🔥 调试日志（仅对特定学校）
    if debug_school_id:
        loginfo(
            f"[DEBUG] calculate_transfer_status for school {debug_school_id} | "
            f"start1={start1_str}, end1={end1_str}, start2={start2_str}, end2={end2_str} | "
            f"today={today}"
        )
    
    # 检查文本状态
    if is_text_closed_status(str(start1_str) if start1_str else '') or \
       is_text_closed_status(str(start2_str) if start2_str else '') or \
       is_text_closed_status(str(end1_str) if end1_str else ''):
        return 'closed'
    
    # 检查"开放申请"文本状态
    if start1_str and isinstance(start1_str, str) and is_text_open_status(start1_str):
        if end1_str:
            end1_date = parse_date_string(end1_str)
            if end1_date:
                if today <= end1_date:
                    days_left = (end1_date - today).days
                    return 'deadline' if days_left <= 7 else 'open'
                else:
                    return 'closed'
            # 🔥 如果截止时间无法解析，但有截止时间字符串，尝试其他方式
            # 可能是格式问题，但至少说明有截止时间，需要进一步检查
        # 没有截止时间，认为是开放的
        return 'open'
    
    if start2_str and isinstance(start2_str, str) and is_text_open_status(start2_str):
        if end2_str:
            end2_date = parse_date_string(end2_str)
            if end2_date:
                if today <= end2_date:
                    days_left = (end2_date - today).days
                    return 'deadline' if days_left <= 7 else 'open'
                else:
                    return 'closed'
            # 🔥 如果截止时间无法解析，但有截止时间字符串，尝试其他方式
        # 没有截止时间，认为是开放的
        return 'open'
    
    # 检查"每年X月"格式
    if start1_str and isinstance(start1_str, str) and '每年' in start1_str:
        month = parse_month_from_text(start1_str)
        if month and now.month == month:
            return 'open'
    
    if start2_str and isinstance(start2_str, str) and '每年' in start2_str:
        month = parse_month_from_text(start2_str)
        if month and now.month == month:
            return 'open'
    
    # 解析日期（跳过已经是文本状态的字段）
    start1_date = None
    start2_date = None
    
    # 时间段1：解析开始时间（如果不是文本状态）
    if start1_str and isinstance(start1_str, str):
        if is_text_open_status(start1_str) or '每年' in start1_str:
            # 文本状态已经在上面处理了，跳过
            pass
        else:
            start1_date = parse_date_string(start1_str)
    elif start1_str:
        start1_date = parse_date_string(start1_str)
    
    # 时间段2：解析开始时间（如果不是文本状态）
    if start2_str and isinstance(start2_str, str):
        if is_text_open_status(start2_str) or '每年' in start2_str:
            # 文本状态已经在上面处理了，跳过
            pass
        else:
            start2_date = parse_date_string(start2_str)
    elif start2_str:
        start2_date = parse_date_string(start2_str)
    
    end1_date = parse_date_string(end1_str) if end1_str else None
    end2_date = parse_date_string(end2_str) if end2_str else None
    
    # 检查两个时间段
    statuses = []
    
    # 时间段1
    if start1_date and end1_date:
        # 有开始和截止时间，检查是否在范围内
        if start1_date <= today <= end1_date:
            days_left = (end1_date - today).days
            statuses.append('deadline' if days_left <= 7 else 'open')
        elif today < start1_date:
            statuses.append('closed')
        else:
            statuses.append('closed')
    elif start1_date and not end1_date:
        # 只有开始时间，没有截止时间（90天内认为是开放）
        days_since_start = (today - start1_date).days
        if 0 <= days_since_start <= 90:
            statuses.append('open')
        else:
            statuses.append('closed')
    elif not start1_date and end1_date:
        # 🔥 只有截止时间，没有开始时间（前端不会认为开放，但后端应该检查截止时间）
        # 如果截止时间未过，可能是"开放申请"文本 + 截止时间的格式
        # 这种情况下，如果截止时间未过，应该认为是开放的
        if today <= end1_date:
            days_left = (end1_date - today).days
            statuses.append('deadline' if days_left <= 7 else 'open')
        else:
            statuses.append('closed')
    
    # 时间段2
    if start2_date and end2_date:
        # 有开始和截止时间，检查是否在范围内
        if start2_date <= today <= end2_date:
            days_left = (end2_date - today).days
            statuses.append('deadline' if days_left <= 7 else 'open')
        elif today < start2_date:
            statuses.append('closed')
        else:
            statuses.append('closed')
    elif start2_date and not end2_date:
        # 只有开始时间，没有截止时间（90天内认为是开放）
        days_since_start = (today - start2_date).days
        if 0 <= days_since_start <= 90:
            statuses.append('open')
        else:
            statuses.append('closed')
    elif not start2_date and end2_date:
        # 🔥 只有截止时间，没有开始时间（前端不会认为开放，但后端应该检查截止时间）
        # 如果截止时间未过，可能是"开放申请"文本 + 截止时间的格式
        # 这种情况下，如果截止时间未过，应该认为是开放的
        if today <= end2_date:
            days_left = (end2_date - today).days
            statuses.append('deadline' if days_left <= 7 else 'open')
        else:
            statuses.append('closed')
    
    # 如果有任何一个时间段是开放的，返回开放状态
    if 'open' in statuses:
        return 'open'
    if 'deadline' in statuses:
        return 'deadline'
    if statuses:
        return 'closed'
    
    return None

