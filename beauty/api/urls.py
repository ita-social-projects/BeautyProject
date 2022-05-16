from django.urls import path

from .views import *

app_name = "api"

urlpatterns = [
    path('', CustomUserListCreateView.as_view(), name='user-list'),
    path('<int:pk>/', CustomUserDetailRUDView.as_view(), name='user-detail'),
    path('<int:user>/order/<int:id>/',
         CustomUserOrderDetailGenerics.as_view(),
         name='specialist-order-detail'),
]
