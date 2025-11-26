import json
import re
import time
import hashlib
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.cache import cache
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.utils.text_converter import normalize_keyword
from backend.utils.cache import CacheManager
from common.logger import loginfo


def get_band_sort_key(band_str):
    """
    获取 Band 的排序键，用于排序
    返回 (band_number, sub_level)
    - band_number: 1, 2, 3, 999 (数字越小优先级越高，999表示未知)
    - sub_level: 1(A), 2(B), 3(C), 4(无子级别), 999 (子级别越小优先级越高)
    
    排序优先级：Band 1A > Band 1B > Band 1C > Band 1 > Band 2A > ... > 未知
    """
    if not band_str or band_str == '未知':
        return (999, 999)
    
    band_str = str(band_str).strip()
    
    # 提取 Band 数字（更精确的匹配）
    band_number = 999
    # 匹配 "Band 1", "Band 2", "Band 3" 或 "1", "2", "3" 开头
    match = re.search(r'Band\s*(\d)|^(\d)', band_str, re.IGNORECASE)
    if match:
        band_number = int(match.group(1) or match.group(2))
    
    # 提取子级别 (A, B, C) - 更精确的匹配，避免误匹配
    sub_level = 4  # 默认无子级别
    # 匹配 "Band 1A", "Band 1B", "Band 1C" 等格式
    sub_match = re.search(r'Band\s*\d+([ABC])', band_str, re.IGNORECASE)
    if sub_match:
        sub_char = sub_match.group(1).upper()
        if sub_char == 'A':
            sub_level = 1
        elif sub_char == 'B':
            sub_level = 2
        elif sub_char == 'C':
            sub_level = 3
    
    return (band_number, sub_level)


def sort_yearly_stats(promotion_info):
    """
    辅助函数：对 promotion_info 中的 yearly_stats 按年份降序排序
    并对每个年份的 schools 按照 Band 进行排序
    解决 MySQL JSON 字段存储不保证顺序的问题
    """
    if not promotion_info or not isinstance(promotion_info, dict):
        return promotion_info
    
    if 'yearly_stats' in promotion_info and isinstance(promotion_info['yearly_stats'], dict):
        try:
            # 按年份降序排序
            sorted_stats = dict(sorted(promotion_info['yearly_stats'].items(), key=lambda x: x[0], reverse=True))
            
            # 对每个年份的 schools 按照 Band 进行排序
            for year, year_data in sorted_stats.items():
                if isinstance(year_data, dict) and 'schools' in year_data and isinstance(year_data['schools'], dict):
                    schools_dict = year_data['schools']
                    # 转换为列表，按照 Band 排序
                    schools_sorted = sorted(
                        schools_dict.items(),
                        key=lambda x: get_band_sort_key(
                            x[1].get('band', '未知') if isinstance(x[1], dict) else '未知'
                        )
                    )
                    # 转换回字典（Python 3.7+ 字典保持插入顺序）
                    sorted_stats[year]['schools'] = dict(schools_sorted)
            
            # 返回新的字典以避免修改原数据
            new_info = promotion_info.copy()
            new_info['yearly_stats'] = sorted_stats
            loginfo(f"sorted_stats: {sorted_stats}")
            return new_info
        except Exception:
            # 如果排序失败（例如键不是可比较的），返回原数据
            loginfo(f"sorted_stats failed, promotion_info: {promotion_info}")
            return promotion_info
    loginfo(f"promotion_info: {promotion_info}")
    return promotion_info


def get_band1_rate(school):
    """
    获取学校的 Band 1 比例
    如果 promotion_info 中的 band1_rate_null 为 True，返回 None
    否则优先使用 school.band1_rate，如果为 None 则从 promotion_info 中获取
    """
    # 检查 promotion_info 中的 band1_rate_null 标志
    if school.promotion_info and isinstance(school.promotion_info, dict):
        if school.promotion_info.get('band1_rate_null') is True:
            return None
    
    # 优先使用 school.band1_rate
    if school.band1_rate is not None:
        return float(school.band1_rate)
    
    # 如果 school.band1_rate 为 None，尝试从 promotion_info 中获取
    if school.promotion_info and isinstance(school.promotion_info, dict):
        band1_rate = school.promotion_info.get('band1_rate')
        if band1_rate is not None:
            return float(band1_rate)
    
    return None


