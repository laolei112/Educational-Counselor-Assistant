# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import redirect
from django.urls import include, path, re_path
from backend import api as api
from backend.api import seo_views


def redirect_view(request):
    response = redirect("/")
    return response


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    re_path(r"^302", redirect_view),
    # SEO-friendly school detail pages (Server-Side Meta Injection)
    re_path(r"^school/(?P<school_type>\w+)/(?P<school_id>\d+)$", seo_views.seo_school_detail_view),
    re_path(r"^api/", include(api.urls)),
]
