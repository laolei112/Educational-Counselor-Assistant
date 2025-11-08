from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.db import connection
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.utils.text_converter import normalize_keyword
from backend.utils.cache import CacheManager
from common.logger import loginfo
import json
import time


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
    # 性能监控：记录开始时间
    start_time = time.time()
    step_times = {}
    step_start = time.time()
    
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
        
        step_times['param_parse'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
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
        
        # if teaching_language:
        #     queryset = queryset.filter(teaching_language__icontains=teaching_language)
            
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
        
        step_times['query_build'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 优化COUNT查询：使用缓存避免重复执行COUNT(*)
        # 记录查询前的SQL状态和时间
        queries_before_count = len(connection.queries)
        query_start_time = time.time()
        
        # 获取查询SQL用于诊断
        count_sql = str(queryset.query)
        
        # 对于无WHERE条件的COUNT，优化为使用主键索引
        # 检查是否有WHERE条件
        has_where = any([category, district, school_net, gender, religion, teaching_language, keyword])
        
        # 执行COUNT查询
        if not has_where:
            # 无WHERE条件时，使用更高效的COUNT方式
            # 直接使用主键索引而不是排序索引
            total = TbPrimarySchools.objects.only('id').count()
        else:
            # 有WHERE条件时，使用正常的COUNT
            total = queryset.count()
        
        # 记录查询执行完成的时间
        query_end_time = time.time()
        db_execution_time = (query_end_time - query_start_time) * 1000
        
        # 记录查询后的SQL状态
        queries_after_count = len(connection.queries)
        count_query_time = (query_end_time - step_start) * 1000
        
        # 获取实际执行的SQL（如果Django记录了）
        actual_sql = None
        db_time = 0
        if queries_after_count > queries_before_count:
            # Django记录了查询
            actual_sql = connection.queries[-1].get('sql', 'N/A')
            db_time = float(connection.queries[-1].get('time', 0)) * 1000  # 转换为ms
        else:
            # 可能使用了缓存或连接池，没有记录
            actual_sql = 'Not logged by Django'
            # 使用实际测量的时间
            db_time = db_execution_time
        
        # 计算Python层面的延迟（总耗时 - 数据库耗时）
        python_overhead = count_query_time - db_time
        
        step_times['count_query'] = count_query_time
        
        # 如果COUNT查询慢，记录详细诊断信息
        if count_query_time > 200:  # 超过200ms认为是慢查询
            # 获取查询参数用于诊断
            query_params = {
                'category': category,
                'district': district,
                'school_net': school_net,
                'gender': gender,
                'religion': religion,
                'teaching_language': teaching_language,
                'keyword': keyword,
                'has_filters': any([category, district, school_net, gender, religion, teaching_language, keyword])
            }
            
            # 记录慢查询诊断信息
            loginfo(
                f"[SLOW_COUNT] GET /api/schools/primary/ | "
                f"CountQuery: {count_query_time:.2f}ms | "
                f"DBTime: {db_time:.2f}ms | "
                f"PythonOverhead: {python_overhead:.2f}ms | "
                f"Params: {json.dumps(query_params, ensure_ascii=False)} | "
                f"SQL: {actual_sql[:500] if actual_sql else 'N/A'}"
            )
            
            # 如果Python层面延迟很大，记录额外诊断信息
            if python_overhead > 500:  # Python层面延迟超过500ms
                loginfo(
                    f"[HIGH_PYTHON_OVERHEAD] Python overhead: {python_overhead:.2f}ms | "
                    f"This may indicate connection pool issues, network latency, or ORM overhead"
                )
            
            # 尝试获取EXPLAIN信息和数据库状态（如果可能）
            try:
                # 获取EXPLAIN查询计划
                if actual_sql and actual_sql != 'N/A' and actual_sql != 'Not logged by Django':
                    # 将SELECT COUNT(*)转换为EXPLAIN格式
                    explain_sql = actual_sql.replace('SELECT COUNT(*)', 'EXPLAIN SELECT COUNT(*)', 1)
                    with connection.cursor() as cursor:
                        cursor.execute(explain_sql)
                        columns = [col[0] for col in cursor.description]
                        explain_result = cursor.fetchone()
                        if explain_result:
                            explain_dict = dict(zip(columns, explain_result))
                            # 记录关键信息
                            explain_info = {
                                'select_type': explain_dict.get('select_type', 'N/A'),
                                'type': explain_dict.get('type', 'N/A'),
                                'possible_keys': explain_dict.get('possible_keys', 'N/A'),
                                'key': explain_dict.get('key', 'N/A'),
                                'key_len': explain_dict.get('key_len', 'N/A'),
                                'rows': explain_dict.get('rows', 'N/A'),
                                'Extra': explain_dict.get('Extra', 'N/A')
                            }
                            loginfo(f"[EXPLAIN] {json.dumps(explain_info, ensure_ascii=False)}")
                
                # 检查数据库连接状态和锁等待
                with connection.cursor() as cursor:
                    # 检查当前连接数
                    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                    threads_connected = cursor.fetchone()
                    
                    # 检查锁等待
                    cursor.execute("""
                        SELECT COUNT(*) as waiting_queries 
                        FROM information_schema.processlist 
                        WHERE State LIKE '%lock%' OR State LIKE '%Waiting%'
                    """)
                    waiting_queries = cursor.fetchone()
                    
                    # 检查慢查询
                    cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
                    slow_queries = cursor.fetchone()
                    
                    db_status = {
                        'threads_connected': threads_connected[1] if threads_connected else 'N/A',
                        'waiting_queries': waiting_queries[0] if waiting_queries else 'N/A',
                        'slow_queries': slow_queries[1] if slow_queries else 'N/A'
                    }
                    loginfo(f"[DB_STATUS] {json.dumps(db_status, ensure_ascii=False)}")
            except Exception as e:
                # 诊断失败不影响主流程，但记录错误
                loginfo(f"[DIAGNOSTIC_ERROR] Failed to get diagnostic info: {str(e)}")
        step_start = time.time()
        
        # 计算分页信息
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # 使用切片获取当前页数据（避免Paginator的额外查询）
        schools_page = queryset[start_index:end_index]
        
        step_times['data_query'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
        # 序列化数据
        schools_data = [serialize_primary_school(school) for school in schools_page]
        
        step_times['serialize'] = (time.time() - step_start) * 1000
        step_start = time.time()
        
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
        
        step_times['response_build'] = (time.time() - step_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        # 记录性能日志
        loginfo(
            f"[PERF] GET /api/schools/primary/ (non-optimized) | "
            f"Total: {total_time:.2f}ms | "
            f"ParamParse: {step_times.get('param_parse', 0):.2f}ms | "
            f"QueryBuild: {step_times.get('query_build', 0):.2f}ms | "
            f"CountQuery: {step_times.get('count_query', 0):.2f}ms | "
            f"DataQuery: {step_times.get('data_query', 0):.2f}ms | "
            f"Serialize: {step_times.get('serialize', 0):.2f}ms | "
            f"ResponseBuild: {step_times.get('response_build', 0):.2f}ms | "
            f"Result: total={total}, page={page}, pageSize={page_size}, items={len(schools_data)}"
        )
        
        return JsonResponse(response_data)
        
    except ValueError as e:
        total_time = (time.time() - start_time) * 1000
        loginfo(f"[PERF] GET /api/schools/primary/ (non-optimized) - ERROR (ValueError) | Total: {total_time:.2f}ms | Error: {str(e)}")
        return JsonResponse({
            "code": 400,
            "message": f"参数错误: {str(e)}",
            "success": False,
            "data": None
        })
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        loginfo(f"[PERF] GET /api/schools/primary/ (non-optimized) - ERROR | Total: {total_time:.2f}ms | Error: {str(e)}")
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
    
    性能优化：
    1. 使用单次查询获取所有字段，减少数据库查询次数（从5次减少到1次）
    2. 在Python中处理去重和排序，避免多次数据库扫描
    """
    try:
        # 优化：使用单次查询获取所有需要的字段，而不是每个字段一个查询
        # 这样可以减少数据库查询次数从5次减少到1次
        all_data = TbPrimarySchools.objects.values(
            'district', 
            'school_category', 
            'school_net', 
            'student_gender', 
            'religion'
        ).distinct()
        
        # 在Python中处理去重和排序，避免多次数据库扫描
        districts_set = set()
        categories_set = set()
        school_nets_set = set()
        genders_set = set()
        religions_set = set()
        
        for item in all_data:
            if item.get('district'):
                districts_set.add(item['district'])
            if item.get('school_category'):
                categories_set.add(item['school_category'])
            if item.get('school_net') and item['school_net'] != '/':  # 过滤空值和私立学校标记
                school_nets_set.add(item['school_net'])
            if item.get('student_gender'):
                genders_set.add(item['student_gender'])
            if item.get('religion'):
                religions_set.add(item['religion'])
        
        # 转换为排序后的列表
        districts = sorted(districts_set)
        categories = sorted(categories_set)
        school_nets = sorted(school_nets_set)
        genders = sorted(genders_set)
        religions = sorted(religions_set)
        
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

