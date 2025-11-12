"""
调度器管理接口
提供查看和手动触发缓存预热的功能
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.management import call_command
from backend.scheduler import get_scheduler
from common.logger import loginfo
import time
import threading


@require_http_methods(["GET"])
def scheduler_status(request):
    """
    获取调度器状态
    GET /api/scheduler/status/
    """
    try:
        scheduler = get_scheduler()
        
        # 获取所有任务
        jobs = scheduler.get_jobs()
        
        return JsonResponse({
            'success': True,
            'data': {
                'running': scheduler.scheduler.running if scheduler.scheduler else False,
                'jobs': jobs,
                'total_jobs': len(jobs)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取调度器状态失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def trigger_warmup(request):
    """
    手动触发缓存预热
    POST /api/scheduler/warmup/
    
    参数:
        type: 预热类型 (all/primary/secondary/stats)
        async: 是否异步执行 (true/false, 默认false)
    """
    try:
        import json
        body = json.loads(request.body) if request.body else {}
        
        warmup_type = body.get('type', 'all')
        is_async = body.get('async', False)
        
        def run_warmup():
            """执行预热任务"""
            start_time = time.time()
            
            try:
                if warmup_type == 'primary':
                    call_command('warmup_cache', '--primary')
                elif warmup_type == 'secondary':
                    call_command('warmup_cache', '--secondary')
                elif warmup_type == 'stats':
                    call_command('warmup_cache', '--stats')
                else:
                    call_command('warmup_cache')
                
                elapsed = time.time() - start_time
                loginfo(f"手动触发缓存预热完成 (type={warmup_type})，耗时: {elapsed:.2f}秒")
                
            except Exception as e:
                loginfo(f"手动触发缓存预热失败: {str(e)}")
        
        if is_async:
            # 异步执行
            thread = threading.Thread(target=run_warmup)
            thread.daemon = True
            thread.start()
            
            return JsonResponse({
                'success': True,
                'message': f'缓存预热任务已提交 (type={warmup_type})，正在后台执行'
            })
        else:
            # 同步执行
            start_time = time.time()
            run_warmup()
            elapsed = time.time() - start_time
            
            return JsonResponse({
                'success': True,
                'message': f'缓存预热完成 (type={warmup_type})',
                'data': {
                    'elapsed_time': f'{elapsed:.2f}秒'
                }
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'触发缓存预热失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clear_and_warmup(request):
    """
    清除缓存并重新预热
    POST /api/scheduler/clear-and-warmup/
    
    适用场景：数据更新后需要刷新缓存
    """
    try:
        import json
        body = json.loads(request.body) if request.body else {}
        
        is_async = body.get('async', False)
        
        def run_clear_and_warmup():
            """执行清除和预热"""
            start_time = time.time()
            
            try:
                # 1. 清除缓存
                loginfo("清除所有学校相关缓存...")
                call_command('clear_cache', '--schools')
                
                # 2. 重新预热
                loginfo("重新预热缓存...")
                call_command('warmup_cache')
                
                elapsed = time.time() - start_time
                loginfo(f"清除并预热缓存完成，耗时: {elapsed:.2f}秒")
                
            except Exception as e:
                loginfo(f"清除并预热缓存失败: {str(e)}")
        
        if is_async:
            # 异步执行
            thread = threading.Thread(target=run_clear_and_warmup)
            thread.daemon = True
            thread.start()
            
            return JsonResponse({
                'success': True,
                'message': '清除并预热任务已提交，正在后台执行'
            })
        else:
            # 同步执行
            start_time = time.time()
            run_clear_and_warmup()
            elapsed = time.time() - start_time
            
            return JsonResponse({
                'success': True,
                'message': '清除并预热完成',
                'data': {
                    'elapsed_time': f'{elapsed:.2f}秒'
                }
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'清除并预热失败: {str(e)}'
        }, status=500)

