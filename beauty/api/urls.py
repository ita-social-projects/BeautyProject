from django.urls import path
from .views import CustomUserRegistration
from .models import CustomUser
from .serializers import CustomUserDetailSerializer
urlpatterns = [
    path("register/", CustomUserRegistration.as_view(queryset=CustomUser.objects.all(), serializer_class=CustomUserDetailSerializer)),
]