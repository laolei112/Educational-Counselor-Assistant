"""
Django 应用配置
在应用启动时初始化定时任务调度器
"""
from django.apps import AppConfig
import os


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    verbose_name = '后端应用'
    
    def ready(self):
        """
        应用准备就绪时执行
        注意: 在开发环境下，Django的自动重载会导致ready()被调用两次
        """
        # 只在主进程中启动调度器（避免在runserver的reload进程中重复启动）
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            from backend.scheduler import start_scheduler
            from common.logger import loginfo
            
            try:
                # 启动缓存预热调度器
                scheduler = start_scheduler()
                loginfo("✓ 缓存预热调度器已在应用启动时自动启动")
                
                # 可选: 打印所有定时任务
                jobs = scheduler.get_jobs()
                loginfo(f"已配置 {len(jobs)} 个定时任务:")
                for job in jobs:
                    loginfo(f"  - {job['name']}: 下次执行时间 {job['next_run']}")
                    
            except Exception as e:
                loginfo(f"⚠ 调度器启动失败: {str(e)}")

