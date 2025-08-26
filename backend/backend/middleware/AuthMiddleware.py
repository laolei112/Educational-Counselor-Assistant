import os

from django.shortcuts import redirect
from django.http import JsonResponse
from common.logger import loginfo


class AuthMiddleware(object):
     # 白名单
    white_list = [
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


