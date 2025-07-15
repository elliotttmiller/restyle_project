# restyle_project/backend/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # We are inheriting all the fields from Django's default User model
    def __str__(self):
        return self.username