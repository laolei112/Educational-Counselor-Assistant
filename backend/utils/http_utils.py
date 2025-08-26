from rest_framework import status
from rest_framework.response import Response

def response_with_json(data=None, msg="", code=status.HTTP_200_OK):
    if data is None:
        data = {}
    return Response(
        {
            "code": code,
            "msg":  msg,
            "data": data,
        },
        status=code,
    )