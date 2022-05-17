from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status

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

    def perform_destroy(self, instance):
        """Reimplementation of the DESTROY (DELETE) method.
        Makes current user inactive by changing its' field
        """
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Permissions
    # rest git hub
