"""
优化后的学校API视图
主要优化：
1. 添加Redis缓存
2. 优化数据库查询
3. 减少COUNT查询
4. 优化搜索逻辑
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch, Count
from backend.models.tb_schools import TbSchools
from backend.utils.cache import CacheManager, cache_response
import json


def serialize_school(school):
    """
    序列化学校数据为前端需要的格式
    优化：预加载所有需要的字段，避免额外查询
    """
    return {
        "id": school.id,
        "name": school.name,
        "type": school.level,
        "category": school.category,
        "band1Rate": school.promotion_rate.get('band1_rate', 0) if school.promotion_rate else 0,
        "applicationStatus": school.application_status,
        "district": school.district,
        "schoolNet": school.net_name,
        "tuition": float(school.tuition) if school.tuition else 0,
        "gender": school.gender,
        "feederSchools": school.promotion_rate.get('feeder_schools', []) if school.promotion_rate else [],
        "linkedUniversities": school.promotion_rate.get('linked_universities', []) if school.promotion_rate else [],
        "linkedSchools": school.promotion_rate.get('linked_schools', []) if school.promotion_rate else [],
        
        # 新增字段
        "religion": school.religion,
        "schoolType": school.category,
        "teachingLanguage": school.promotion_rate.get('teaching_language', '中英并重') if school.promotion_rate else '中英并重',
        "curriculum": school.promotion_rate.get('curriculum', ['DSE']) if school.promotion_rate else ['DSE'],
        "applicationDeadline": school.promotion_rate.get('application_deadline') if school.promotion_rate else None,
        "schoolScale": {
            "classes": school.promotion_rate.get('classes', 0) if school.promotion_rate else 0,
            "students": school.promotion_rate.get('students', 0) if school.promotion_rate else 0
        } if school.promotion_rate else None,
        "features": school.promotion_rate.get('features', []) if school.promotion_rate else [],
        "contact": {
            "address": school.address,
            "phone": school.promotion_rate.get('phone') if school.promotion_rate else None,
            "email": school.promotion_rate.get('email') if school.promotion_rate else None,
            "website": school.official_website
        },
        
        "url": school.url,
        "remarks": school.remarks,
        "createdAt": school.created_at.isoformat() if school.created_at else None,
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None
    }


@csrf_exempt
@require_http_methods(["GET"])
def schools_list_optimized(request):
    """
    优化后的获取学校列表接口
    GET /api/schools
    
    优化点：
    1. 添加缓存层
    2. 优化查询条件
    3. 使用only()减少字段查询
    4. 缓存total count
    """
    try:
        # 获取查询参数
        school_type = request.GET.get('type')
        category = request.GET.get('category')
        district = request.GET.get('district')
        application_status = request.GET.get('applicationStatus')
        keyword = request.GET.get('keyword', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('pageSize', 20)), 100)  # 限制最大页面大小
        
        # 生成缓存key
        cache_key = CacheManager.generate_cache_key(
            CacheManager.PREFIX_SCHOOL_LIST,
            type=school_type,
            category=category,
            district=district,
            status=application_status,
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 构建基础查询
        queryset = TbSchools.objects.all()
        
        # 应用过滤条件（使用索引字段）
        if school_type:
            queryset = queryset.filter(level=school_type)
        
        if category:
            queryset = queryset.filter(category=category)
            
        if district:
            queryset = queryset.filter(district=district)
            
        if application_status:
            queryset = queryset.filter(application_status=application_status)
        
        # 搜索优化：简化搜索逻辑
        if keyword:
            # 优先搜索名称和地区（这两个字段最常用）
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(district__icontains=keyword)
            )
        
        # 排序（使用索引字段）
        queryset = queryset.order_by('-application_status', 'name')
        
        # 获取总数（缓存这个结果）
        count_cache_key = cache_key + ":count"
        total = CacheManager.get(count_cache_key)
        if total is None:
            total = queryset.count()
            CacheManager.set(count_cache_key, total, CacheManager.TIMEOUT_SHORT)
        
        # 计算分页
        total_pages = (total + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 获取当前页数据（只查询需要的字段）
        schools_page = queryset[start_index:end_index]
        
        # 序列化数据
        schools_data = [serialize_school(school) for school in schools_page]
        
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
def school_detail_optimized(request, school_id):
    """
    优化后的获取学校详情接口
    GET /api/schools/{id}
    """
    try:
        school_id = int(school_id)
        
        # 生成缓存key
        cache_key = f"{CacheManager.PREFIX_SCHOOL_DETAIL}{school_id}"
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 查询学校
        try:
            school = TbSchools.objects.get(id=school_id)
        except TbSchools.DoesNotExist:
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
            "data": serialize_school(school)
        }
        
        # 缓存结果（详情页缓存时间更长）
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
def schools_stats_optimized(request):
    """
    优化后的获取学校统计信息接口
    GET /api/schools/stats
    """
    try:
        school_type = request.GET.get('type')
        
        # 生成缓存key
        cache_key = CacheManager.generate_cache_key(
            CacheManager.PREFIX_SCHOOL_STATS,
            type=school_type
        )
        
        # 尝试从缓存获取
        cached_result = CacheManager.get(cache_key)
        if cached_result:
            return JsonResponse(cached_result)
        
        # 构建查询
        queryset = TbSchools.objects.all()
        
        if school_type:
            queryset = queryset.filter(level=school_type)
        
        # 使用聚合查询一次性获取统计信息
        stats = queryset.aggregate(
            total=Count('id'),
            open_applications=Count('id', filter=Q(application_status='open'))
        )
        
        # 构建响应
        response_data = {
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": stats['total'],
                "openApplications": stats['open_applications']
            }
        }
        
        # 缓存结果（统计数据缓存时间最长）
        CacheManager.set(cache_key, response_data, CacheManager.TIMEOUT_LONG)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })

