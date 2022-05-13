from django.urls import path

from .views import CustomUserGenerics, CustomUserDetailGenerics

app_name = "api"

urlpatterns = [
    path('', CustomUserGenerics.as_view(), name='user-list'),
    path('<int:pk>/', CustomUserDetailGenerics.as_view(), name='user-detail'),
]
