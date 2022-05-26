from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path('user/', CustomUserListCreateView.as_view(),
         name='user-list-create'),
    path('user/<int:pk>/', CustomUserDetailRUDView.as_view(),
         name='user-detail'),
    path('user/<int:user>/order/<int:id>/',
         CustomUserOrderDetailRUDView.as_view(),
         name='specialist-order-detail'),

    path('order/', OrderListCreateView.as_view(),
         name='order-list-create'),

    path('order/<int:pk>/', OrderRetrieveUpdateDestroyView.as_view(),
         name='order-detail'),

    path('order/<int:pk>/user/<str:uid>/<str:token>/<str:status>/',
         OrderApprovingView.as_view(),
         name='order-approving'),
]
