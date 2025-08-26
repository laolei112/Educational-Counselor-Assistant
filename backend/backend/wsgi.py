import os

from django.core.wsgi import get_wsgi_application
# from django.core.asgi import get_asgi_application
# from django.urls import path, re_path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import django_eventstream

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# application = ProtocolTypeRouter({
#     'http': URLRouter([
#         path('events/', AuthMiddlewareStack(
#             URLRouter(django_eventstream.routing.urlpatterns)
#         ), { 'channels': ['test'] }),
#         re_path(r'', get_wsgi_application()),
#     ]),
# })