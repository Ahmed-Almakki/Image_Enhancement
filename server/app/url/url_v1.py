from django.urls import path
from ..views import auth_views_v1

urlpatterns = [
    path('get_token/', auth_views_v1.csrf_token),
    path('login', auth_views_v1.login_v1),
    path('register', auth_views_v1.register_v1)
]