def serialize_primary_school(school):
    """
    序列化小学数据为前端需要的格式
    优化: 减少方法调用,直接访问属性
    """
    # 优化: 直接从 total_classes_info 获取总班数,优先使用 current_year_total_classes
    total_classes = 0
    if school.total_classes_info and isinstance(school.total_classes_info, dict):
        # 尝试从 current_year_total_classes 获取
        if 'current_year_total_classes' in school.total_classes_info:
            try:
                total_classes = int(school.total_classes_info['current_year_total_classes'])
            except (ValueError, TypeError):
                pass
        
        # 如果没有获取到（为0），则回退到计算所有年级的班级总数
        if total_classes == 0:
            total_classes = sum(
                school.total_classes_info.get(grade, 0) 
                for grade in ['primary_1', 'primary_2', 'primary_3', 'primary_4', 'primary_5', 'primary_6']
                if isinstance(school.total_classes_info.get(grade), (int, float))
            )
    
    # 处理 promotion_info 排序
    promotion_info = sort_yearly_stats(school.promotion_info)
    
    return {
        "id": school.id,
        "name": school.school_name,
        "nameTraditional": school.school_name_traditional,
        "nameEnglish": school.school_name_english,
        "type": "primary",
        "category": school.school_category,
        "district": school.district,
        "schoolNet": school.school_net,
        "gender": school.student_gender,
        "religion": school.religion,
        "teachingLanguage": school.teaching_language,
        
        # 学费信息
        "tuition": school.tuition if school.tuition else "-",
        
        # 联系方式
        "contact": {
            "address": school.address,
            "phone": school.phone,
            "fax": school.fax,
            "email": school.email,
            "website": school.website
        },
        
        # 基础信息
        "basicInfo": school.school_basic_info if school.school_basic_info else {},
        
        # 中学联系信息
        "secondaryInfo": school.secondary_info if school.secondary_info else {},
        
        # 班级信息
        "schoolScale": {
            "classes": total_classes,
            "students": 0
        },
        "classesInfo": school.total_classes_info if school.total_classes_info else {},
        
        # 教学信息
        "classTeachingInfo": school.class_teaching_info if school.class_teaching_info else {},
        
        # 评估信息
        "assessmentInfo": school.assessment_info if school.assessment_info else {},
        # 插班信息
        "transferInfo": school.transfer_info if school.transfer_info else {},
        # 升学信息
        "promotionInfo": promotion_info if promotion_info else {},
        # Band1比例
        "band1Rate": get_band1_rate(school),
        # 其他
        "isFullDay": school.is_full_day(),
        "isCoed": school.is_coed(),
        
        # 时间戳
        "createdAt": school.created_at.isoformat() if school.created_at else None,
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None
    }


def get_cache_key_for_query(params):
    """
    根据查询参数生成缓存键
    """
    # 将参数字典转换为排序后的字符串,确保相同参数生成相同的键
    param_str = json.dumps(params, sort_keys=True)
    hash_value = hashlib.md5(param_str.encode()).hexdigest()
    return f"primary_schools_count:{hash_value}"


