from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
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
        "linkedSchools": school.promotion_rate.get('linked_schools', []) if school.promotion_rate else [],
        
        # 新增字段
        "religion": school.religion,
        "schoolType": school.category,  # 映射到schoolType字段
        "teachingLanguage": school.teaching_language if school.teaching_language else None,
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
        
        # 保留的原有字段
        "url": school.url,
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
            # 使用 Case 和 When 来实现排序：校名包含关键词的排在前面
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(net_name__icontains=keyword) |
                Q(remarks__icontains=keyword)
            ).annotate(
                # 添加排序权重：校名包含关键词的权重最高
                search_priority=Case(
                    When(name__icontains=keyword, then=Value(1)),  # 校名包含关键词，优先级最高
                    When(district__icontains=keyword, then=Value(2)),  # 地区包含关键词
                    When(address__icontains=keyword, then=Value(3)),  # 地址包含关键词
                    When(category__icontains=keyword, then=Value(4)),  # 分类包含关键词
                    When(religion__icontains=keyword, then=Value(5)),  # 宗教包含关键词
                    When(net_name__icontains=keyword, then=Value(6)),  # 校网包含关键词
                    When(remarks__icontains=keyword, then=Value(7)),  # 备注包含关键词
                    default=Value(8),
                    output_field=IntegerField()
                )
            ).order_by('search_priority', 'name')  # 按优先级和校名排序
        
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
            # 使用 Case 和 When 来实现排序：校名包含关键词的排在前面
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(net_name__icontains=keyword) |
                Q(remarks__icontains=keyword)
            ).annotate(
                # 添加排序权重：校名包含关键词的权重最高
                search_priority=Case(
                    When(name__icontains=keyword, then=Value(1)),  # 校名包含关键词，优先级最高
                    When(district__icontains=keyword, then=Value(2)),  # 地区包含关键词
                    When(address__icontains=keyword, then=Value(3)),  # 地址包含关键词
                    When(category__icontains=keyword, then=Value(4)),  # 分类包含关键词
                    When(religion__icontains=keyword, then=Value(5)),  # 宗教包含关键词
                    When(net_name__icontains=keyword, then=Value(6)),  # 校网包含关键词
                    When(remarks__icontains=keyword, then=Value(7)),  # 备注包含关键词
                    default=Value(8),
                    output_field=IntegerField()
                )
            ).order_by('search_priority', 'name')  # 按优先级和校名排序
        
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


# 注意：中学列表接口已迁移到 secondary_views.py，从 tb_secondary_schools 表读取
# 该函数已废弃，请使用 secondary_views.secondary_schools_list


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
