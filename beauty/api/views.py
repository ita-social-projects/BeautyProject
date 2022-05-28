"""All views for the BeatyProject."""
import logging

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
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from beauty.tokens import OrderApprovingTokenGenerator
from .models import CustomUser, Order
from .permissions import (IsAccountOwnerOrReadOnly, IsOrderUser)

from .serializers.customuser_serializers import (CustomUserDetailSerializer,
                                                 CustomUserSerializer,
                                                 ResetPasswordSerializer)
from api.serializers.order_serializers import (OrderSerializer,
                                               OrderDeleteSerializer)
from beauty import signals
from beauty.utils import ApprovingOrderEmail
from .serializers.review_serializers import ReviewAddSerializer


logger = logging.getLogger(__name__)


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for users custom POST methods."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserActivationView(GenericAPIView):
    """Generic view for user account activation."""

    def get(self, request: object, uidb64: str, token: str):
        """Activate use account.

        Args:
            request (object): request data.
            uidb64 (str): coded user id.
            token (str): user token.
        """
        user_id = int(force_str(urlsafe_base64_decode(uidb64)))

        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = True
        user.save()

        logger.info(f"User {user} was activated")

        return redirect(reverse("api:user-detail", kwargs={"pk": user_id}))


class ResetPasswordView(GenericAPIView):
    """Generic view for reset password."""

    serializer_class = ResetPasswordSerializer
    model = CustomUser

    def post(self, request: object, uidb64: str, token: str):
        """Reset use password.

        Args:
            request (object): request data.
            uidb64 (str): coded user id.
            token (str): user token.
        """
        user_id = int(force_str(urlsafe_base64_decode(uidb64)))
        user = get_object_or_404(CustomUser, id=user_id)
        self.get_serializer().validate(request.POST)
        user.set_password(request.POST.get("password"))
        user.save()

        logger.info(f"User {user} password was reset")

        return redirect(reverse("api:user-detail", kwargs={"pk": user_id}))


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for users custom GET, PUT and DELETE methods.

    RUD - Retrieve, Update, Destroy.
    """

    permission_classes = [IsAccountOwnerOrReadOnly]

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    def perform_destroy(self, instance):
        """Reimplementation of the DESTROY (DELETE) method.

        Makes current user inactive by changing its field.
        """
        if instance.is_active:
            instance.is_active = False
            instance.save()

            logger.info(f"User {instance} was deactivated")

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderListCreateView(ListCreateAPIView):
    """Generic API for orders custom POST method."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

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


class OrderRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Generic API for orders custom GET, PUT and DELETE methods.

    RUD - Retrieve, Update, Destroy.
    """

    queryset = Order.objects.exclude(status__in=[2, 4])
    serializer_class = OrderDeleteSerializer
    permission_classes = (IsAuthenticated, IsOrderUser)

    def get_object(self):
        """Get object.

        Method for getting order objects by using both order user id
        and order id lookup fields.
        """
        if len(self.kwargs) > 1:
            obj = get_object_or_404(
                self.get_queryset(),
                Q(customer=self.kwargs["user"]) | Q(specialist=self.kwargs["user"]),
                id=self.kwargs["pk"],
            )
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


class ReviewAddView(GenericAPIView):
    """This class represents a view which is accessed when someone
    is trying to create a new Review. It makes use of the POST method,
    other methods are not allowed in this view.
    """

    serializer_class = ReviewAddSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, user):
        """This is a POST method of the view"""
        serializer = ReviewAddSerializer(data=request.data)
        if serializer.is_valid():
            to_user = CustomUser.objects.get(pk=user)
            serializer.save(
                from_user=self.request.user,
                to_user=to_user
            )
            logger.info(f"User {self.request.user} posted a review for {to_user}")
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
