from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path('users/', CustomUserListCreateView.as_view(),
         name='user-list-create'),
    path('user/<int:pk>/', CustomUserDetailRUDView.as_view(),
         name='user-detail'),
    path('user/<int:user>/order/<int:id>/',
         CustomUserOrderDetailRUDView.as_view(),
         name='specialist-order-detail'),

    path('businesses/', BusinessListCreateView.as_view(),
         name='business-list-create'),

    path('orders/', OrderListCreateView.as_view(),
         name='order-list-create'),
]
