from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from backend.models.tb_schools import TbSchools
import json


def serialize_school(school):
    """
    序列化学校数据为前端需要的格式
    """
    return {
        "id": school.id,
        "name": school.name,
        "type": school.level,  # 使用 level 字段映射到 type
        "category": school.category,
        "band1Rate": school.promotion_rate.get('band1_rate', 0) if school.promotion_rate else 0,
        "applicationStatus": school.application_status,
        "district": school.district,
        "schoolNet": school.net_name,  # 使用 net_name 字段映射到 schoolNet
        "tuition": float(school.tuition) if school.tuition else 0,
        "gender": school.gender,
        "feederSchools": school.promotion_rate.get('feeder_schools', []) if school.promotion_rate else [],
        "linkedUniversities": school.promotion_rate.get('linked_universities', []) if school.promotion_rate else [],
        "url": school.url,
        "religion": school.religion,
        "address": school.address,
        "officialWebsite": school.official_website,
        "remarks": school.remarks,
        "createdAt": school.created_at.isoformat() if school.created_at else None,
        "updatedAt": school.updated_at.isoformat() if school.updated_at else None
    }


@csrf_exempt
@require_http_methods(["GET"])
def schools_list(request):
    """
    获取学校列表
    GET /api/schools
    """
    try:
        # 获取查询参数
        school_type = request.GET.get('type')
        category = request.GET.get('category')
        district = request.GET.get('district')
        application_status = request.GET.get('applicationStatus')
        keyword = request.GET.get('keyword')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 20))
        
        # 构建查询条件
        queryset = TbSchools.objects.all()
        
        # 应用过滤条件
        if school_type:
            queryset = queryset.filter(level=school_type)
        
        if category:
            queryset = queryset.filter(category=category)
            
        if district:
            queryset = queryset.filter(district=district)
            
        if application_status:
            queryset = queryset.filter(application_status=application_status)
            
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(net_name__icontains=keyword) |
                Q(remarks__icontains=keyword)
            )
        
        # 分页
        paginator = Paginator(queryset, page_size)
        schools_page = paginator.get_page(page)
        
        # 序列化数据
        schools_data = [serialize_school(school) for school in schools_page]
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "list": schools_data,
                "total": paginator.count,
                "page": page,
                "pageSize": page_size,
                "totalPages": paginator.num_pages
            }
        })
        
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
def school_detail(request, school_id):
    """
    获取学校详情
    GET /api/schools/{id}
    """
    try:
        school_id = int(school_id)
        
        try:
            school = TbSchools.objects.get(id=school_id)
        except TbSchools.DoesNotExist:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
        
        # 序列化学校数据
        school_data = serialize_school(school)
        
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
def primary_schools_list(request):
    """
    获取小学列表
    GET /api/schools/primary
    """
    try:
        # 获取查询参数
        category = request.GET.get('category')
        district = request.GET.get('district')
        application_status = request.GET.get('applicationStatus')
        keyword = request.GET.get('keyword')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 20))
        
        # 构建查询条件 - 只查询小学
        queryset = TbSchools.objects.filter(level='primary')
        
        # 应用过滤条件
        if category:
            queryset = queryset.filter(category=category)
            
        if district:
            queryset = queryset.filter(district=district)
            
        if application_status:
            queryset = queryset.filter(application_status=application_status)
            
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(net_name__icontains=keyword) |
                Q(remarks__icontains=keyword)
            )
        
        # 分页
        paginator = Paginator(queryset, page_size)
        schools_page = paginator.get_page(page)
        
        # 序列化数据
        schools_data = [serialize_school(school) for school in schools_page]
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "list": schools_data,
                "total": paginator.count,
                "page": page,
                "pageSize": page_size,
                "totalPages": paginator.num_pages
            }
        })
        
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
def secondary_schools_list(request):
    """
    获取中学列表
    GET /api/schools/secondary
    """
    try:
        # 获取查询参数
        category = request.GET.get('category')
        district = request.GET.get('district')
        application_status = request.GET.get('applicationStatus')
        keyword = request.GET.get('keyword')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 20))
        
        # 构建查询条件 - 只查询中学
        queryset = TbSchools.objects.filter(level='secondary')
        
        # 应用过滤条件
        if category:
            queryset = queryset.filter(category=category)
            
        if district:
            queryset = queryset.filter(district=district)
            
        if application_status:
            queryset = queryset.filter(application_status=application_status)
            
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(net_name__icontains=keyword) |
                Q(remarks__icontains=keyword)
            )
        
        # 分页
        paginator = Paginator(queryset, page_size)
        schools_page = paginator.get_page(page)
        
        # 序列化数据
        schools_data = [serialize_school(school) for school in schools_page]
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "list": schools_data,
                "total": paginator.count,
                "page": page,
                "pageSize": page_size,
                "totalPages": paginator.num_pages
            }
        })
        
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
def schools_stats(request):
    """
    获取学校统计信息
    GET /api/schools/stats
    """
    try:
        school_type = request.GET.get('type')
        
        # 构建查询条件
        queryset = TbSchools.objects.all()
        if school_type:
            queryset = queryset.filter(level=school_type)
        
        # 计算统计信息
        total_schools = queryset.count()
        open_applications = queryset.filter(application_status='open').count()
        
        # 按类型统计
        type_stats = {}
        for level, _ in TbSchools.LEVEL_CHOICES:
            count = queryset.filter(level=level).count()
            type_stats[level] = count
        
        # 按地区统计
        district_stats = {}
        districts = queryset.values_list('district', flat=True).distinct()
        for district in districts:
            if district:
                count = queryset.filter(district=district).count()
                district_stats[district] = count
        
        # 按分类统计
        category_stats = {}
        for category, _ in TbSchools.CATEGORY_CHOICES:
            count = queryset.filter(category=category).count()
            category_stats[category] = count
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total_schools,
                "openApplications": open_applications,
                "typeStats": type_stats,
                "districtStats": district_stats,
                "categoryStats": category_stats
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        }) 
