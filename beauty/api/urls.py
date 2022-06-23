"""This module provides all needed api urls."""

from datetime import datetime

from django.urls import path, register_converter

from api.views.order_views import (CustomerOrdersViews, OrderApprovingView,
                                   OrderListCreateView, OrderRetrieveCancelView)

from api.views.schedule import OwnerSpecialistScheduleView, SpecialistScheduleView

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


class DateConverter:
    """Converter class for passing date in urls.

    Provide to_python and to_url methods.
    """

    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        """Converts date from url to python datetime object."""
        return datetime.strptime(value, "%Y-%m-%d")

    def to_url(self, value):
        """Return date value from url."""
        return value


register_converter(DateConverter, "date")

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
    path(
        "schedule/<int:position_id>/<int:specialist_id>/<int:service_id>/<date:order_date>/",
        SpecialistScheduleView.as_view(),
        name="specialist-schedule",
    ),
    path(
        "owner_schedule/<int:position_id>/<int:specialist_id>/<date:order_date>/",
        OwnerSpecialistScheduleView.as_view(),
        name="owner-specialist-schedule",
    ),
]
