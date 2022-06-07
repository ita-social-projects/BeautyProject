"""This module provides all needed api urls."""

from django.urls import path

from api.views.order_views import (OrderApprovingView, OrderListCreateView,
                                   OrderRetrieveCancelView)
from api.views.review_views import (ReviewDisplayView, ReviewDisplayDetailView)
from .views_api import (AllServicesListView, BusinessDetailRUDView,
                        BusinessesListCreateAPIView, CustomUserDetailRUDView,
                        CustomUserListCreateView, PositionListCreateView, ReviewAddView,
                        ServiceUpdateView)


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
        OrderRetrieveCancelView.as_view(),
        name="user-order-detail",
    ),
    path(
        "orders/",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),
    path(
        "order/<int:pk>/",
        OrderRetrieveCancelView.as_view(),
        name="order-detail",
    ),
    path(
        "order/<str:uid>/<str:token>/<str:status>/",
        OrderApprovingView.as_view(),
        name="order-approving",
    ),
    path(
        "businesses/",
        BusinessesListCreateAPIView.as_view(),
        name="businesses-list-create",
    ),
    path(
        "business/<int:pk>/",
        BusinessDetailRUDView.as_view(),
        name="business-detail",
    ),
    path(
        "position/",
        PositionListCreateView.as_view(),
        name="position-list",
    ),
    path(
        r"<int:user>/reviews/add/",
        ReviewAddView.as_view(),
        name="review-add",
    ),
    path(
        r"reviews/<int:to_user>/",
        ReviewDisplayView.as_view(),
        name="review-get",
    ),
    path(
        r"review/<int:pk>/",
        ReviewDisplayDetailView.as_view(),
        name="review-detail",
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