def serialize_primary_school_for_list(school):
    """
    列表页精简序列化 - 只返回卡片展示必需的字段
    
    卡片显示内容：
    - 基本信息：名称、类型、地区、校网、宗教、性别、学费
    - Band1比例：band1Rate (生成列)
    - 联系中学：secondaryInfo (结龙、直属、联系中学)
    - 申请状态：transferInfo (用于显示申请状态徽章)
    
    不包含详情页专用字段：
    - basicInfo (学校介绍)
    - classesInfo (班级详情)
    - classTeachingInfo (教学模式)
    - assessmentInfo (评估政策)
    - promotionInfo (升学详情JSON，band1_rate已提取为生成列)
    """
    # 使用统一的函数获取 band1_rate（会检查 band1_rate_null 标志）
    band1_rate = get_band1_rate(school)
    
    return {
        # 基本信息
        "id": school.id,
        "name": school.school_name,
        "nameTraditional": school.school_name_traditional,
        "nameEnglish": school.school_name_english,
        "type": "primary",
        "category": school.school_category,
        "district": school.district,
        "schoolNet": school.school_net,
        "gender": school.student_gender,
        "religion": school.religion,
        "tuition": school.tuition or "-",
        
        # 卡片显示：Band1比例（生成列，前端使用 school.band1Rate）
        "band1Rate": band1_rate,
        
        # 卡片显示：联系中学信息（结龙、直属、联系中学）
        "secondaryInfo": school.secondary_info or {},
        
        # 卡片需要：申请状态信息
        "transferInfo": school.transfer_info if school.transfer_info else {},
    }


def serialize_primary_school_optimized(school):
    """
    详情页完整序列化 - 返回所有字段
    用于详情接口 /api/schools/primary/{id}/
    """
    # 预先获取 JSON 字段,避免多次访问
    total_classes_info = school.total_classes_info or {}
    # 排序 yearly_stats
    promotion_info = sort_yearly_stats(school.promotion_info or {})
    
    # 快速计算总班数(避免方法调用)
    total_classes = 0
    if isinstance(total_classes_info, dict):
        # 优先使用 current_year_total_classes
        if 'current_year_total_classes' in total_classes_info:
            try:
                total_classes = int(total_classes_info['current_year_total_classes'])
            except (ValueError, TypeError):
                pass
        
        # 如果没有获取到（为0），则回退到计算所有年级的班级总数
        if total_classes == 0:
            for grade in ('primary_1', 'primary_2', 'primary_3', 'primary_4', 'primary_5', 'primary_6'):
                val = total_classes_info.get(grade, 0)
                if isinstance(val, (int, float)):
                    total_classes += val
    
    # 使用统一的函数获取 band1_rate（会检查 band1_rate_null 标志）
    band1_rate = get_band1_rate(school)
    
    return {
        "id": school.id,
        "name": school.school_name,
        "nameTraditional": school.school_name_traditional,
        "nameEnglish": school.school_name_english,
        "type": "primary",
        "category": school.school_category,
        "district": school.district,
        "schoolNet": school.school_net,
        "gender": school.student_gender,
        "religion": school.religion,
        "teachingLanguage": school.teaching_language,
        "tuition": school.tuition or "-",
        "contact": {
            "address": school.address,
            "phone": school.phone,
            "fax": school.fax,
            "email": school.email,
            "website": school.website
        },
        "basicInfo": school.school_basic_info or {},
        "secondaryInfo": school.secondary_info or {},
        "schoolScale": {
            "classes": total_classes,
            "students": 0
        },
        "classesInfo": total_classes_info,
        "classTeachingInfo": school.class_teaching_info or {},
        "assessmentInfo": school.assessment_info or {},
        "transferInfo": school.transfer_info or {},
        "promotionInfo": promotion_info,
        "band1Rate": band1_rate,
        "isFullDay": school.is_full_day(),
        "isCoed": school.is_coed(),
        "createdAt": school.created_at.isoformat() if school.created_at else None,
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None
    }


