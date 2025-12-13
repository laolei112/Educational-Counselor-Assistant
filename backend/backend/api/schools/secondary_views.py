from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import F, Q
from django.core.cache import cache
from backend.models.tb_secondary_schools import TbSecondarySchools
from backend.utils.text_converter import normalize_keyword
from backend.utils.cache import CacheManager
from backend.utils.application_status import calculate_s1_p1_status, calculate_transfer_status
from common.logger import logerror, loginfo
import json
import traceback
import time
import hashlib


def get_cache_key_for_secondary_query(params):
    """
    根据查询参数生成缓存键
    """
    param_str = json.dumps(params, sort_keys=True)
    hash_value = hashlib.md5(param_str.encode()).hexdigest()
    return f"secondary_schools_list:{hash_value}"


def serialize_secondary_school_for_list(school):
    """
    列表页精简序列化 - 只返回卡片展示必需的字段
    
    卡片显示内容：
    - 基本信息：名称、类型、地区、校网、宗教、性别、学费、分组
    - 申请状态：transferInfo (用于显示申请状态徽章) - 精简版
    
    不包含详情页专用字段：
    - admissionInfo (招生详情)
    - promotionInfo (升学详情)
    - schoolCurriculum (课程体系)
    """
    # 🔥 优化：精简 transferInfo，只返回计算后的申请状态（不包含详细时间信息）
    transfer_info = school.transfer_info or {}
    transfer_info_minimal = {}
    if isinstance(transfer_info, dict):
        # 使用统一的工具函数计算申请状态，与前端逻辑保持一致
        # 这样可以大幅减少数据大小，同时保持前端功能
        
        # 计算S1申请状态（中一申请）- 使用小一/S1的统一函数
        s1_info = transfer_info.get('S1')
        if s1_info and isinstance(s1_info, dict):
            s1_status = calculate_s1_p1_status(s1_info)
            if s1_status:
                transfer_info_minimal['S1'] = {'application_status': s1_status}
        
        # 计算插班申请状态
        transfer_data = transfer_info.get('插班')
        if transfer_data and isinstance(transfer_data, dict):
            # 🔥 传递学校ID用于调试（可选）
            transfer_status = calculate_transfer_status(transfer_data, debug_school_id=school.id)
            if transfer_status:
                transfer_info_minimal['插班'] = {'application_status': transfer_status}
        
        # 🔥 为了前端兼容性，在顶层添加 application_status
        # 优先使用S1或插班的状态
        if 'S1' in transfer_info_minimal:
            transfer_info_minimal['application_status'] = transfer_info_minimal['S1'].get('application_status')
        elif '插班' in transfer_info_minimal:
            transfer_info_minimal['application_status'] = transfer_info_minimal['插班'].get('application_status')
    
    return {
        # 基本信息
        "id": school.id,
        "name": school.school_name,
        "nameTraditional": school.school_name_traditional,
        "nameEnglish": school.school_name_english,
        "type": "secondary",
        "district": school.district,
        "schoolNet": school.school_net,
        "religion": school.religion,
        "gender": school.student_gender,
        "tuition": school.tuition if school.tuition else 0,
        "category": school.school_category,
        "schoolType": school.school_category,
        "schoolGroup": school.school_group,
        
        # 🔥 优化：精简的申请状态信息（只返回状态标识，不包含详细时间）
        "transferInfo": transfer_info_minimal,
    }


