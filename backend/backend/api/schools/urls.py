from django.urls import re_path
from . import views
from . import secondary_views
from . import primary_views
# 导入优化后的视图
from .primary_views_optimized import (
    primary_schools_list_optimized,
    primary_school_detail_optimized,
    primary_schools_stats_optimized,
    primary_schools_filters_optimized
)
from .secondary_views_optimized import (
    secondary_schools_list_optimized,
    secondary_school_detail_optimized,
    secondary_schools_stats_optimized,
    secondary_schools_filters_optimized
)

urlpatterns = [
    # 通用接口（已废弃，不再使用）
    # re_path(r'^$', views.schools_list, name='schools_list'),
    # re_path(r'^stats/$', views.schools_stats, name='schools_stats'),
    # re_path(r'^(?P<school_id>\d+)/$', views.school_detail, name='school_detail'),
    # 使用优化版本（已添加缓存和性能优化）
    re_path(r'^primary/$', primary_schools_list_optimized, name='primary_schools_list'),
    re_path(r'^primary/stats/$', primary_schools_stats_optimized, name='primary_schools_stats'),
    re_path(r'^primary/filters/$', primary_schools_filters_optimized, name='primary_schools_filters'),
    re_path(r'^primary/(?P<school_id>\d+)/$', primary_school_detail_optimized, name='primary_school_detail'),
    
    # 原版本（已废弃，保留作为备份）
    # re_path(r'^primary/$', primary_views.primary_schools_list, name='primary_schools_list'),
    # re_path(r'^primary/stats/$', primary_views.primary_schools_stats, name='primary_schools_stats'),
    # re_path(r'^primary/filters/$', primary_views.primary_schools_filters, name='primary_schools_filters'),
    # re_path(r'^primary/(?P<school_id>\d+)/$', primary_views.primary_school_detail, name='primary_school_detail'),

    # 使用优化版本（已添加缓存和性能优化）
    re_path(r'^secondary/$', secondary_schools_list_optimized, name='secondary_schools_list'),
    re_path(r'^secondary/stats/$', secondary_schools_stats_optimized, name='secondary_schools_stats'),
    re_path(r'^secondary/filters/$', secondary_schools_filters_optimized, name='secondary_schools_filters'),
    re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_school_detail_optimized, name='secondary_school_detail'),
    
    # 原版本（已废弃，保留作为备份）
    # re_path(r'^secondary/$', secondary_views.secondary_schools_list, name='secondary_schools_list'),
    # re_path(r'^secondary/stats/$', secondary_views.secondary_schools_stats, name='secondary_schools_stats'),
    # re_path(r'^secondary/filters/$', secondary_views.secondary_schools_filters, name='secondary_schools_filters'),
    # re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_views.secondary_school_detail, name='secondary_school_detail'),

    
    # # 小学接口（使用优化后的视图）
    # re_path(r'^primary/$', primary_schools_list_optimized, name='primary_schools_list'),
    # re_path(r'^primary/stats/$', primary_schools_stats_optimized, name='primary_schools_stats'),
    # re_path(r'^primary/filters/$', primary_schools_filters_optimized, name='primary_schools_filters'),
    # re_path(r'^primary/(?P<school_id>\d+)/$', primary_school_detail_optimized, name='primary_school_detail'),
    
    # # 中学接口（使用优化后的视图）
    # re_path(r'^secondary/$', secondary_schools_list_optimized, name='secondary_schools_list'),
    # re_path(r'^secondary/stats/$', secondary_schools_stats_optimized, name='secondary_schools_stats'),
    # re_path(r'^secondary/filters/$', secondary_schools_filters_optimized, name='secondary_schools_filters'),
    # re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_school_detail_optimized, name='secondary_school_detail'),
] 