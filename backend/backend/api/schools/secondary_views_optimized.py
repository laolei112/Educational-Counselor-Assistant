"""
优化后的中学API视图
主要优化：
1. 添加Redis缓存
2. 优化数据库查询
3. 减少COUNT查询
4. 优化搜索逻辑
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from backend.models.tb_secondary_schools import TbSecondarySchools
from backend.utils.cache import CacheManager
from backend.utils.text_converter import normalize_keyword
import json


def serialize_secondary_school(school):
    """
    序列化中学数据为前端需要的格式
    """
    # 解析课程数据
    curriculum_data = None
    if school.school_curriculum:
        try:
            curriculum_data = json.loads(school.school_curriculum)
        except:
            curriculum_data = None
    
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
            "students": 0
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
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None
    }


@csrf_exempt
@require_http_methods(["GET"])
def secondary_schools_list_optimized(request):
    """
    优化后的中学列表接口
    GET /api/schools/secondary/
    """
    try:
        # 获取查询参数
        category = request.GET.get('category')
        district = request.GET.get('district')
        school_group = request.GET.get('schoolGroup')
        gender = request.GET.get('gender')
        religion = request.GET.get('religion')
        keyword = request.GET.get('keyword', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('pageSize', 20)), 100)
        
        # 生成缓存key
        cache_key = CacheManager.generate_cache_key(
            "secondary:list:",
            category=category,
            district=district,
            school_group=school_group,
            gender=gender,
            religion=religion,
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 构建查询条件
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
        
        # 搜索优化：支持简繁体搜索
        if keyword:
            # 标准化关键词（将繁体转为简体，统一用于搜索）
            normalized_keyword = normalize_keyword(keyword)
            
            # 构建搜索条件：同时搜索简体字段和繁体字段
            # 对于学校名称，同时用标准化关键词和原始关键词搜索简体和繁体字段
            # 这样可以确保无论用户输入简体还是繁体，都能匹配到
            name_filter = (
                Q(school_name__icontains=normalized_keyword) | 
                Q(school_name__icontains=keyword) |
                Q(school_name_traditional__icontains=normalized_keyword) |
                Q(school_name_traditional__icontains=keyword)
            )
            
            # 其他字段的搜索（同时使用标准化关键词和原始关键词）
            other_filters = (
                Q(district__icontains=normalized_keyword) | Q(district__icontains=keyword) |
                Q(address__icontains=normalized_keyword) | Q(address__icontains=keyword) |
                Q(school_category__icontains=normalized_keyword) | Q(school_category__icontains=keyword) |
                Q(religion__icontains=normalized_keyword) | Q(religion__icontains=keyword) |
                Q(school_net__icontains=normalized_keyword) | Q(school_net__icontains=keyword) |
                Q(school_group__icontains=normalized_keyword) | Q(school_group__icontains=keyword) |
                Q(admission_info__icontains=normalized_keyword) | Q(admission_info__icontains=keyword)
            )
            
            queryset = queryset.filter(name_filter | other_filters)
        
        # 排序
        queryset = queryset.order_by('school_name')
        
        # 获取总数（缓存）
        count_cache_key = cache_key + ":count"
        total = CacheManager.get(count_cache_key)
        if total is None:
            total = queryset.count()
            CacheManager.set(count_cache_key, total, CacheManager.TIMEOUT_SHORT)
        
        # 计算分页
        total_pages = (total + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 获取当前页数据
        schools_page = queryset[start_index:end_index]
        
        # 序列化数据
        schools_data = [serialize_secondary_school(school) for school in schools_page]
        
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
        
        # 缓存结果
        CacheManager.set(cache_key, response_data, CacheManager.TIMEOUT_SHORT)
        
        return JsonResponse(response_data)
        
    except ValueError as e:
        return JsonResponse({
            "code": 400,
            "message": f"参数错误: {str(e)}",
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
def secondary_school_detail_optimized(request, school_id):
    """
    优化后的中学详情接口
    GET /api/schools/secondary/{id}/
    """
    try:
        school_id = int(school_id)
        
        # 生成缓存key
        cache_key = f"secondary:detail:{school_id}"
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 查询学校
        try:
            school = TbSecondarySchools.objects.get(id=school_id)
        except TbSecondarySchools.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": serialize_secondary_school(school)
        }
        
        # 缓存结果
        CacheManager.set(cache_key, response_data, CacheManager.TIMEOUT_MEDIUM)
        
        return JsonResponse(response_data)
        
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
def secondary_schools_stats_optimized(request):
    """
    优化后的中学统计接口
    GET /api/schools/secondary/stats/
    """
    try:
        # 获取查询参数
        district = request.GET.get('district')
        category = request.GET.get('category')
        school_group = request.GET.get('schoolGroup')
        
        # 生成缓存key
        cache_key = CacheManager.generate_cache_key(
            "secondary:stats:",
            district=district,
            category=category,
            school_group=school_group
        )
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 构建查询
        queryset = TbSecondarySchools.objects.all()
        
        if district:
            queryset = queryset.filter(district=district)
        
        if category:
            queryset = queryset.filter(school_category=category)
        
        if school_group:
            queryset = queryset.filter(school_group=school_group)
        
        # 使用聚合查询
        total = queryset.count()
        
        # 按组别统计
        by_group = {}
        if not school_group:
            groups = TbSecondarySchools.objects.values('school_group').annotate(
                count=Count('id')
            ).order_by('school_group')
            by_group = {item['school_group']: item['count'] for item in groups if item['school_group']}
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total,
                "byGroup": by_group,
                "byDistrict": {},
                "byCategory": {}
            }
        }
        
        # 缓存结果
        CacheManager.set(cache_key, response_data, CacheManager.TIMEOUT_LONG)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })


@csrf_exempt
@require_http_methods(["GET"])
def secondary_schools_filters_optimized(request):
    """
    优化后的中学筛选器接口
    GET /api/schools/secondary/filters/
    
    性能优化：
    1. 使用单次查询获取所有字段，减少数据库查询次数（从5次减少到1次）
    2. 在Python中处理去重和排序，避免多次数据库扫描
    3. 使用缓存减少重复查询
    """
    try:
        # 生成缓存key
        cache_key = "secondary:filters:all"
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
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
        districts = sorted(districts_set)
        categories = sorted(categories_set)
        school_groups = sorted(school_groups_set)
        genders = sorted(genders_set)
        religions = sorted(religions_set)
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "districts": districts,
                "categories": categories,
                "schoolGroups": school_groups,
                "genders": genders,
                "religions": religions
            }
        }
        
        # 缓存结果（筛选器数据变化较少，缓存时间较长）
        CacheManager.set(cache_key, response_data, CacheManager.TIMEOUT_LONG)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })

