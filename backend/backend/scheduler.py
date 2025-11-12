"""
定时任务调度器
使用 APScheduler 实现定时缓存预热

功能：
1. 每天凌晨 3:00 预热所有缓存
2. 每天上午 8:00 再次预热（上班高峰期前）
3. 每隔 2 小时预热筛选选项和统计信息
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management import call_command
from common.logger import loginfo, logerror
import time


class CacheScheduler:
    """缓存预热调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """设置定时任务"""
        
        # 任务1: 每天凌晨 3:00 完整预热
        self.scheduler.add_job(
            func=self._warmup_all_cache,
            trigger=CronTrigger(hour=3, minute=0),
            id='warmup_all_daily_3am',
            name='完整缓存预热(凌晨3点)',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300  # 5分钟容错时间
        )
        loginfo("已添加定时任务: 每天凌晨3:00完整预热缓存")
        
        # 任务2: 每天上午 8:00 再次预热（高峰期前）
        self.scheduler.add_job(
            func=self._warmup_all_cache,
            trigger=CronTrigger(hour=8, minute=0),
            id='warmup_all_daily_8am',
            name='完整缓存预热(上午8点)',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300
        )
        loginfo("已添加定时任务: 每天上午8:00完整预热缓存")
        
        # 任务3: 每隔2小时预热统计和筛选选项
        self.scheduler.add_job(
            func=self._warmup_stats_cache,
            trigger=IntervalTrigger(hours=2),
            id='warmup_stats_interval',
            name='统计信息预热(每2小时)',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300
        )
        loginfo("已添加定时任务: 每2小时预热统计和筛选信息")
        
        # 任务4: 每天中午 12:00 预热（午间高峰期前）
        self.scheduler.add_job(
            func=self._warmup_school_lists,
            trigger=CronTrigger(hour=12, minute=0),
            id='warmup_lists_daily_12pm',
            name='学校列表预热(中午12点)',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300
        )
        loginfo("已添加定时任务: 每天中午12:00预热学校列表")
    
    def _warmup_all_cache(self):
        """完整预热所有缓存"""
        try:
            start_time = time.time()
            loginfo("开始完整缓存预热...")
            
            call_command('warmup_cache')
            
            elapsed = time.time() - start_time
            loginfo(f"完整缓存预热完成，耗时: {elapsed:.2f}秒")
            
        except Exception as e:
            logerror(f"完整缓存预热失败: {str(e)}")
    
    def _warmup_stats_cache(self):
        """预热统计信息"""
        try:
            start_time = time.time()
            loginfo("开始预热统计信息...")
            
            call_command('warmup_cache', '--stats')
            
            elapsed = time.time() - start_time
            loginfo(f"统计信息预热完成，耗时: {elapsed:.2f}秒")
            
        except Exception as e:
            logerror(f"统计信息预热失败: {str(e)}")
    
    def _warmup_school_lists(self):
        """预热学校列表"""
        try:
            start_time = time.time()
            loginfo("开始预热学校列表...")
            
            call_command('warmup_cache', '--primary')
            call_command('warmup_cache', '--secondary')
            
            elapsed = time.time() - start_time
            loginfo(f"学校列表预热完成，耗时: {elapsed:.2f}秒")
            
        except Exception as e:
            logerror(f"学校列表预热失败: {str(e)}")
    
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            loginfo("缓存预热调度器已启动")
            
            # 立即执行一次预热（可选）
            # self._warmup_all_cache()
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            loginfo("缓存预热调度器已关闭")
    
    def get_jobs(self):
        """获取所有任务信息"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs


# 全局调度器实例
_scheduler_instance = None


def get_scheduler():
    """获取调度器单例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = CacheScheduler()
    return _scheduler_instance


def start_scheduler():
    """启动调度器"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def shutdown_scheduler():
    """关闭调度器"""
    global _scheduler_instance
    if _scheduler_instance is not None:
        _scheduler_instance.shutdown()
        _scheduler_instance = None

