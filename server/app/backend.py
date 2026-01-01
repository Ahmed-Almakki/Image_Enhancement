"""
Class for Authentication using Email because the default authentication check the username and password not email
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailAuthentication(ModelBackend):
    """
    Authenticate using Email
    """
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        must be declared this way the **kwargs it important
        also the (user_can_authenticate) check if is active or not
        """
        if not email and not password:
            return None
        try:
            checkUser = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if checkUser.check_password(password) and self.user_can_authenticate(checkUser):
            return checkUser
        return None
