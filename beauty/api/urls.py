from django.urls import path
from .views import *


app_name = "api"

urlpatterns = [
    path('', CustomUserListCreateView.as_view(), name='user-list'),
    path('<int:pk>/', CustomUserDetailRUDView.as_view(), name='user-detail'),
    path('<int:user>/order/<int:id>/',
         CustomUserOrderDetailRUDView.as_view(),
         name='specialist-order-detail'),
    path(r'<int:user>/reviews/add/', ReviewAddView.as_view(),
         name='review-add'),
]
