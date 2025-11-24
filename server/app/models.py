from django.db import models
from django.contrib.auth.models import AbstractUser


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
