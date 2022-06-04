"""This module provides all needed api urls."""

from django.urls import path

from .views import (AllOrOwnerBusinessesListCreateView,
                    CustomUserDetailRUDView, CustomUserListCreateView,
<<<<<<< HEAD
                    OrderApprovingView, OrderListCreateView,
                    OrderRetrieveUpdateDestroyView, OwnerBusinessDetailRUDView,
                    ReviewAddView)
=======
                    OrderApprovingView, OrderListCreateView, OrderRetrieveUpdateDestroyView,
                    OwnerBusinessDetailRUDView, ReviewAddView, ServiceUpdateView,
                    AllServicesListView)
>>>>>>> dc9b9ea64e628cdc284d5124b6f9eed67975745e


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
        AllOrOwnerBusinessesListCreateView.as_view(),
        name="businesses-list-create",
    ),
    path(
        "owner_businesses/<int:owner_id>/",
        AllOrOwnerBusinessesListCreateView.as_view(),
        name="certain-owners-businesses-list",
    ),
    path(
        "owner_business/<int:owner_id>/<int:pk>/",
        OwnerBusinessDetailRUDView.as_view(),
        name="owner-business-detail",
    ),
    path(
        "business/<int:pk>/",
        OwnerBusinessDetailRUDView.as_view(),
        name="business-detail",
    ),
    path(
        r"<int:user>/reviews/add/",
        ReviewAddView.as_view(),
        name="review-add",
    ),
    path(
        "services/",
        AllServicesListView.as_view(),
        name="service-list",
    ),
    path("service/<int:pk>/",
         ServiceUpdateView.as_view(),
         name="service-detail"),
]
