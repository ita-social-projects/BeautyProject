from django.http import Http404
from itsdangerous import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from serializers import CustomSerializer


class CustomUserRegistration(APIView):
    """
    Create new CustomUser
    """
    def post(self, request, format=None):
        serializer = CustomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
