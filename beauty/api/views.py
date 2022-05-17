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

    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()

    # This serializer is attached to POST method
    serializer_class = CustomUserSerializer
