from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path('users/', CustomUserListCreateView.as_view(),
         name='user-list-create'),
    path('user/<int:pk>/', CustomUserDetailRUDView.as_view(),
         name='user-detail'),
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
    path('', CustomUserListCreateView.as_view(), name='user-list'),
    path('<int:pk>/', CustomUserDetailRUDView.as_view(), name='user-detail'),
    path('<int:user>/order/<int:id>/',
         CustomUserOrderDetailRUDView.as_view(),
         name='specialist-order-detail'),
    path(r'<int:user>/reviews/add/', ReviewAddView.as_view(),
         name='review-add'),
]
