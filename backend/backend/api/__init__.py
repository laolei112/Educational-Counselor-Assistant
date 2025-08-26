from django.urls import include, re_path
from backend.api.schools import urls as schools_urls


urls = [
    re_path(r"^schools/", include(schools_urls)),
]
