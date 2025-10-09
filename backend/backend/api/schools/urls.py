from django.urls import re_path
from . import views
from . import secondary_views

urlpatterns = [
    # 通用接口
    re_path(r'^$', views.schools_list, name='schools_list'),
    re_path(r'^stats/$', views.schools_stats, name='schools_stats'),
    re_path(r'^(?P<school_id>\d+)/$', views.school_detail, name='school_detail'),
    
    # 小学接口（从 tb_schools 表读取）
    re_path(r'^primary/$', views.primary_schools_list, name='primary_schools_list'),
    
    # 中学接口（从 tb_secondary_schools 表读取）
    re_path(r'^secondary/$', secondary_views.secondary_schools_list, name='secondary_schools_list'),
    re_path(r'^secondary/stats/$', secondary_views.secondary_schools_stats, name='secondary_schools_stats'),
    re_path(r'^secondary/(?P<school_id>\d+)/$', secondary_views.secondary_school_detail, name='secondary_school_detail'),
] 