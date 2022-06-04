"""This module provides all needed api urls."""

from django.urls import path

from .views import (AllOrOwnerBusinessesListCreateAPIView,
                    BusinessDetailRetrieveAPIView,
                    CustomUserDetailRUDView,
                    CustomUserListCreateView,
                    OrderApprovingView,
                    OrderListCreateView,
                    OrderRetrieveUpdateDestroyView,
                    OwnerBusinessDetailRUDView,
                    PositionListCreateView,
                    PositionRetrieveUpdateDestroyView,
                    ReviewAddView)


app_name = "api"
urlpatterns = [
    path(
        "users/",
        CustomUserListCreateView.as_view(),
        name="user-list-create",
    ),
    path(
        "user/<int:pk>/",
        CustomUserDetailRUDView.as_view(),
        name="user-detail",
    ),
    path(
        "user/<int:user>/order/<int:pk>/",
        OrderRetrieveUpdateDestroyView.as_view(),
        name="user-order-detail",
    ),
    path(
        "orders/", OrderListCreateView.as_view(),
        name="order-list-create",
    ),
    path(
        "order/<int:pk>/",
        OrderRetrieveUpdateDestroyView.as_view(),
        name="order-detail",
    ),
    path(
        "order/<str:uid>/<str:token>/<str:status>/",
        OrderApprovingView.as_view(),
        name="order-approving",
    ),
    path(
        "businesses/",
        AllOrOwnerBusinessesListCreateAPIView.as_view(),
        name="businesses-list-create",
    ),
    path(
        "businesses/<int:owner_id>/",
        AllOrOwnerBusinessesListCreateAPIView.as_view(),
        name="certain-owners-businesses-list",
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
    path(
        "position/",
        PositionListCreateView.as_view(),
        name="position-list",
    ),
    path(
        "position/<int:pk>",
        PositionRetrieveUpdateDestroyView.as_view(),
        name="position-detail-list",
    ),
    path(
        r"<int:user>/reviews/add/",
        ReviewAddView.as_view(),
        name="review-add"),
]
