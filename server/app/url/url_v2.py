from django.urls import path
from ..views import auth_views_v1, auth_views_v2

urlpatterns = [
    path('state/', auth_views_v2.sendState, name="redirct_params_for_oauth"),
    path('auth/google/', auth_views_v2.loginRegister, name='OAuth_login'),
    path('current_user/', auth_views_v2.current_user, name='get_currentUser'),
]