def serialize_secondary_school(school):
    """
    详情页完整序列化 - 返回所有字段
    用于详情接口 /api/schools/secondary/{id}/
    """
    # 解析课程数据
    curriculum_data = None
    if school.school_curriculum:
        try:
            curriculum_data = json.loads(school.school_curriculum)
        except:
            curriculum_data = None
    
    # 解析按教学语言分类的课程数据
    curriculum_by_language = school.curriculum_by_language if school.curriculum_by_language else None
    
    return {
        "id": school.id,
        "name": school.school_name,
        "nameTraditional": school.school_name_traditional,
        "nameEnglish": school.school_name_english,
        "type": "secondary",
        "district": school.district,
        "schoolNet": school.school_net,
        "religion": school.religion,
        "gender": school.student_gender,
        "teachingLanguage": school.teaching_language if school.teaching_language else None,
        "tuition": school.tuition if school.tuition else 0,
        "category": school.school_category,
        "schoolType": school.school_category,
        "schoolGroup": school.school_group,
        "transferInfo": school.transfer_info if school.transfer_info else {},
        "totalClasses": school.total_classes,
        "admissionInfo": school.admission_info,
        "promotionInfo": school.promotion_info if school.promotion_info else {},
        "schoolCurriculum": curriculum_data,
        "schoolScale": {
            "classes": school.total_classes if school.total_classes else 0,
            "students": 0  # 中学数据中没有学生数，设置为0
        },
        "contact": {
            "address": school.address,
            "phone": school.phone,
            "email": school.email,
            "website": school.website
        },
        "address": school.address,
        "phone": school.phone,
        "email": school.email,
        "website": school.website,
        "officialWebsite": school.website,
        "createdAt": school.created_at.isoformat() if school.created_at else None,
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None,
        
        # 为了兼容前端，添加一些默认字段
        "band1Rate": 0,
        
        # ========== 新增字段 ==========
        # 基本信息
        "schoolArea": school.school_area,
        "schoolSponsor": school.school_sponsor,
        "foundedYear": school.founded_year,
        "schoolMotto": school.school_motto,
        
        # 教师信息
        "teacherCount": school.teacher_count,
        "teacherInfo": school.teacher_info if school.teacher_info else None,
        
        # 班级信息
        "classesByGrade": school.classes_by_grade if school.classes_by_grade else None,
        
        # 课程信息（按教学语言分类）
        "curriculumByLanguage": curriculum_by_language,
        
        # 学校政策与特色
        "languagePolicy": school.language_policy,
        "teachingStrategy": school.teaching_strategy,
        "schoolBasedCurriculum": school.school_based_curriculum,
        "careerEducation": school.career_education,
        "diversitySupport": school.diversity_support,
        "assessmentAdaptation": school.assessment_adaptation,
        "wholePersonLearning": school.whole_person_learning,
        
        # 设施与交通
        "facilities": school.facilities,
        "transportation": school.transportation,
        "remarks": school.remarks,
    }


