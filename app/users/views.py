from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from users.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create new token for the user"""
    serializer_class = AuthTokenSerializer
    # centralize the rendering in api_settings
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
