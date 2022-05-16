from .models import CustomUser
from .serializers.serializers_customuser import CustomUserSerializer, CustomUserDetailSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for custom POST method"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # Permissions
    # line with max chars in code


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for custom GET, PUT and DELETE method
    RUD - Retrive, Update, Delete"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    # Permissions
    # rest git hub 

