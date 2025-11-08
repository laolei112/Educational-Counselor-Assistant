from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.cache import cache
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.utils.text_converter import normalize_keyword
from backend.utils.cache import CacheManager
from common.logger import loginfo
import json
import time
import hashlib


def serialize_primary_school(school):
    """
    序列化小学数据为前端需要的格式
    优化: 减少方法调用,直接访问属性
    """
    # 优化: 直接从 total_classes_info 获取总班数,避免额外的 get_total_classes() 调用
    total_classes = 0
    if school.total_classes_info and isinstance(school.total_classes_info, dict):
        # 计算所有年级的班级总数
        total_classes = sum(
            school.total_classes_info.get(grade, 0) 
            for grade in ['primary_1', 'primary_2', 'primary_3', 'primary_4', 'primary_5', 'primary_6']
            if isinstance(school.total_classes_info.get(grade), (int, float))
        )
    
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
        "promotionInfo": school.promotion_info if school.promotion_info else {},
        # Band1比例
        "band1Rate": float(school.band1_rate) if school.band1_rate is not None else (
            school.promotion_info.get('band1_rate') if school.promotion_info and isinstance(school.promotion_info, dict) else None
        ),
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



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, F
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.utils.text_converter import normalize_keyword
from common.logger import loginfo
import json
import time


def serialize_primary_school_optimized(school):
    """
    优化版序列化函数
    1. 减少字典查找次数
    2. 避免重复的类型检查
    3. 直接计算总班数
    """
    # 预先获取 JSON 字段,避免多次访问
    total_classes_info = school.total_classes_info or {}
    promotion_info = school.promotion_info or {}
    
    # 快速计算总班数(避免方法调用)
    total_classes = 0
    if isinstance(total_classes_info, dict):
        for grade in ('primary_1', 'primary_2', 'primary_3', 'primary_4', 'primary_5', 'primary_6'):
            val = total_classes_info.get(grade, 0)
            if isinstance(val, (int, float)):
                total_classes += val
    
    # 获取 band1_rate (优先使用生成列)
    band1_rate = None
    if school.band1_rate is not None:
        band1_rate = float(school.band1_rate)
    elif isinstance(promotion_info, dict):
        band1_rate = promotion_info.get('band1_rate')
    
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
    获取小学列表 - 优化版(无缓存)
    
    核心优化:
    1. 🔥 分离 COUNT 和数据查询,COUNT 时不带 ORDER BY
    2. 🔥 使用 only() 减少查询字段(如果不需要所有字段)
    3. 🔥 优化关键字搜索逻辑
    4. 提前验证分页参数,避免无效查询
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
        
        # 网络延迟监控：记录查询前后的时间戳
        query_start = time.time()
        try:
            # 尝试获取数据库实际执行时间（如果支持）
            from django.db import connection
            db_start = time.time()
            total = count_queryset.count()
            db_end = time.time()
            
            # 计算总耗时和可能的网络延迟
            count_query_time = (db_end - query_start) * 1000
            
            # 如果 COUNT 查询耗时超过 200ms，记录详细诊断信息
            if count_query_time > 200:
                # 尝试获取数据库状态
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                        threads_connected = cursor.fetchone()[1] if cursor.fetchone() else "N/A"
                        
                        cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
                        max_connections = cursor.fetchone()[1] if cursor.fetchone() else "N/A"
                        
                        loginfo(
                            f"[SLOW_COUNT] GET /api/schools/primary/ | "
                            f"CountQuery: {count_query_time:.2f}ms | "
                            f"ThreadsConnected: {threads_connected}/{max_connections} | "
                            f"Params: category={category}, district={district}, keyword={keyword[:20] if keyword else None}"
                        )
                except:
                    pass
        except Exception as e:
            # 如果监控失败，仍然执行查询
            total = count_queryset.count()
            count_query_time = (time.time() - query_start) * 1000
            loginfo(f"[COUNT_ERROR] COUNT 查询异常: {str(e)} | 耗时: {count_query_time:.2f}ms")
        
        step_times['count_query'] = count_query_time
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
        
        # 🔥 优化7: 如果只需要部分字段,使用 only() 或 defer()
        # 例如列表页不需要所有详细信息时:
        # data_queryset = data_queryset.only(
        #     'id', 'school_name', 'school_name_traditional', 'school_name_english',
        #     'school_category', 'district', 'school_net', 'student_gender',
        #     'religion', 'teaching_language', 'band1_rate', 'tuition',
        #     'address', 'phone', 'website'
        # )
        
        # 使用切片获取当前页数据
        schools_page = data_queryset[start_index:end_index]
        
        step_times['data_query'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 序列化数据
        schools_data = [serialize_primary_school_optimized(school) for school in schools_page]
        
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
        
        # 记录性能日志
        loginfo(
            f"[PERF] GET /api/schools/primary/ (query-optimized) | "
            f"Total: {total_time:.2f}ms | "
            f"ParamParse: {step_times.get('param_parse', 0):.2f}ms | "
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
        loginfo(f"[PERF] GET /api/schools/primary/ (query-optimized) - ERROR (ValueError) | Total: {total_time:.2f}ms | Error: {str(e)}")
        return JsonResponse({
            "code": 400,
            "message": f"参数错误: {str(e)}",
            "success": False,
            "data": None
        })
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        loginfo(f"[PERF] GET /api/schools/primary/ (query-optimized) - ERROR | Total: {total_time:.2f}ms | Error: {str(e)}")
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
        # cache_key = f"primary_school_detail:{school_id}"
        # cached_data = cache.get(cache_key)
        
        # if cached_data:
        #     return JsonResponse({
        #         "code": 200,
        #         "message": "成功",
        #         "success": True,
        #         "data": cached_data
        #     })
        
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
        
        # # 缓存30分钟
        # cache.set(cache_key, school_data, 1800)
        
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
def primary_schools_stats(request):
    """
    获取小学统计信息(简化版本,只返回学校总数)
    GET /api/schools/primary/stats/
    """
    try:
        # 🔥 优化: 使用缓存
        # cache_key = "primary_schools_total_count"
        # total_schools = cache.get(cache_key)
        
        # if total_schools is None:
        total_schools = TbPrimarySchools.objects.count()
        #     # 缓存10分钟 (总数变化不频繁)
        #     cache.set(cache_key, total_schools, 600)
        
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
        # cache_key = "primary_schools_filters"
        # cached_filters = cache.get(cache_key)
        
        # if cached_filters:
        #     return JsonResponse({
        #         "code": 200,
        #         "message": "成功",
        #         "success": True,
        #         "data": cached_filters
        #     })
        
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
        
        # 缓存15分钟 (筛选选项变化不频繁)
        # cache.set(cache_key, filters_data, 900)
        
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
