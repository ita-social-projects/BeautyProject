from rest_framework.permissions import IsAdminUser
from rest_framework.generics import (
                                    ListCreateAPIView,
                                    RetrieveUpdateDestroyAPIView
                                    )

from .models import CustomUser
from .serializers.serializers_customuser import (
                                                CustomUserSerializer, 
                                                CustomUserDetailSerializer
                                                )


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for POST and GET all method"""

    queryset = CustomUser.objects.all()

    # This serializer is attached to POST method
    serializer_class = CustomUserSerializer


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for GET, PUT and DELETE method,
    RUD - Retrive, Update, Delete"""

    queryset = CustomUser.objects.all()

    # This serializer is attached to GET, PUT, DELETE methods
    serializer_class = CustomUserDetailSerializer
