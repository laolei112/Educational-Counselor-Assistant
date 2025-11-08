from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.utils.text_converter import normalize_keyword
from backend.utils.cache import CacheManager
import json


def serialize_primary_school(school):
    """
    序列化小学数据为前端需要的格式
    """
    # 获取总班数
    total_classes = school.get_total_classes()
    
    return {
        "id": school.id,
        "name": school.school_name,
        "nameTraditional": school.school_name_traditional,
        "nameEnglish": school.school_name_english,
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
        
        # 中学联系信息
        "secondaryInfo": school.secondary_info if school.secondary_info else {},
        
        # 班级信息
        "schoolScale": {
            "classes": total_classes if total_classes is not None else 0,
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
        # Band1比例（优先使用生成列band1_rate，性能更好）
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
            ).order_by('-band1_rate', 'school_name')  # 按Band 1比例和校名排序
        else:
            # 默认按Band 1比例降序，比例相同时按学校名称排序
            # 使用生成列band1_rate（已通过SQL添加，可直接使用索引，性能大幅提升）
            queryset = queryset.order_by('-band1_rate', 'school_name')
        
        # 优化COUNT查询：使用缓存避免重复执行COUNT(*)
        total = queryset.count()        
        # 计算分页信息
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 使用切片获取当前页数据（避免Paginator的额外查询）
        schools_page = queryset[start_index:end_index]
        
        # 序列化数据
        schools_data = [serialize_primary_school(school) for school in schools_page]
        
        return JsonResponse({
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
    获取小学统计信息（简化版本，只返回学校总数）
    GET /api/schools/primary/stats/
    """
    try:
        # 只返回所有学校的总数
        total_schools = TbPrimarySchools.objects.count()
        
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