@csrf_exempt
@require_http_methods(["GET"])
def primary_schools_list(request):
    """
    获取小学列表 - 优化版(带缓存)
    
    核心优化:
    1. 🔥 使用缓存提升响应速度
    2. 🔥 分离 COUNT 和数据查询,COUNT 时不带 ORDER BY
    3. 🔥 使用 only() 减少查询字段(如果不需要所有字段)
    4. 🔥 优化关键字搜索逻辑
    5. 提前验证分页参数,避免无效查询
    """
    start_time = time.time()
    step_times = {}
    step_start = time.time()
    
    try:
        # 获取并验证查询参数
        category = request.GET.get('category')
        district = request.GET.get('district')
        school_net = request.GET.get('schoolNet')
        gender = request.GET.get('gender')
        religion = request.GET.get('religion')
        teaching_language = request.GET.get('teachingLanguage')
        keyword = request.GET.get('keyword')
        
        # 验证分页参数
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('pageSize', 20))
            if page < 1 or page_size < 1 or page_size > 100:
                raise ValueError("Invalid pagination parameters")
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        step_times['param_parse'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 🔥 缓存优化: 基于查询参数生成缓存键
        cache_params = {
            'category': category,
            'district': district,
            'school_net': school_net,
            'gender': gender,
            'religion': religion,
            'teaching_language': teaching_language,
            'keyword': keyword,
            'page': page,
            'page_size': page_size
        }
        cache_key = get_cache_key_for_query(cache_params)
        
        # 尝试从缓存获取数据
        cached_data = cache.get(cache_key)
        if cached_data:
            total_time = (time.time() - start_time) * 1000
            
            # 兼容两种缓存格式：
            # 1. warmup_cache 格式：直接是 data 部分 {'list': ..., 'total': ...}
            # 2. API 格式：完整的响应格式 {'code': 200, 'data': {...}}
            if 'data' in cached_data:
                # API 格式，直接返回
                result_data = cached_data
                data_part = cached_data['data']
            else:
                # warmup_cache 格式，需要包装成完整响应格式
                result_data = {
                    "code": 200,
                    "message": "成功",
                    "success": True,
                    "data": cached_data
                }
                data_part = cached_data
            
            loginfo(
                f"[PERF] GET /api/schools/primary/ (from-cache) | "
                f"Total: {total_time:.2f}ms | "
                f"Result: total={data_part.get('total', 0)}, page={data_part.get('page', page)}, pageSize={data_part.get('pageSize', page_size)}, items={len(data_part.get('list', []))}"
            )
            return JsonResponse(result_data)
        
        step_times['cache_check'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 🔥 优化1: 构建基础过滤条件 (不包含 ORDER BY)
        base_filters = Q()
        
        if category:
            base_filters &= Q(school_category=category)
        if district:
            base_filters &= Q(district=district)
        if school_net:
            base_filters &= Q(school_net=school_net)
        if gender:
            base_filters &= Q(student_gender=gender)
        if religion:
            base_filters &= Q(religion=religion)
        if teaching_language:
            base_filters &= Q(teaching_language__icontains=teaching_language)
        
        # 处理关键字搜索
        if keyword:
            normalized_keyword = normalize_keyword(keyword)
            # 🔥 优化2: 简化关键字搜索 - 避免重复的 icontains
            # 如果标准化后与原始关键字相同,就不需要重复搜索
            if normalized_keyword == keyword:
                keyword_filter = (
                    Q(school_name__icontains=keyword) |
                    Q(school_name_traditional__icontains=keyword) |
                    Q(school_name_english__icontains=keyword)
                )
            else:
                # 只有在标准化后不同时,才需要搜索两次
                keyword_filter = (
                    Q(school_name__icontains=normalized_keyword) | 
                    Q(school_name__icontains=keyword) |
                    Q(school_name_traditional__icontains=normalized_keyword) |
                    Q(school_name_traditional__icontains=keyword) |
                    Q(school_name_english__icontains=keyword)
                )
            base_filters &= keyword_filter
        
        step_times['query_build'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 🔥 优化3: 分离 COUNT 查询 (不带 ORDER BY)
        # COUNT 查询使用最简单的形式,数据库可以直接使用索引
        count_queryset = TbPrimarySchools.objects.filter(base_filters)
        total = count_queryset.count()
        
        step_times['count_query'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 提前计算分页信息
        if total == 0:
            # 🔥 优化4: 无数据时直接返回,避免后续查询
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": {
                    "list": [],
                    "total": 0,
                    "page": page,
                    "pageSize": page_size,
                    "totalPages": 0
                }
            })
        
        total_pages = (total + page_size - 1) // page_size
        
        # 🔥 优化5: 验证页码是否超出范围
        if page > total_pages:
            page = total_pages
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 🔥 优化6: 数据查询时才添加 ORDER BY
        # 分离排序逻辑,确保 COUNT 时不受影响
        data_queryset = TbPrimarySchools.objects.filter(base_filters).order_by(
            '-band1_rate',  # 使用生成列,有索引
            'school_name'
        )
        
        # 列表页只查询卡片必需字段（减少数据库I/O和网络传输）
        data_queryset = data_queryset.only(
            # 基本字段（11个）
            'id', 'school_name', 'school_name_traditional', 'school_name_english',
            'school_category', 'district', 'school_net', 'student_gender',
            'religion', 'tuition', 'band1_rate',
            # 卡片需要的JSON字段（2个）
            'secondary_info',   # 联系中学信息
            'transfer_info'     # 申请状态
        )
        
        # 使用切片获取当前页数据
        schools_page = data_queryset[start_index:end_index]
        
        step_times['data_query'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 使用精简序列化（只返回卡片必需字段）
        schools_data = [serialize_primary_school_for_list(school) for school in schools_page]
        
        step_times['serialize'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "list": schools_data,
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages
            }
        }
        
        step_times['response_build'] = (time.time() - step_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        # 🔥 缓存结果数据（10分钟）
        cache.set(cache_key, response_data, 600)
        
        # 记录性能日志
        loginfo(
            f"[PERF] GET /api/schools/primary/ (query-optimized) | "
            f"Total: {total_time:.2f}ms | "
            f"ParamParse: {step_times.get('param_parse', 0):.2f}ms | "
            f"CacheCheck: {step_times.get('cache_check', 0):.2f}ms | "
            f"QueryBuild: {step_times.get('query_build', 0):.2f}ms | "
            f"CountQuery: {step_times.get('count_query', 0):.2f}ms | "
            f"DataQuery: {step_times.get('data_query', 0):.2f}ms | "
            f"Serialize: {step_times.get('serialize', 0):.2f}ms | "
            f"ResponseBuild: {step_times.get('response_build', 0):.2f}ms | "
            f"Result: total={total}, page={page}, pageSize={page_size}, items={len(schools_data)}"
        )
        
        return JsonResponse(response_data)
        
    except ValueError as e:
        total_time = (time.time() - start_time) * 1000
        loginfo(f"[PERF] GET /api/schools/primary/ (query-optimized) - ERROR (ValueError) | Total: {total_time:.2f}ms | Error: {traceback.format_exc()}")
        return JsonResponse({
            "code": 400,
            "message": f"参数错误: {str(e)}",
            "success": False,
            "data": None
        })
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        loginfo(f"[PERF] GET /api/schools/primary/ (query-optimized) - ERROR | Total: {total_time:.2f}ms | Error: {traceback.format_exc()}")
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def primary_school_detail(request, school_id):
    """
    获取小学详情
    GET /api/schools/primary/{id}/
    """
    try:
        school_id = int(school_id)
        
        # 🔥 优化: 添加缓存
        cache_key = f"primary_school_detail:{school_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": cached_data
            })
        
        try:
            school = TbPrimarySchools.objects.get(id=school_id)
        except TbPrimarySchools.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
        
        # 序列化学校数据
        school_data = serialize_primary_school(school)
        
        # 缓存30分钟
        cache.set(cache_key, school_data, 1800)
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": school_data
        })
        
    except ValueError:
        return JsonResponse({
            "code": 400,
            "message": "无效的学校ID",
            "success": False,
            "data": None
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def primary_school_recommendations(request, school_id):
    """
    获取小学推荐列表（同区学校、热门学校）
    GET /api/schools/primary/{id}/recommendations/
    """
    try:
        school_id = int(school_id)
        
        # 缓存优化
        cache_key = f"primary_school_recommendations:{school_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": cached_data
            })
            
        try:
            current_school = TbPrimarySchools.objects.get(id=school_id)
        except TbPrimarySchools.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
            
        # 1. 同区推荐 (Same District) - 随机取4个
        related_schools = TbPrimarySchools.objects.filter(
            district=current_school.district
        ).exclude(id=school_id).order_by('?')[:4]
        
        # 2. 热门推荐 (Popular/High Banding) - 取全港Band1率最高的4个
        # 注意：band1_rate 是生成列，可能为 None
        popular_schools = TbPrimarySchools.objects.exclude(
            id=school_id
        ).exclude(
            id__in=[s.id for s in related_schools]
        ).order_by('-band1_rate')[:4]
        
        # 序列化函数 (精简版)
        def serialize_simple(school):
            return {
                "id": school.id,
                "name": school.school_name,
                "type": "primary",
                "district": school.district,
                "category": school.school_category,
                "tuition": school.tuition or "-",
                "band1Rate": get_band1_rate(school)
            }
            
        data = {
            "related": [serialize_simple(s) for s in related_schools],
            "popular": [serialize_simple(s) for s in popular_schools]
        }
        
        # 缓存 6 小时
        cache.set(cache_key, data, 21600)
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def primary_schools_stats(request):
    """
    获取小学统计信息(简化版本,只返回学校总数)
    GET /api/schools/primary/stats/
    """
    try:
        # 🔥 优化: 使用缓存
        cache_key = "primary_schools_total_count"
        total_schools = cache.get(cache_key)
        
        if total_schools is None:
            total_schools = TbPrimarySchools.objects.count()
            # 缓存1天 (总数变化不频繁)
            cache.set(cache_key, total_schools, 60 * 60 * 24)
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total_schools,
                "openApplications": 0
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def primary_schools_filters(request):
    """
    获取小学筛选选项
    GET /api/schools/primary/filters/
    
    性能优化:
    1. 使用单次查询获取所有字段,减少数据库查询次数(从5次减少到1次)
    2. 在Python中处理去重和排序,避免多次数据库扫描
    3. 添加缓存
    """
    try:
        # 🔥 优化: 添加缓存
        cache_key = "primary_schools_filters"
        cached_filters = cache.get(cache_key)
        
        if cached_filters:
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": cached_filters
            })
        
        # 使用单次查询获取所有需要的字段
        all_data = TbPrimarySchools.objects.values(
            'district', 
            'school_category', 
            'school_net', 
            'student_gender', 
            'religion'
        ).distinct()
        
        # 在Python中处理去重和排序
        districts_set = set()
        categories_set = set()
        school_nets_set = set()
        genders_set = set()
        religions_set = set()
        
        for item in all_data:
            if item.get('district'):
                districts_set.add(item['district'])
            if item.get('school_category'):
                categories_set.add(item['school_category'])
            if item.get('school_net') and item['school_net'] != '/':
                school_nets_set.add(item['school_net'])
            if item.get('student_gender'):
                genders_set.add(item['student_gender'])
            if item.get('religion'):
                religions_set.add(item['religion'])
        
        # 转换为排序后的列表
        filters_data = {
            "districts": sorted(districts_set),
            "categories": sorted(categories_set),
            "genders": sorted(genders_set),
            "religions": sorted(religions_set),
            "schoolNets": sorted(school_nets_set)
        }
        
        # 缓存1天 (筛选选项变化不频繁)
        cache.set(cache_key, filters_data, 60 * 60 * 24)
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": filters_data
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })
