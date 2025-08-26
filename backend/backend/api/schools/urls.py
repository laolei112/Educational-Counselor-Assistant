from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.schools_list, name='schools_list'),
    re_path(r'^stats/$', views.schools_stats, name='schools_stats'),
    re_path(r'^(?P<school_id>\d+)/$', views.school_detail, name='school_detail'),
] 