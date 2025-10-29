from django.urls import path
from ..views import auth_views_v1

urlpatterns = [
    path('login', auth_views_v1.email_login),
    # path('register/')
]