"""This module provides all needed urls."""
from django.urls import path

from .views import (AllOrOwnerBusinessesListCreateAPIView, BusinessDetailRetrieveAPIView,
                    CustomUserDetailRUDView, CustomUserListCreateView,
                    CustomUserOrderDetailRUDView, OwnerBusinessDetailRUDView)


app_name = "api"

urlpatterns = [
    path(
        "users/",
        CustomUserListCreateView.as_view(),
        name="user-list",
    ),
    path(
        "user/<int:pk>/",
        CustomUserDetailRUDView.as_view(),
        name="user-detail",
    ),
    path(
        "user/<int:user>/order/<int:id>/",
        CustomUserOrderDetailRUDView.as_view(),
        name="specialist-order-detail",
    ),
    path(
        'businesses/',
        AllBusinessesListAPIView.as_view(),
        name='businesses-list',
    ),
    path(
        'businesses/<int:owner_id>/',
        OwnerBusinessesListAPIView.as_view(),
        name='certain-owners-businesses-list',
    ),
    path(
        "businesses/<int:owner_id>/<int:pk>/",
        OwnerBusinessDetailRUDView.as_view(),
        name="owner-business-detail",
    ),
    path(
        "business/<int:pk>/",
        BusinessDetailRetrieveAPIView.as_view(),
        name="business-detail",
    ),
]