@csrf_exempt
@require_http_methods(["GET"])
def secondary_schools_list(request):
    """
    获取中学列表（从 tb_secondary_schools 表）- 带缓存优化
    GET /api/schools/secondary
    """
    # 性能监控：记录开始时间
    start_time = time.time()
    step_times = {}
    step_start = time.time()
    
    try:
        # 获取查询参数
        category = request.GET.get('category')
        district = request.GET.get('district')
        school_group = request.GET.get('schoolGroup')
        gender = request.GET.get('gender')
        religion = request.GET.get('religion')
        keyword = request.GET.get('keyword')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 20))
        
        step_times['param_parse'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 🔥 缓存优化: 基于查询参数生成缓存键
        cache_params = {
            'category': category,
            'district': district,
            'school_group': school_group,
            'gender': gender,
            'religion': religion,
            'keyword': keyword,
            'page': page,
            'page_size': page_size
        }
        cache_key = get_cache_key_for_secondary_query(cache_params)
        step_times['cache_key_gen'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 尝试从缓存获取数据
        cached_data = cache.get(cache_key)
        cache_get_time = (time.time() - step_start) * 1000
        step_times['cache_get'] = cache_get_time
        step_start = time.time()
        
        # 🔥 监控：如果缓存读取超过100ms，记录警告
        if cache_get_time > 100:
            loginfo(
                f"[WARN] Slow cache read detected | "
                f"CacheKey: {cache_key[:50]}... | "
                f"CacheGet: {cache_get_time:.2f}ms | "
                f"This may indicate Redis performance issues or network latency"
            )
        
        if cached_data:
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
            
            step_times['data_process'] = (time.time() - step_start) * 1000
            step_start = time.time()
            
            # 构建JsonResponse（这里会序列化数据）
            response = JsonResponse(result_data)
            
            step_times['json_response'] = (time.time() - step_start) * 1000
            total_time = (time.time() - start_time) * 1000
            
            loginfo(
                f"[PERF] GET /api/schools/secondary/ (from-cache) | "
                f"Total: {total_time:.2f}ms | "
                f"KeyGen: {step_times.get('cache_key_gen', 0):.2f}ms | "
                f"CacheGet: {step_times.get('cache_get', 0):.2f}ms | "
                f"DataProcess: {step_times.get('data_process', 0):.2f}ms | "
                f"JsonResponse: {step_times.get('json_response', 0):.2f}ms | "
                f"Result: total={data_part.get('total', 0)}, page={data_part.get('page', page)}, pageSize={data_part.get('pageSize', page_size)}, items={len(data_part.get('list', []))}"
            )
            return response
        
        step_times['cache_check'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 构建查询条件 - 从 tb_secondary_schools 表查询
        queryset = TbSecondarySchools.objects.all()
        
        # 应用过滤条件
        if category:
            queryset = queryset.filter(school_category=category)
            
        if district:
            queryset = queryset.filter(district=district)
        
        if school_group:
            queryset = queryset.filter(school_group=school_group)
        
        if gender:
            queryset = queryset.filter(student_gender=gender)
        
        if religion:
            queryset = queryset.filter(religion=religion)
            
        if keyword:
            # 标准化关键词（将繁体转为简体，统一用于搜索）
            normalized_keyword = normalize_keyword(keyword)
            
            # 只搜索学校名称（简体、繁体、英文）
            # 同时用标准化关键词和原始关键词搜索，确保无论用户输入简体还是繁体，都能匹配到
            queryset = queryset.filter(
                Q(school_name__icontains=normalized_keyword) | 
                Q(school_name__icontains=keyword) |
                Q(school_name_traditional__icontains=normalized_keyword) |
                Q(school_name_traditional__icontains=keyword) |
                Q(school_name_english__icontains=keyword)
            ).order_by(F('school_group').asc(nulls_last=True), 'school_name')
        else:
            # 没有关键词时，按照 school_group 和 school_name 排序（NULL 值排在最后）
            queryset = queryset.order_by(F('school_group').asc(nulls_last=True), 'school_name')
        
        step_times['query_build'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 优化COUNT查询：使用缓存避免重复执行COUNT(*)
        total = queryset.count()
        
        step_times['count_query'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 计算分页信息
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 列表页只查询卡片必需字段（减少数据库I/O和网络传输）
        queryset = queryset.only(
            # 基本字段
            'id', 'school_name', 'school_name_traditional', 'school_name_english',
            'district', 'school_net', 'religion', 'student_gender',
            'tuition', 'school_category', 'school_group',
            # 卡片需要的JSON字段
            'transfer_info'  # 申请状态
        )
        
        # 使用切片获取当前页数据（避免Paginator的额外查询）
        schools_page = queryset[start_index:end_index]
        
        step_times['data_query'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 使用精简序列化（只返回卡片必需字段）
        schools_data = [serialize_secondary_school_for_list(school) for school in schools_page]
        
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
            f"[PERF] GET /api/schools/secondary/ (query-optimized) | "
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
        loginfo(f"[PERF] GET /api/schools/secondary/ (non-optimized) - ERROR (ValueError) | Total: {total_time:.2f}ms | Error: {str(e)}")
        return JsonResponse({
            "code": 400,
            "message": f"参数错误: {str(e)}",
            "success": False,
            "data": None
        })
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logerror(f"服务器错误: {traceback.format_exc()}")
        loginfo(f"[PERF] GET /api/schools/secondary/ (non-optimized) - ERROR | Total: {total_time:.2f}ms | Error: {str(e)}")
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def secondary_school_detail(request, school_id):
    """
    获取中学详情（从 tb_secondary_schools 表）- 带缓存优化
    GET /api/schools/secondary/{id}
    """
    try:
        school_id = int(school_id)
        
        # 🔥 缓存优化: 尝试从缓存获取数据
        cache_key = f"secondary_school_detail:{school_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": cached_data
            })
        
        try:
            school = TbSecondarySchools.objects.get(id=school_id)
        except TbSecondarySchools.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
        
        # 序列化学校数据
        school_data = serialize_secondary_school(school)
        
        # 🔥 缓存数据（30分钟）
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
def secondary_school_recommendations(request, school_id):
    """
    获取中学推荐列表（同区学校、热门学校）
    GET /api/schools/secondary/{id}/recommendations/
    """
    try:
        school_id = int(school_id)
        
        # 缓存优化
        cache_key = f"secondary_school_recommendations:{school_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": cached_data
            })
            
        try:
            current_school = TbSecondarySchools.objects.get(id=school_id)
        except TbSecondarySchools.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
            
        # 1. 同区推荐 (Same District) - 随机取4个
        related_schools = TbSecondarySchools.objects.filter(
            district=current_school.district
        ).exclude(id=school_id).order_by('?')[:6]
        
        # 2. 热门推荐 (Popular) - 取 Band 1A/1B 学校中随机6个
        popular_schools = TbSecondarySchools.objects.filter(
            school_group__in=['BAND 1A', 'BAND 1B', 'BAND 1C']
        ).exclude(
            id=school_id
        ).exclude(
            id__in=[s.id for s in related_schools]
        ).order_by('?')[:6]
        
        # 序列化函数 (精简版)
        def serialize_simple(school):
            return {
                "id": school.id,
                "name": school.school_name,
                "type": "secondary",
                "district": school.district,
                "category": school.school_category,
                "tuition": school.tuition or "-",
                "schoolGroup": school.school_group
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
def secondary_schools_stats(request):
    """
    获取中学统计信息（简化版本，只返回学校总数）- 带缓存优化
    GET /api/schools/secondary/stats
    """
    try:
        # 🔥 缓存优化: 尝试从缓存获取数据
        cache_key = "secondary_schools_total_count"
        total_schools = cache.get(cache_key)
        
        if total_schools is None:
            # 只返回所有学校的总数
            total_schools = TbSecondarySchools.objects.count()
            # 🔥 缓存1天（总数变化不频繁）
            cache.set(cache_key, total_schools, 60 * 60 * 24)
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total_schools,
                "openApplications": 0  # 为了兼容前端接口，保留此字段
            }
        })
        
    except Exception as e:
        logerror(f"服务器错误: {traceback.format_exc()}")
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def secondary_schools_filters(request):
    """
    优化后的中学筛选器接口 - 带缓存优化
    GET /api/schools/secondary/filters/
    
    性能优化：
    1. 🔥 使用缓存提升响应速度
    2. 使用单次查询获取所有字段，减少数据库查询次数（从5次减少到1次）
    3. 在Python中处理去重和排序，避免多次数据库扫描
    """
    try:
        # 🔥 缓存优化: 尝试从缓存获取数据
        cache_key = "secondary_schools_filters"
        cached_filters = cache.get(cache_key)
        
        if cached_filters:
            return JsonResponse({
                "code": 200,
                "message": "成功",
                "success": True,
                "data": cached_filters
            })
        
        # 优化：使用单次查询获取所有需要的字段，而不是每个字段一个查询
        # 这样可以减少数据库查询次数从5次减少到1次
        all_data = TbSecondarySchools.objects.values(
            'district', 
            'school_category', 
            'school_group', 
            'student_gender', 
            'religion'
        ).distinct()
        
        # 在Python中处理去重和排序，避免多次数据库扫描
        districts_set = set()
        categories_set = set()
        school_groups_set = set()
        genders_set = set()
        religions_set = set()
        
        for item in all_data:
            if item.get('district'):
                districts_set.add(item['district'])
            if item.get('school_category'):
                categories_set.add(item['school_category'])
            if item.get('school_group'):
                school_groups_set.add(item['school_group'])
            if item.get('student_gender'):
                genders_set.add(item['student_gender'])
            if item.get('religion'):
                religions_set.add(item['religion'])
        
        # 转换为排序后的列表
        filters_data = {
            "districts": sorted(districts_set),
            "categories": sorted(categories_set),
            "schoolGroups": sorted(school_groups_set),
            "genders": sorted(genders_set),
            "religions": sorted(religions_set)
        }
        
        # 🔥 缓存1天（筛选选项变化不频繁）
        cache.set(cache_key, filters_data, 60 * 60 * 24)
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": filters_data
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })

