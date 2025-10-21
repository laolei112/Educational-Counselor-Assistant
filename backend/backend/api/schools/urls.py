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
    secondary_schools_stats_optimized
)

urlpatterns = [
    # 通用接口（已废弃，不再使用）
    # re_path(r'^$', views.schools_list, name='schools_list'),
    # re_path(r'^stats/$', views.schools_stats, name='schools_stats'),
    # re_path(r'^(?P<school_id>\d+)/$', views.school_detail, name='school_detail'),
    
    # 小学接口（使用优化后的视图）
    re_path(r'^primary/$', primary_schools_list_optimized, name='primary_schools_list'),
    re_path(r'^primary/stats/$', primary_schools_stats_optimized, name='primary_schools_stats'),
    re_path(r'^primary/filters/$', primary_schools_filters_optimized, name='primary_schools_filters'),
    re_path(r'^primary/(?P<school_id>\d+)/$', primary_school_detail_optimized, name='primary_school_detail'),
    
    # 中学接口（使用优化后的视图）
    re_path(r'^secondary/$', secondary_schools_list_optimized, name='secondary_schools_list'),
    re_path(r'^secondary/stats/$', secondary_schools_stats_optimized, name='secondary_schools_stats'),
    re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_school_detail_optimized, name='secondary_school_detail'),
] 