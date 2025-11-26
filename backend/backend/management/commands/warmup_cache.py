"""
缓存预热管理命令
提前加载常用数据到缓存中，提升用户访问速度

用法:
    python manage.py warmup_cache              # 预热所有缓存
    python manage.py warmup_cache --primary    # 只预热小学缓存
    python manage.py warmup_cache --secondary  # 只预热中学缓存
    python manage.py warmup_cache --stats      # 只预热统计信息
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import close_old_connections
from django.db.models import Q
from backend.models.tb_primary_schools import TbPrimarySchools
from backend.models.tb_secondary_schools import TbSecondarySchools
from backend.api.schools.primary_views import (
    serialize_primary_school, 
    get_cache_key_for_query,
    # get_primary_filters
)
from backend.api.schools.secondary_views import (
    serialize_secondary_school_for_list,
    serialize_secondary_school,
    get_cache_key_for_secondary_query
)
from backend.utils.cache import CacheManager
from common.logger import loginfo
import json
import time


class Command(BaseCommand):
    help = '预热缓存 - 提前加载常用数据到缓存'

    def add_arguments(self, parser):
        parser.add_argument(
            '--primary',
            action='store_true',
            help='只预热小学缓存',
        )
        parser.add_argument(
            '--secondary',
            action='store_true',
            help='只预热中学缓存',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='只预热统计信息',
        )
        parser.add_argument(
            '--details',
            action='store_true',
            help='预热所有学校详情',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='显示详细信息',
        )

    def handle(self, *args, **options):
        # 确保在执行命令前关闭失效的数据库连接
        close_old_connections()
        
        start_time = time.time()
        self.verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.WARNING('开始预热缓存...'))
        self.stdout.write(self.style.WARNING('='*60))
        
        # 确定预热范围
        warmup_all = not any([
            options['primary'], 
            options['secondary'], 
            options['stats'],
            options['details']
        ])
        
        stats = {
            'primary': 0,
            'secondary': 0,
            'filters': 0,
            'stats': 0,
            'details': 0,
            'errors': 0
        }
        
        try:
            # 预热小学数据
            if warmup_all or options['primary']:
                self.stdout.write('\n📚 预热小学数据...')
                primary_count = self._warmup_primary_schools()
                stats['primary'] = primary_count
                self.stdout.write(self.style.SUCCESS(f'  ✓ 小学缓存预热完成：{primary_count} 条'))
            
            # 预热中学数据
            if warmup_all or options['secondary']:
                self.stdout.write('\n🏫 预热中学数据...')
                secondary_count = self._warmup_secondary_schools()
                stats['secondary'] = secondary_count
                self.stdout.write(self.style.SUCCESS(f'  ✓ 中学缓存预热完成：{secondary_count} 条'))
            
            # # 预热筛选选项
            # if warmup_all:
            #     self.stdout.write('\n🔍 预热筛选选项...')
            #     filter_count = self._warmup_filters()
            #     stats['filters'] = filter_count
            #     self.stdout.write(self.style.SUCCESS(f'  ✓ 筛选选项预热完成：{filter_count} 条'))
            
            # 预热统计信息
            if warmup_all or options['stats']:
                self.stdout.write('\n📊 预热统计信息...')
                stats_count = self._warmup_stats()
                stats['stats'] = stats_count
                self.stdout.write(self.style.SUCCESS(f'  ✓ 统计信息预热完成：{stats_count} 条'))
            
            # 预热所有学校详情
            if warmup_all or options['details']:
                self.stdout.write('\n📝 预热所有学校详情...')
                details_count = self._warmup_all_details()
                stats['details'] = details_count
                self.stdout.write(self.style.SUCCESS(f'  ✓ 学校详情预热完成：{details_count} 条'))
            
            elapsed_time = time.time() - start_time
            
            # 输出总结
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('✓ 缓存预热完成！'))
            self.stdout.write('='*60)
            self.stdout.write(f'  小学缓存：{stats["primary"]} 条')
            self.stdout.write(f'  中学缓存：{stats["secondary"]} 条')
            self.stdout.write(f'  筛选选项：{stats["filters"]} 条')
            self.stdout.write(f'  统计信息：{stats["stats"]} 条')
            self.stdout.write(f'  学校详情：{stats["details"]} 条')
            self.stdout.write(f'  失败数量：{stats["errors"]} 条')
            self.stdout.write(f'  总耗时：{elapsed_time:.2f} 秒')
            self.stdout.write('='*60)
            
            loginfo(f"Cache warmup completed: {stats}, time: {elapsed_time:.2f}s")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ 缓存预热失败: {str(e)}'))
            raise

    def _warmup_primary_schools(self):
        """预热小学列表数据"""
        count = 0
        
        # 常用查询组合 - 注意：参数格式必须与 API 视图中的 cache_params 完全一致
        # API 中使用：category, district, school_net, gender, religion, teaching_language, keyword, page, page_size
        common_queries = [
            # 1. 首页默认查询（第一页）- 所有筛选参数为 None
            {
                'category': None,
                'district': None,
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            # 2. 常见片区
            {
                'category': None,
                'district': '港岛（中西区）',
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': '九龙（油尖旺区）',
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': '新界（沙田区）',
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            # 3. 常见校网
            {
                'category': None,
                'district': None,
                'school_net': '11',
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': None,
                'school_net': '41',
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            # 4. 常见类别
            {
                'category': '官立',
                'district': None,
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': '资助',
                'district': None,
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': '私立',
                'district': None,
                'school_net': None,
                'gender': None,
                'religion': None,
                'teaching_language': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
        ]
        
        for cache_params in common_queries:
            try:
                if self.verbose:
                    self.stdout.write(f'  预热查询: {cache_params}')
                
                # 构建查询
                queryset = TbPrimarySchools.objects.all()
                
                # 应用筛选条件
                if cache_params.get('district'):
                    queryset = queryset.filter(district=cache_params['district'])
                if cache_params.get('school_net'):
                    queryset = queryset.filter(school_net=cache_params['school_net'])
                if cache_params.get('category'):
                    queryset = queryset.filter(school_category=cache_params['category'])
                if cache_params.get('gender'):
                    queryset = queryset.filter(student_gender=cache_params['gender'])
                if cache_params.get('religion'):
                    queryset = queryset.filter(religion=cache_params['religion'])
                if cache_params.get('teaching_language'):
                    queryset = queryset.filter(teaching_language__icontains=cache_params['teaching_language'])
                if cache_params.get('keyword'):
                    keyword = cache_params['keyword']
                    queryset = queryset.filter(
                        Q(school_name__icontains=keyword) |
                        Q(school_name_traditional__icontains=keyword) |
                        Q(school_name_english__icontains=keyword) |
                        Q(district__icontains=keyword) |
                        Q(school_net__icontains=keyword)
                    )
                
                # 分页
                page = cache_params.get('page', 1)
                page_size = cache_params.get('page_size', 20)
                offset = (page - 1) * page_size
                
                # 获取数据
                schools = list(queryset[offset:offset + page_size])
                total = queryset.count()
                
                # 序列化
                schools_data = [serialize_primary_school(s) for s in schools]
                
                # 构建响应数据
                result = {
                    'list': schools_data,
                    'page': page,
                    'pageSize': page_size,
                    'total': total,
                    'totalPages': (total + page_size - 1) // page_size
                }
                
                # 生成缓存键 - 使用与 API 完全一致的参数格式
                cache_key = get_cache_key_for_query(cache_params)
                
                # 缓存数据（30分钟）
                cache.set(cache_key, result, timeout=1800)
                count += 1
                
                if self.verbose:
                    self.stdout.write(f'    ✓ 已缓存 {len(schools_data)} 条记录，缓存键: {cache_key}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ 失败: {cache_params} - {str(e)}'))
                continue
        
        return count

    def _warmup_secondary_schools(self):
        """预热中学列表数据"""
        count = 0
        
        # 常用查询组合 - 注意：参数格式必须与 API 视图中的 cache_params 完全一致
        # API 中使用：category, district, school_group, gender, religion, keyword, page, page_size
        common_queries = [
            # 1. 首页默认查询 - 所有筛选参数为 None
            {
                'category': None,
                'district': None,
                'school_group': None,
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            # 2. 常见片区
            {
                'category': None,
                'district': '港岛区',
                'school_group': None,
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': '九龙城',
                'school_group': None,
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': '沙田',
                'school_group': None,
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            # 3. 常见学校组别 (Banding)
            {
                'category': None,
                'district': None,
                'school_group': '1A',
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': None,
                'school_group': '1B',
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            {
                'category': None,
                'district': None,
                'school_group': '2A',
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
            # 4. 组合查询
            {
                'category': None,
                'district': '九龙城',
                'school_group': '1A',
                'gender': None,
                'religion': None,
                'keyword': None,
                'page': 1,
                'page_size': 20
            },
        ]
        
        for cache_params in common_queries:
            try:
                if self.verbose:
                    self.stdout.write(f'  预热查询: {cache_params}')
                
                # 构建查询
                queryset = TbSecondarySchools.objects.all()
                
                # 应用筛选条件
                if cache_params.get('district'):
                    queryset = queryset.filter(district=cache_params['district'])
                if cache_params.get('school_group'):
                    queryset = queryset.filter(school_group=cache_params['school_group'])
                if cache_params.get('category'):
                    queryset = queryset.filter(school_category=cache_params['category'])
                if cache_params.get('gender'):
                    queryset = queryset.filter(student_gender=cache_params['gender'])
                if cache_params.get('religion'):
                    queryset = queryset.filter(religion=cache_params['religion'])
                if cache_params.get('keyword'):
                    keyword = cache_params['keyword']
                    queryset = queryset.filter(
                        Q(school_name__icontains=keyword) |
                        Q(school_name_traditional__icontains=keyword) |
                        Q(school_name_english__icontains=keyword) |
                        Q(district__icontains=keyword)
                    )
                
                # 分页
                page = cache_params.get('page', 1)
                page_size = cache_params.get('page_size', 20)
                offset = (page - 1) * page_size
                
                # 获取数据
                schools = list(queryset[offset:offset + page_size])
                total = queryset.count()
                
                # 序列化（列表页使用精简版本）
                schools_data = [serialize_secondary_school_for_list(s) for s in schools]
                
                # 构建响应数据
                result = {
                    'list': schools_data,
                    'page': page,
                    'pageSize': page_size,
                    'total': total,
                    'totalPages': (total + page_size - 1) // page_size
                }
                
                # 生成缓存键 - 使用与 API 完全一致的参数格式
                cache_key = get_cache_key_for_secondary_query(cache_params)
                
                # 缓存数据（30分钟）
                cache.set(cache_key, result, timeout=1800)
                count += 1
                
                if self.verbose:
                    self.stdout.write(f'    ✓ 已缓存 {len(schools_data)} 条记录，缓存键: {cache_key}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ 失败: {cache_params} - {str(e)}'))
                continue
        
        return count

    # def _warmup_filters(self):
    #     """预热筛选选项"""
    #     count = 0
        
    #     try:
    #         # 预热小学筛选选项
    #         primary_filters = get_primary_filters()
    #         cache_key = 'primary_filters'
    #         cache.set(cache_key, primary_filters, timeout=3600)  # 1小时
    #         count += 1
            
    #         if self.verbose:
    #             self.stdout.write(f'  ✓ 小学筛选选项已缓存')
            
    #         # 预热中学筛选选项
    #         secondary_districts = list(
    #             TbSecondarySchools.objects
    #             .values_list('district', flat=True)
    #             .distinct()
    #             .order_by('district')
    #         )
    #         secondary_groups = list(
    #             TbSecondarySchools.objects
    #             .exclude(Q(school_group__isnull=True) | Q(school_group=''))
    #             .values_list('school_group', flat=True)
    #             .distinct()
    #             .order_by('school_group')
    #         )
            
    #         secondary_filters = {
    #             'districts': secondary_districts,
    #             'schoolGroups': secondary_groups
    #         }
            
    #         cache_key = 'secondary_filters'
    #         cache.set(cache_key, secondary_filters, timeout=3600)  # 1小时
    #         count += 1
            
    #         if self.verbose:
    #             self.stdout.write(f'  ✓ 中学筛选选项已缓存')
                
    #     except Exception as e:
    #         self.stdout.write(self.style.ERROR(f'  ✗ 筛选选项缓存失败: {str(e)}'))
        
    #     return count

    def _warmup_stats(self):
        """预热统计信息"""
        count = 0
        
        try:
            # 小学统计
            primary_total = TbPrimarySchools.objects.count()
            primary_stats = {
                'totalSchools': primary_total,
                'openApplications': 0  # 需要根据实际业务逻辑计算
            }
            cache_key = CacheManager.generate_cache_key(
                CacheManager.PREFIX_SCHOOL_STATS,
                type='primary'
            )
            cache.set(cache_key, primary_stats, timeout=3600)
            count += 1
            
            if self.verbose:
                self.stdout.write(f'  ✓ 小学统计: {primary_total} 所')
            
            # 中学统计
            secondary_total = TbSecondarySchools.objects.count()
            secondary_stats = {
                'totalSchools': secondary_total,
                'openApplications': 0
            }
            cache_key = CacheManager.generate_cache_key(
                CacheManager.PREFIX_SCHOOL_STATS,
                type='secondary'
            )
            cache.set(cache_key, secondary_stats, timeout=3600)
            count += 1
            
            if self.verbose:
                self.stdout.write(f'  ✓ 中学统计: {secondary_total} 所')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ 统计信息缓存失败: {str(e)}'))
        
        return count

    def _warmup_all_details(self):
        """预热所有学校详情数据"""
        count = 0
        
        # 1. 小学详情
        try:
            primary_schools = TbPrimarySchools.objects.all()
            total_primary = primary_schools.count()
            if self.verbose:
                self.stdout.write(f'  正在预热 {total_primary} 所小学的详情...')
                
            for school in primary_schools:
                try:
                    cache_key = f"primary_school_detail:{school.id}"
                    data = serialize_primary_school(school)
                    cache.set(cache_key, data, timeout=86400) # 24小时
                    count += 1
                except Exception as e:
                    if self.verbose:
                        self.stdout.write(self.style.ERROR(f'    小学ID {school.id} 预热失败: {str(e)}'))
                    continue
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ 小学详情预热失败: {str(e)}'))

        # 2. 中学详情
        try:
            secondary_schools = TbSecondarySchools.objects.all()
            total_secondary = secondary_schools.count()
            if self.verbose:
                self.stdout.write(f'  正在预热 {total_secondary} 所中学的详情...')
                
            for school in secondary_schools:
                try:
                    cache_key = f"secondary_school_detail:{school.id}"
                    data = serialize_secondary_school(school)
                    cache.set(cache_key, data, timeout=86400) # 24小时
                    count += 1
                except Exception as e:
                    if self.verbose:
                        self.stdout.write(self.style.ERROR(f'    中学ID {school.id} 预热失败: {str(e)}'))
                    continue
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ 中学详情预热失败: {str(e)}'))
            
        return count

