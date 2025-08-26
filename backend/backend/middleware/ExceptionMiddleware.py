# -*- coding: utf-8 -*-
import json
import traceback

from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from common.logger import logerror


class ExceptionMiddleware(object):


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            response = self.get_response(request)
        except ValidationError:
            data = {
                "result": False,
                "message": f"参数验证失败:{exec}",
                "data": {},
            }
            return HttpResponse(
                json.dumps(data),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )
        except Exception as err:
            path = request.get_full_path()  # Get the URL Path# Get the traceback
            meta = request.META  # Get request meta information
            logerror(f"{path} {meta} error: {traceback.format_exc()}")
            data = {
                "result": False,
                "message": "handle request error",
                "data": {},
            }
            return HttpResponse(
                json.dumps(data),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        if response.status_code == 500:
            data = {
                "result": False,
                "message": "服务器出现异常，请联系程序员查看日志",
                "data": {},
            }
            return HttpResponse(
                json.dumps(data),
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )
        return response

