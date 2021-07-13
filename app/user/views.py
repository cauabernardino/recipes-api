from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Handles the creation of a new user in the system"""
    serializer_class = UserSerializer
