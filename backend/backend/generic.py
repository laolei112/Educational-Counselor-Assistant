# -*- coding: utf-8 -*-
import os

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import exceptions
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication


class YundiUserAuthentication(BaseAuthentication):

    def authenticate(self, request):
        username = request.session.get('username')
        if not username:
            detail = {"detail": "用户未通过鉴权", "result": False}
            raise exceptions.AuthenticationFailed(detail)
        else:
            user = User.objects.filter(username=username).first()
        return user, user


class ApiMixin(GenericViewSet):

    # if os.environ.get("AOVTOOLS_ENV_NOAUTH", "") == "1":
    #     print("no auth by dev env")
    #     authentication_classes = []
    #     permission_classes = []
    # else:
    authentication_classes = []
    # authentication_classes = [YundiUserAuthentication,]
    # permission_classes = [IsAuthenticated,]
    permission_classes = []

    # def finalize_response(self, request, response, *args, **kwargs):
        # 禁用客户端的 MIME 类型嗅探行为，防止基于"MIME"的攻击
        # response._headers["x-content-type-options"] = ("X-Content-Type-Options", "nosniff")
        # return super(ApiMixin, self).finalize_response(request, response, *args, **kwargs)
