from django.urls import path

from .models import CustomUser
from .serializers import CustomUserSerializer
# from .views import CustomUserRegistration
from rest_framework.generics import ListCreateAPIView
from .views import CustomUserGenerics, CustomUserDetailGenerics

urlpatterns = [
    path('', CustomUserGenerics.as_view(), name='user-list'),
    path('<int:pk>/', CustomUserDetailGenerics.as_view(), name='user-detail'),
]
