from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Mock data - same as frontend for consistency
MOCK_SCHOOLS = [
    # 中学数据
    {
        "id": 1,
        "name": "圣保罗男女中学",
        "type": "secondary",
        "category": "elite",
        "band1Rate": 94,
        "applicationStatus": "open",
        "district": "中西区",
        "schoolNet": "校网11",
        "tuition": 36800,
        "gender": "coed",
        "feederSchools": ["圣保罗书院"],
        "linkedUniversities": ["香港大学"]
    },
    {
        "id": 2,
        "name": "喇沙书院",
        "type": "secondary",
        "category": "traditional",
        "band1Rate": 88,
        "applicationStatus": "closed",
        "district": "九龙城",
        "schoolNet": "校网41",
        "tuition": 28500,
        "gender": "boys",
        "feederSchools": ["喇沙小学"],
        "linkedUniversities": ["香港中文大学"]
    },
    {
        "id": 3,
        "name": "拔萃女书院",
        "type": "secondary",
        "category": "direct",
        "band1Rate": 96,
        "applicationStatus": "open",
        "district": "九龙城",
        "schoolNet": "校网41",
        "tuition": 42000,
        "gender": "girls",
        "feederSchools": ["拔萃女小学"],
        "linkedUniversities": ["香港大学", "香港中文大学"]
    },
    # 小学数据
    {
        "id": 4,
        "name": "拔萃女小学",
        "type": "primary",
        "category": "direct",
        "band1Rate": 98,
        "applicationStatus": "open",
        "district": "九龙城",
        "schoolNet": "校网41",
        "tuition": 38000,
        "gender": "girls",
        "feederSchools": [],
        "linkedUniversities": ["拔萃女书院"]
    },
    {
        "id": 5,
        "name": "圣保罗男女中学附属小学",
        "type": "primary",
        "category": "elite",
        "band1Rate": 95,
        "applicationStatus": "open",
        "district": "南区",
        "schoolNet": "校网18",
        "tuition": 32000,
        "gender": "coed",
        "feederSchools": [],
        "linkedUniversities": ["圣保罗男女中学"]
    },
    {
        "id": 6,
        "name": "喇沙小学",
        "type": "primary",
        "category": "traditional",
        "band1Rate": 92,
        "applicationStatus": "closed",
        "district": "九龙城",
        "schoolNet": "校网41",
        "tuition": 0,
        "gender": "boys",
        "feederSchools": [],
        "linkedUniversities": ["喇沙书院"]
    }
]


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
        
        # 过滤数据
        filtered_schools = MOCK_SCHOOLS.copy()
        
        if school_type:
            filtered_schools = [s for s in filtered_schools if s['type'] == school_type]
        
        if category:
            filtered_schools = [s for s in filtered_schools if s['category'] == category]
            
        if district:
            filtered_schools = [s for s in filtered_schools if s['district'] == district]
            
        if application_status:
            filtered_schools = [s for s in filtered_schools if s['applicationStatus'] == application_status]
            
        if keyword:
            filtered_schools = [s for s in filtered_schools 
                              if keyword.lower() in s['name'].lower() or keyword.lower() in s['district'].lower()]
        
        # 分页
        total = len(filtered_schools)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        schools_page = filtered_schools[start_index:end_index]
        
        total_pages = (total + page_size - 1) // page_size
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "list": schools_page,
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
def school_detail(request, school_id):
    """
    获取学校详情
    GET /api/schools/{id}
    """
    try:
        school_id = int(school_id)
        school = next((s for s in MOCK_SCHOOLS if s['id'] == school_id), None)
        
        if not school:
            return JsonResponse({
                "code": 404,
                "message": "学校不存在",
                "success": False,
                "data": None
            })
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": school
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
def schools_stats(request):
    """
    获取学校统计信息
    GET /api/schools/stats
    """
    try:
        school_type = request.GET.get('type')
        
        # 过滤数据
        filtered_schools = MOCK_SCHOOLS.copy()
        if school_type:
            filtered_schools = [s for s in filtered_schools if s['type'] == school_type]
        
        # 计算统计信息
        total_schools = len(filtered_schools)
        open_applications = len([s for s in filtered_schools if s['applicationStatus'] == 'open'])
        
        return JsonResponse({
            "code": 200,
            "message": "成功",
            "success": True,
            "data": {
                "totalSchools": total_schools,
                "openApplications": open_applications
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "message": f"服务器错误: {str(e)}",
            "success": False,
            "data": None
        }) 