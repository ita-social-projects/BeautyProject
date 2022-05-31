from django.urls import path
from .views import *

app_name = "api"     

urlpatterns = [
    path('user/', CustomUserListCreateView.as_view(),
         name='user-list'),
    path('user/<int:pk>/', CustomUserDetailRUDView.as_view(),
         name='user-detail'),

    path('businesses/', BusinessListCreateView.as_view(),
         name='business-list-create'),

    path('user/<int:user>/order/<int:pk>/',
         OrderRetrieveUpdateDestroyView.as_view(),
         name='user-order-detail'),
    path('orders/', OrderListCreateView.as_view(),
         name='order-list-create'),
    path('order/<int:pk>/', OrderRetrieveUpdateDestroyView.as_view(),
         name='order-detail'),
    path('order/<str:uid>/<str:token>/<str:status>/',
         OrderApprovingView.as_view(),
         name='order-approving'),
]
