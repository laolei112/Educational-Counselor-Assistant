from django.urls import re_path
from . import views
from . import secondary_views
from . import primary_views


urlpatterns = [
    # 通用接口（已废弃，不再使用）
    # re_path(r'^$', views.schools_list, name='schools_list'),
    # re_path(r'^stats/$', views.schools_stats, name='schools_stats'),
    # re_path(r'^(?P<school_id>\d+)/$', views.school_detail, name='school_detail'),


    re_path(r'^primary/$', primary_views.primary_schools_list, name='primary_schools_list'),
    re_path(r'^primary/stats/$', primary_views.primary_schools_stats, name='primary_schools_stats'),
    re_path(r'^primary/filters/$', primary_views.primary_schools_filters, name='primary_schools_filters'),
    re_path(r'^primary/(?P<school_id>\d+)/recommendations/$', primary_views.primary_school_recommendations, name='primary_school_recommendations'),
    re_path(r'^primary/(?P<school_id>\d+)/$', primary_views.primary_school_detail, name='primary_school_detail'),

    re_path(r'^secondary/$', secondary_views.secondary_schools_list, name='secondary_schools_list'),
    re_path(r'^secondary/stats/$', secondary_views.secondary_schools_stats, name='secondary_schools_stats'),
    re_path(r'^secondary/filters/$', secondary_views.secondary_schools_filters, name='secondary_schools_filters'),
    re_path(r'^secondary/(?P<school_id>\d+)/recommendations/$', secondary_views.secondary_school_recommendations, name='secondary_school_recommendations'),
    re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_views.secondary_school_detail, name='secondary_school_detail'),

] 