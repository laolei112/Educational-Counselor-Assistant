from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, Value, IntegerField
from backend.models.tb_primary_schools import TbPrimarySchools
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
        "type": "primary",  # 固定为小学
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
        
        # 中学联系（一条龙/直属/联系中学）
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
def primary_schools_list(request):
    """
    获取小学列表
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
        keyword = request.GET.get('keyword')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 20))
        
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
            queryset = queryset.filter(teaching_language__icontains=teaching_language)
            
        if keyword:
            # 使用 Case 和 When 来实现排序：校名包含关键词的排在前面
            queryset = queryset.filter(
                Q(school_name__icontains=keyword) | 
                Q(district__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(school_category__icontains=keyword) |
                Q(religion__icontains=keyword) |
                Q(school_net__icontains=keyword) |
                Q(teaching_language__icontains=keyword)
            ).annotate(
                # 添加排序权重：校名包含关键词的权重最高
                search_priority=Case(
                    When(school_name__icontains=keyword, then=Value(1)),  # 校名包含关键词，优先级最高
                    When(district__icontains=keyword, then=Value(2)),  # 地区包含关键词
                    When(address__icontains=keyword, then=Value(3)),  # 地址包含关键词
                    When(school_category__icontains=keyword, then=Value(4)),  # 分类包含关键词
                    When(religion__icontains=keyword, then=Value(5)),  # 宗教包含关键词
                    When(school_net__icontains=keyword, then=Value(6)),  # 校网包含关键词
                    When(teaching_language__icontains=keyword, then=Value(7)),  # 教学语言包含关键词
                    default=Value(8),
                    output_field=IntegerField()
                )
            ).order_by('search_priority', 'school_name')  # 按优先级和校名排序
        else:
            # 默认按学校名称排序
            queryset = queryset.order_by('school_name')
        
        # 分页
        paginator = Paginator(queryset, page_size)
        schools_page = paginator.get_page(page)
        
        # 序列化数据
        schools_data = [serialize_primary_school(school) for school in schools_page]
        
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
def primary_school_detail(request, school_id):
    """
    获取小学详情
    GET /api/schools/primary/{id}/
    """
    try:
        school_id = int(school_id)
        
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
    获取小学统计信息
    GET /api/schools/primary/stats/
    """
    try:
        # 计算统计信息
        queryset = TbPrimarySchools.objects.all()
        total_schools = queryset.count()
        
        # 按类型统计
        category_stats = {}
        categories = queryset.values_list('school_category', flat=True).distinct()
        for category in categories:
            if category:
                count = queryset.filter(school_category=category).count()
                category_stats[category] = count
        
        # 按地区统计
        district_stats = {}
        districts = queryset.values_list('district', flat=True).distinct()
        for district in districts:
            if district:
                count = queryset.filter(district=district).count()
                district_stats[district] = count
        
        # 按性别统计
        gender_stats = {}
        genders = queryset.values_list('student_gender', flat=True).distinct()
        for gender in genders:
            if gender:
                count = queryset.filter(student_gender=gender).count()
                gender_stats[gender] = count
        
        # 按宗教统计
        religion_stats = {}
        religions = queryset.values_list('religion', flat=True).distinct()
        for religion in religions:
            if religion:
                count = queryset.filter(religion=religion).count()
                religion_stats[religion] = count
        
        # 按校网统计
        school_net_stats = {}
        school_nets = queryset.values_list('school_net', flat=True).distinct()
        for school_net in school_nets:
            if school_net and school_net != '/':  # 排除私立学校的 '/'
                count = queryset.filter(school_net=school_net).count()
                school_net_stats[school_net] = count
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total_schools,
                "categoryStats": category_stats,
                "districtStats": district_stats,
                "genderStats": gender_stats,
                "religionStats": religion_stats,
                "schoolNetStats": school_net_stats
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
    """
    try:
        queryset = TbPrimarySchools.objects.all()
        
        # 获取所有可用的筛选选项
        districts = list(queryset.values_list('district', flat=True).distinct().order_by('district'))
        districts = [d for d in districts if d]  # 过滤空值
        
        categories = list(queryset.values_list('school_category', flat=True).distinct().order_by('school_category'))
        categories = [c for c in categories if c]  # 过滤空值
        
        genders = list(queryset.values_list('student_gender', flat=True).distinct().order_by('student_gender'))
        genders = [g for g in genders if g]  # 过滤空值
        
        religions = list(queryset.values_list('religion', flat=True).distinct().order_by('religion'))
        religions = [r for r in religions if r]  # 过滤空值
        
        school_nets = list(queryset.values_list('school_net', flat=True).distinct().order_by('school_net'))
        school_nets = [s for s in school_nets if s and s != '/']  # 过滤空值和私立学校标记
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "districts": districts,
                "categories": categories,
                "genders": genders,
                "religions": religions,
                "schoolNets": school_nets
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })

