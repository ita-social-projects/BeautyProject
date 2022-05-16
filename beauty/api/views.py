from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from .models import CustomUser
from .serializers.serializers_customuser import CustomUserDetailSerializer
from .serializers.serializers_customuser import CustomUserSerializer


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for custom POST method"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # Permissions
    # line with max chars in code


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for custom GET, PUT and DELETE method.
    RUD - Retrieve, Update, Destroy"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    # Permissions
    # rest git hub
