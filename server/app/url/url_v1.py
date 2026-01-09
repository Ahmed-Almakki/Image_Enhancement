from django.urls import path
from django.urls.static import static
from django.conf import settings
from ..views import auth_views_v1, uploadFile

urlpatterns = [
    path('login', auth_views_v1.login_v1, name='Login_v1'),
    path('register', auth_views_v1.register_v1, name='Register_v1'),
    path('upload', uploadFile.upload_file, name='UploadImage'),
    path('activate-account', auth_views_v1.activateAccount, name='ActivateAccount'),
    path('check-task/<str:task_id>', uploadFile.checkTask, name="CheckTask"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)