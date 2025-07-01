# restyle_project/backend/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    pass

admin.site.register(CustomUser, CustomUserAdmin)