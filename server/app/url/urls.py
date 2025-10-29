from django.urls import path, include

urlpatterns = [
    path('api/v1/', include('server.app.url.url_v1')),
    path('api/v2/', include('server.app.url.url_v2'))
]

