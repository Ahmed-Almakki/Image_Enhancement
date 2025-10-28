from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser

# this make my custom user show up and managed in DJango admin
admin.site.register(MyUser, UserAdmin)

# Register your models here.
