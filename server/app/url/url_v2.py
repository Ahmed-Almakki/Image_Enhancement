from django.urls import path
from ..views import auth_views_v1, auth_views_v2

urlpatterns = [
    path('get_token/', auth_views_v1.csrf_token),
    path('state/', auth_views_v2.sendState),
    path('auth/google/', auth_views_v2.loginRegister),
]