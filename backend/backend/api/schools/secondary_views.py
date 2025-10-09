from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from backend.models.tb_secondary_schools import TbSecondarySchools
import json


def serialize_secondary_school(school):
    """
    序列化中学数据为前端需要的格式
    """
    return {
        "id": school.id,
        "name": school.school_name,
        "type": "secondary",
        "district": school.district,
        "schoolNet": school.school_net,
        "religion": school.religion,
        "gender": school.student_gender,
        "tuition": school.tuition,
        "category": school.school_category,
        "schoolType": school.school_category,
        "schoolGroup": school.school_group,
        "transferOpenTime": school.transfer_open_time,
        "totalClasses": school.total_classes,
        "admissionInfo": school.admission_info,
        "schoolCurriculum": school.school_curriculum,
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
        "applicationStatus": "open",  # 默认值
        "band1Rate": 0,  # 如果需要可以从 school_group 推算
    }


@csrf_exempt
@require_http_methods(["GET"])
def secondary_schools_list(request):
    """
    获取中学列表（从 tb_secondary_schools 表）
    GET /api/schools/secondary
    """
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
            # 使用 Case 和 When 来实现排序：校名包含关键词的排在前面
            queryset = queryset.filter(
                Q(school_name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(school_category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(school_net__icontains=keyword) |
                Q(school_group__icontains=keyword) |
                Q(admission_info__icontains=keyword)
            ).annotate(
                # 添加排序权重：校名包含关键词的权重最高
                search_priority=Case(
                    When(school_name__icontains=keyword, then=Value(1)),
                    When(district__icontains=keyword, then=Value(2)),
                    When(address__icontains=keyword, then=Value(3)),
                    When(school_category__icontains=keyword, then=Value(4)),
                    When(religion__icontains=keyword, then=Value(5)),
                    When(school_net__icontains=keyword, then=Value(6)),
                    When(school_group__icontains=keyword, then=Value(7)),
                    When(admission_info__icontains=keyword, then=Value(8)),
                    default=Value(9),
                    output_field=IntegerField()
                )
            ).order_by('search_priority', 'school_name')
        
        # 分页
        paginator = Paginator(queryset, page_size)
        schools_page = paginator.get_page(page)
        
        # 序列化数据
        schools_data = [serialize_secondary_school(school) for school in schools_page]
        
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
def secondary_school_detail(request, school_id):
    """
    获取中学详情（从 tb_secondary_schools 表）
    GET /api/schools/secondary/{id}
    """
    try:
        school_id = int(school_id)
        
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
def secondary_schools_stats(request):
    """
    获取中学统计信息（从 tb_secondary_schools 表）
    GET /api/schools/secondary/stats
    """
    try:
        # 构建查询条件
        queryset = TbSecondarySchools.objects.all()
        
        # 计算统计信息
        total_schools = queryset.count()
        
        # 按地区统计
        district_stats = {}
        districts = queryset.values_list('district', flat=True).distinct()
        for district in districts:
            if district:
                count = queryset.filter(district=district).count()
                district_stats[district] = count
        
        # 按学校类别统计
        category_stats = {}
        categories = queryset.values_list('school_category', flat=True).distinct()
        for category in categories:
            if category:
                count = queryset.filter(school_category=category).count()
                category_stats[category] = count
        
        # 按学校组别统计
        group_stats = {}
        groups = queryset.values_list('school_group', flat=True).distinct()
        for group in groups:
            if group:
                count = queryset.filter(school_group=group).count()
                group_stats[group] = count
        
        # 按性别统计
        gender_stats = {}
        genders = queryset.values_list('student_gender', flat=True).distinct()
        for gender in genders:
            if gender:
                count = queryset.filter(student_gender=gender).count()
                gender_stats[gender] = count
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total_schools,
                "districtStats": district_stats,
                "categoryStats": category_stats,
                "groupStats": group_stats,
                "genderStats": gender_stats
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })

