# restyle_project/backend/users/views.py

from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

class CreateUserView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]