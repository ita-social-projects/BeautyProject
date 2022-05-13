
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer
from .serializers import CustomUserDetailSerializer


class CustomUserGenerics(ListCreateAPIView):
    """
    Create new CustomUser
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

    """def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = CustomUserSerializer(queryset, many=True)
        return Response(serializer.data)"""

    def perform_create(self, serializer):
        serializer.save()


class CustomUserDetailGenerics(ListCreateAPIView):
    """
    Create new CustomUser
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = CustomUserSerializer(queryset, many=True)
        return Response(serializer.data)
