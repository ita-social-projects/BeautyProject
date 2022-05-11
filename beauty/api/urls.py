from django.urls import path

from views import CustomUserRegistration

urlpatterns = [
    path("register/", CustomUserRegistration.as_view())
]