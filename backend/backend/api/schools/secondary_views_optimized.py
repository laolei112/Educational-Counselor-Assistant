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
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None,
        
        # 兼容字段
        "band1Rate": 0,
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

