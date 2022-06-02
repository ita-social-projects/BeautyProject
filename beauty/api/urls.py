"""Module with app api urls."""

from django.urls import path
from .views import (CustomUserListCreateView, CustomUserDetailRUDView, ReviewAddView,
                    OrderRetrieveUpdateDestroyView, OrderListCreateView, OrderApprovingView)

app_name = "api"

urlpatterns = [
    path("users/", CustomUserListCreateView.as_view(),
         name="user-list-create"),
    path("user/<int:pk>/", CustomUserDetailRUDView.as_view(),
         name="user-detail"),
    path("user/<int:user>/order/<int:pk>/",
         OrderRetrieveUpdateDestroyView.as_view(),
         name="user-order-detail"),

    path("orders/", OrderListCreateView.as_view(),
         name="order-list-create"),
    path("order/<int:pk>/", OrderRetrieveUpdateDestroyView.as_view(),
         name="order-detail"),
    path("order/<str:uid>/<str:token>/<str:status>/",
         OrderApprovingView.as_view(),
         name="order-approving"),

    path(r"<int:user>/reviews/add/", ReviewAddView.as_view(),
         name="review-add"),
]
