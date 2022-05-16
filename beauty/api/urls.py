from django.urls import path
from .views import CustomUserRegistration, CustomUserDetailRegistration
app_name = "api"

urlpatterns = [
    path('generic-register/', CustomUserRegistration.as_view(), name='user-list'),
    path('generic-register/<int:pk>/', CustomUserDetailRegistration.as_view(), name='user-detail')
]
