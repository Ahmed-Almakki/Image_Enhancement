from django.urls import path
from ..views import auth_views_v1, uploadFile

urlpatterns = [
    path('login', auth_views_v1.login_v1, name='Login_v1'),
    path('register', auth_views_v1.register_v1, name='Register_v1'),
    path('upload', uploadFile.upload_file, name='UploadImage'),
    path('activate-account', auth_views_v1.activateAccount, name='ActivateAccount'),
]