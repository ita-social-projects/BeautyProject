"""This module provides all order's views."""

import logging
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import (filters, status)
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     get_object_or_404, ListAPIView, RetrieveAPIView)
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from beauty import signals
from beauty.tokens import OrderApprovingTokenGenerator
from beauty.utils import (ApprovingOrderEmail, CancelOrderEmail)
from api.models import (CustomUser, Order)
from api.permissions import (IsOrderUser, IsCustomerOrders)
from api.serializers.order_serializers import (OrderDeleteSerializer, OrderSerializer)

logger = logging.getLogger(__name__)


class TokenLoginRequiredMixin(LoginRequiredMixin):
    """A login required mixin that allows token authentication."""

    def dispatch(self, request, *args, **kwargs):
        """If token was provided, ignore authenticated status."""
        http_auth = request.META.get("HTTP_AUTHORIZATION")

        if http_auth and "JWT" in http_auth:
            pass

        elif not request.user.is_authenticated:
            return self.handle_no_permission()

        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class OrderListCreateView(ListCreateAPIView):
    """Generic API for orders custom POST method."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """Create an order and add an authenticated customer to it."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=request.user)

        logger.info(f"{order} with {order.service.name} was created")

        context = {"order": order}
        to = [order.specialist.email]
        ApprovingOrderEmail(request, context).send(to)

        logger.info(f"{order}: approving email was sent to the specialist "
                    f"{order.specialist.get_full_name()}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveCancelView(TokenLoginRequiredMixin, RetrieveUpdateDestroyAPIView):
    """Generic API for orders custom GET, PUT and DELETE methods.

    RUD - Retrieve, Update, Destroy.
    """

    login_url = settings.LOGIN_URL
    redirect_field_name = "redirect_to"

    queryset = Order.objects.all()
    serializer_class = OrderDeleteSerializer
    permission_classes = (IsAuthenticated, IsOrderUser)

    def get_object(self):
        """Get object.

        Method for getting order objects by using both order user id
        and order id lookup fields.
        """
        if len(self.kwargs) > 1:
            user = self.kwargs["user"]
            obj = get_object_or_404(
                self.get_queryset(),
                Q(customer=user) | Q(specialist=user),
                id=self.kwargs["pk"],
            )
            self.check_object_permissions(self.request, obj)

            logger.info(f"{obj} was got from user page")

            return obj

        logger.info(f"{super().get_object()} was got")

        return super().get_object()

    def put(self, request, *args, **kwargs):
        """Put method to cancel an active appointment by customer or specialist."""
        super().put(request, *args, **kwargs)
        order = self.get_object()
        authenticated_user = request.user
        user = order.customer if authenticated_user == order.specialist else order.specialist
        context = {"order": order, "user": authenticated_user}

        CancelOrderEmail(request, context).send([user.email])

        logger.info(f"{order}: canceling email was sent to the {user.get_full_name()}")

        return redirect(
            reverse("api:user-detail", args=[authenticated_user.id]))


class OrderApprovingView(RetrieveAPIView):
    """Approving orders custom GET method."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        """Get an answer from a specialist according to order and implement it."""
        token, order_id, order_status = self.decode_params(kwargs).values()
        order = get_object_or_404(self.get_queryset(), id=order_id)
        if OrderApprovingTokenGenerator().check_token(order, token):
            if order_status == "approved":
                order.mark_as_approved()

                logger.info(f"{order} was approved by the specialist "
                            f"{order.specialist.get_full_name()}")

                self.send_signal(order, request)
                return redirect(reverse("api:user-order-detail",
                                        kwargs={"user": order.specialist.id,
                                                "pk": order.id}))
            elif order_status == "declined":
                order.mark_as_declined()

                logger.info(f"{order} was declined by specialist "
                            f"{order.specialist.get_full_name()}")

                self.send_signal(order, request)
        logger.info(f"Token for {order} is not valid")

        return redirect(
            reverse("api:user-detail", args=[order.specialist.id]))

    def decode_params(self, kwargs: dict) -> dict:
        """Decode params from url.

        Args:
            kwargs(dict): coded params from URL

        Returns(dict): decoded params from URL
        """
        return {"token": kwargs["token"],
                "order_id": int(force_str(urlsafe_base64_decode(kwargs["uid"]))),
                "order_status": force_str(urlsafe_base64_decode(kwargs["status"]))}

    def send_signal(self, order: object, request: dict) -> None:
        """Send signal.

        Send signal for sending an email message to the customer
        with the specialist's order status decision.

        Args:
            order: instance order
            request: metadata about the request
        """
        logger.info(f"Signal was sent with {order}")

        signals.order_status_changed.send(
            sender=self.__class__, order=order, request=request,
        )


class CustomerOrdersViews(ListAPIView):
    """Show all orders concrete customer."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsCustomerOrders)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["status", "specialist", "service", "start_time", "end_time"]

    def get_queryset(self):
        """Get orders for a customer."""
        customer = get_object_or_404(CustomUser, id=self.kwargs["pk"])

        logger.info(f"Get orders for the customer {customer}")

        return customer.customer_orders.all()
