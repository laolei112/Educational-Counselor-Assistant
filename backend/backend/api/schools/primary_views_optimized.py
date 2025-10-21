"""
优化后的小学API视图
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
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.utils.cache import CacheManager
import json


def serialize_primary_school(school):
    """
    序列化小学数据为前端需要的格式
    """
    # 获取关联中学
    linked_schools = school.get_linked_secondary_schools()
    
    # 获取总班数
    total_classes = school.get_total_classes()
    
    return {
        "id": school.id,
        "name": school.school_name,
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
        
        # 中学联系
        "linkedSchools": linked_schools,
        "secondaryInfo": school.secondary_info if school.secondary_info else {},
        
        # 班级信息
        "totalClasses": total_classes,
        "classesInfo": school.total_classes_info if school.total_classes_info else {},
        
        # 教学信息
        "classTeachingInfo": school.class_teaching_info if school.class_teaching_info else {},
        
        # 评估信息
        "assessmentInfo": school.assessment_info if school.assessment_info else {},
        # 插班信息
        "transferInfo": school.transfer_info if school.transfer_info else {},
        # 升学信息
        "promotionInfo": school.promotion_info if school.promotion_info else {},
        
        # 其他
        "isFullDay": school.is_full_day(),
        "isCoed": school.is_coed(),
        
        # 时间戳
        "createdAt": school.created_at.isoformat() if school.created_at else None,
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None
    }


@csrf_exempt
@require_http_methods(["GET"])
def primary_schools_list_optimized(request):
    """
    优化后的小学列表接口
    GET /api/schools/primary/
    """
    try:
        # 获取查询参数
        category = request.GET.get('category')
        district = request.GET.get('district')
        school_net = request.GET.get('schoolNet')
        gender = request.GET.get('gender')
        religion = request.GET.get('religion')
        teaching_language = request.GET.get('teachingLanguage')
        keyword = request.GET.get('keyword', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('pageSize', 20)), 100)
        
        # 生成缓存key
        cache_key = CacheManager.generate_cache_key(
            "primary:list:",
            category=category,
            district=district,
            school_net=school_net,
            gender=gender,
            religion=religion,
            teaching_language=teaching_language,
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 构建查询条件
        queryset = TbPrimarySchools.objects.all()
        
        # 应用过滤条件
        if category:
            queryset = queryset.filter(school_category=category)
            
        if district:
            queryset = queryset.filter(district=district)
        
        if school_net:
            queryset = queryset.filter(school_net=school_net)
        
        if gender:
            queryset = queryset.filter(student_gender=gender)
        
        if religion:
            queryset = queryset.filter(religion=religion)
        
        if teaching_language:
            queryset = queryset.filter(teaching_language=teaching_language)
        
        # 搜索优化：只搜索高频字段
        if keyword:
            queryset = queryset.filter(
                Q(school_name__icontains=keyword) | 
                Q(district__icontains=keyword)
            )
        
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
        schools_data = [serialize_primary_school(school) for school in schools_page]
        
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
def primary_school_detail_optimized(request, school_id):
    """
    优化后的小学详情接口
    GET /api/schools/primary/{id}/
    """
    try:
        school_id = int(school_id)
        
        # 生成缓存key
        cache_key = f"primary:detail:{school_id}"
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 查询学校
        try:
            school = TbPrimarySchools.objects.get(id=school_id)
        except TbPrimarySchools.DoesNotExist:
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
            "data": serialize_primary_school(school)
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
def primary_schools_stats_optimized(request):
    """
    优化后的小学统计接口
    GET /api/schools/primary/stats/
    """
    try:
        # 获取查询参数
        district = request.GET.get('district')
        category = request.GET.get('category')
        
        # 生成缓存key
        cache_key = CacheManager.generate_cache_key(
            "primary:stats:",
            district=district,
            category=category
        )
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 构建查询
        queryset = TbPrimarySchools.objects.all()
        
        if district:
            queryset = queryset.filter(district=district)
        
        if category:
            queryset = queryset.filter(school_category=category)
        
        # 使用聚合查询
        total = queryset.count()
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total,
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
def primary_schools_filters_optimized(request):
    """
    优化后的小学筛选器接口
    GET /api/schools/primary/filters/
    """
    try:
        # 生成缓存key
        cache_key = "primary:filters:all"
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 获取所有可用的筛选选项（使用聚合查询）
        districts = list(TbPrimarySchools.objects.values_list('district', flat=True).distinct().order_by('district'))
        categories = list(TbPrimarySchools.objects.values_list('school_category', flat=True).distinct().order_by('school_category'))
        school_nets = list(TbPrimarySchools.objects.values_list('school_net', flat=True).distinct().order_by('school_net'))
        genders = list(TbPrimarySchools.objects.values_list('student_gender', flat=True).distinct().order_by('student_gender'))
        religions = list(TbPrimarySchools.objects.values_list('religion', flat=True).distinct().order_by('religion'))
        teaching_languages = list(TbPrimarySchools.objects.values_list('teaching_language', flat=True).distinct().order_by('teaching_language'))
        
        # 过滤掉None和空字符串
        districts = [d for d in districts if d]
        categories = [c for c in categories if c]
        school_nets = [s for s in school_nets if s]
        genders = [g for g in genders if g]
        religions = [r for r in religions if r]
        teaching_languages = [t for t in teaching_languages if t]
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "districts": districts,
                "categories": categories,
                "schoolNets": school_nets,
                "genders": genders,
                "religions": religions,
                "teachingLanguages": teaching_languages
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

