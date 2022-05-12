from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser
# from django.views.generic import CreateAPIView
from .models import CustomUser
from .serializers import CustomUserDetailSerializer


class CustomUserRegistration(ListCreateAPIView):
    """
    Create new CustomUser
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer
    permission_classes = [IsAdminUser]

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = CustomUserDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()




'''
    def post(self, request, format=None):
        """POST method for customer registration"""

        serializer = CustomUserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        users = CustomUser.objects.all()
        serializer_context = {"request": request}
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)
        '''