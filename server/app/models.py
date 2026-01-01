from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from datetime import timedelta


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
    original_path = models.CharField(max_length=255, blank=True)
    enhance_path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title
