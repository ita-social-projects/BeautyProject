from django.urls import path

from .views import *

app_name = "api"

urlpatterns = [
    path('', CustomUserListCreateView.as_view(), name='user-list'),
    path('<int:pk>/', CustomUserDetailRUDView.as_view(), name='user-detail')
]
