"""
清除缓存的管理命令
用法: python manage.py clear_cache [--all|--schools]
"""
from django.core.management.base import BaseCommand
from backend.utils.cache import CacheManager


class Command(BaseCommand):
    help = '清除应用缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='清除所有缓存',
        )
        parser.add_argument(
            '--schools',
            action='store_true',
            help='只清除学校相关缓存',
        )

    def handle(self, *args, **options):
        if options['all']:
            self.stdout.write('清除所有缓存...')
            from django.core.cache import cache
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ 已清除所有缓存'))
        
        elif options['schools']:
            self.stdout.write('清除学校相关缓存...')
            CacheManager.clear_school_cache()
            self.stdout.write(self.style.SUCCESS('✓ 已清除学校缓存'))
        
        else:
            self.stdout.write(self.style.WARNING(
                '请指定清除范围：--all 或 --schools'
            ))

