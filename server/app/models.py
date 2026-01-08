from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid



def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f"images/{uuid.uuid4()}.{ext}"


# Create your models here.
class MyUser(AbstractUser):
    """
    Always use AbstractUser when just want to add to the user, but if want full control
    of the fields use AbstractBaseUser
    """
    provider = models.CharField(max_length=200, blank=True, null=True)
    provider_id = models.CharField(max_length=200, blank=True, null=True)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)


class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class RestPassword(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=255)
    attempt = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.email}"


class PasswordToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_token= models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=0)

    def __str__(self):
        return f"Password reset token for {self.user.email}"