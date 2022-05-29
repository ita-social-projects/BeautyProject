from datetime import datetime

from django.db.models import Q
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView, get_object_or_404,
                                     GenericAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from beauty.tokens import OrderApprovingTokenGenerator
from .models import CustomUser, Order
from .permissions import (IsAccountOwnerOrReadOnly, IsOrderUserOrReadOnly)

from .serializers.customuser_serializers import (CustomUserDetailSerializer,
                                                 CustomUserSerializer,
                                                 ResetPasswordSerializer)
from api.serializers.order_serializers import (OrderSerializer,
                                               OrderDetailSerializer)
from beauty import signals
from beauty.utils import ApprovingOrderEmail
import logging

logger = logging.getLogger(__name__)


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for users custom POST methods"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserActivationView(GenericAPIView):
    """Generic view for user account activation"""

    def get(self, request, uidb64, token):
        id = int(force_str(urlsafe_base64_decode(uidb64)))

        user = get_object_or_404(CustomUser, id=id)
        user.is_active = True
        user.save()

        logger.info(f"User {user} was activated")

        return redirect(reverse("api:user-detail", kwargs={"pk": id}))


class ResetPasswordView(GenericAPIView):
    """Generic view for reset password"""
    serializer_class = ResetPasswordSerializer
    model = CustomUser

    def post(self, request, uidb64, token):
        id = int(force_str(urlsafe_base64_decode(uidb64)))
        user = get_object_or_404(CustomUser, id=id)
        self.get_serializer().validate(request.POST)
        user.set_password(request.POST.get('password'))
        user.save()

        logger.info(f"User {user} password was reset")

        return redirect(reverse("api:user-detail", kwargs={"pk": id}))


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for users custom GET, PUT and DELETE methods.
    RUD - Retrieve, Update, Destroy"""
    permission_classes = [IsAccountOwnerOrReadOnly]

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    def perform_destroy(self, instance):
        """Reimplementation of the DESTROY (DELETE) method.
        Makes current user inactive by changing its' field
        """
        if instance.is_active:
            instance.is_active = False
            instance.save()

            logger.info(f"User {instance} was deactivated")

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderListCreateView(ListCreateAPIView):
    """Generic API for orders custom POST method"""

    queryset = Order.objects.exclude(status__in=[2, 4])
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    logger.info("Orders was loaded")

    def post(self, request, *args, **kwargs):
        """Create an order and add an authenticated customer to it."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(customer=request.user)

        logger.info(f"{order} with {order.service.name} was created")

        context = {"order": order}
        to = [order.specialist.email, ]
        ApprovingOrderEmail(request, context).send(to)

        logger.info(f"{order}: approving email was sent to the specialist "
                    f"{order.specialist.get_full_name()}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Generic API for orders custom GET, PUT and DELETE methods.
       RUD - Retrieve, Update, Destroy"""

    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = (IsOrderUserOrReadOnly,)

    def get_object(self):
        """Method for getting order objects by using both order user id
         and order id lookup fields."""
        if len(self.kwargs) > 1:
            obj = get_object_or_404(self.get_queryset(),
                                    Q(customer=self.kwargs['user']) |
                                    Q(specialist=self.kwargs['user']),
                                    id=self.kwargs['id'])
            self.check_object_permissions(self.request, obj)

            logger.info(f"{obj} was got from user page")

            return obj

        logger.info(f"{super().get_object()} was got")

        return super().get_object()


class OrderApprovingView(ListCreateAPIView):
    """Approving orders custom GET method."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        """Get an answer from a specialist according to
        order and implement it.
        """
        token = kwargs["token"]
        order_id = int(force_str(urlsafe_base64_decode(kwargs["uid"])))
        order_status = force_str(urlsafe_base64_decode(kwargs["status"]))
        order = self.get_queryset().get(id=order_id)
        if OrderApprovingTokenGenerator().check_token(order, token):
            if order_status == 'approved':
                order.mark_as_approved()

                logger.info(f"{order} was approved by the specialist "
                            f"{order.specialist.get_full_name()}")

                self.send_signal(order, request)
                return redirect(reverse("api:user-order-detail",
                                        kwargs={"user": order.specialist.id,
                                                "id": order_id}))
            elif order_status == 'declined':
                order.mark_as_declined()

                logger.info(f"{order} was declined by specialist "
                            f"{order.specialist.get_full_name()}")

                self.send_signal(order, request)
        logger.info(f"Token for {order} is not valid")

        return redirect(
            reverse("api:user-detail", args=[order.specialist.id, ]))

    def send_signal(self, order: object, request: dict) -> None:
        """Send signal for sending an email message to the customer
         with the specialist's order status decision

        Args:
            order: instance order
            request: metadata about the request
        """

        logger.info(f"Signal was sent with {order}")

        signals.order_status_changed.send(
            sender=self.__class__, order=order, request=request
        )
