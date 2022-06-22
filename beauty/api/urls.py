"""This module provides all needed api urls."""

from django.urls import path

from api.views.order_views import (CustomerOrdersViews, OrderApprovingView,
                                   OrderListCreateView, OrderRetrieveCancelView)

from api.views.review_views import (ReviewDisplayView,
                                    ReviewRUDView,
                                    ReviewAddView)

from api.views.position_views import (InviteSpecialistToPosition,
                                      InviteSpecialistApprove)

from api.views.customuser_views import InviteRegisterView

from .views_api import (AllServicesListCreateView, BusinessesListCreateAPIView,
                        BusinessDetailRUDView, CustomUserDetailRUDView,
                        CustomUserListCreateView, PositionListCreateView, SpecialistDetailView,
                        ServiceUpdateView, PositionRetrieveUpdateDestroyView,
                        RemoveSpecialistFromPosition)

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
        "specialist/<int:pk>/",
        SpecialistDetailView.as_view(),
        name="specialist-detail",
    ),
    path(
        "user/<int:user>/order/<int:pk>/",
        OrderRetrieveCancelView.as_view(),
        name="user-order-detail",
    ),
    path(
        "customer/<int:pk>/orders/",
        CustomerOrdersViews.as_view(),
        name="customer-orders-list",
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
        "position/<int:pk>",
        PositionRetrieveUpdateDestroyView.as_view(),
        name="position-detail-list",
    ),
    path(
        "position/<int:pk>/specialist/<int:specialist_id>",
        RemoveSpecialistFromPosition.as_view(),
        name="position-delete-specialist",
    ),
    path(
        "position/<int:pk>/add/",
        InviteSpecialistToPosition.as_view(),
        name="position-add-specialist",
    ),
    path(
        "position-accept/<str:email>/<str:position>/<str:token>/<str:answer>/",
        InviteSpecialistApprove.as_view(),
        name="position-approve",
    ),
    path(
        "invited/<str:invite>/<str:token>/",
        InviteRegisterView.as_view(),
        name="register-invite",
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
        ReviewRUDView.as_view(),
        name="review-detail",
    ),
    path(
        "services/",
        AllServicesListCreateView.as_view(),
        name="service-list-create",
    ),
    path("service/<int:pk>/",
         ServiceUpdateView.as_view(),
         name="service-detail"),
]
