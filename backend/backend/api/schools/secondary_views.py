from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import F, Q
from backend.models.tb_secondary_schools import TbSecondarySchools
from backend.utils.text_converter import normalize_keyword
from backend.utils.cache import CacheManager
import json
import traceback
from common.logger import logerror


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
        
        # 优化COUNT查询：使用缓存避免重复执行COUNT(*)
        total = queryset.count()        
        # 计算分页信息
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 使用切片获取当前页数据（避免Paginator的额外查询）
        schools_page = queryset[start_index:end_index]
        
        # 序列化数据
        schools_data = [serialize_secondary_school(school) for school in schools_page]
        
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
        logerror(f"服务器错误: {traceback.format_exc()}")
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
    获取中学统计信息（简化版本，只返回学校总数）
    GET /api/schools/secondary/stats
    """
    try:
        # 只返回所有学校的总数
        total_schools = TbSecondarySchools.objects.count()
        
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
    优化后的中学筛选器接口
    GET /api/schools/secondary/filters/
    """
    try:        
        # 获取所有可用的筛选选项（使用聚合查询）
        districts = list(TbSecondarySchools.objects.values_list('district', flat=True).distinct().order_by('district'))
        categories = list(TbSecondarySchools.objects.values_list('school_category', flat=True).distinct().order_by('school_category'))
        school_groups = list(TbSecondarySchools.objects.values_list('school_group', flat=True).distinct().order_by('school_group'))
        genders = list(TbSecondarySchools.objects.values_list('student_gender', flat=True).distinct().order_by('student_gender'))
        religions = list(TbSecondarySchools.objects.values_list('religion', flat=True).distinct().order_by('religion'))
        
        # 过滤掉None和空字符串
        districts = [d for d in districts if d]
        categories = [c for c in categories if c]
        school_groups = [s for s in school_groups if s]
        genders = [g for g in genders if g]
        religions = [r for r in religions if r]
        
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
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        })

