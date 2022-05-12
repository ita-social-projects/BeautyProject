from django.urls import path
from .views import CustomUserRegistration

from .models import CustomUser
from .serializers import CustomUserSerializer

urlpatterns = [
    path("register/", CustomUserRegistration.as_view()),
]