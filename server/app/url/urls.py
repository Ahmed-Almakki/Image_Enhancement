from django.urls import path, include
from ..views import auth_views_v1

urlpatterns = [
    path('api/v1/', include('server.app.url.url_v1')),
    path('api/v2/', include('server.app.url.url_v2')),
    path('api/get_token/', auth_views_v1.csrf_token, name='get_csrf_token'),
    path('api/logout/', auth_views_v1.singout, name='logout'),
    path('api/reset_passowrd/', auth_views_v2.resetPassword, name='reset_password')
]

