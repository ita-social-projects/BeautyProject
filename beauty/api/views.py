"""Module with views for api application."""

from django.db.models import Q
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, get_object_or_404, \
    GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

import logging

from .models import CustomUser, Order, Business
from .permissions import IsAccountOwnerOrReadOnly

from .serializers.serializers_customuser import CustomUserDetailSerializer, \
    CustomUserSerializer, \
    UserOrderDetailSerializer, ResetPasswordSerializer
from .serializers.serializers_business import BusinessListCreateSerializer

logger = logging.getLogger(__name__)


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for users custom POST methods."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserActivationView(GenericAPIView):
    """Generic view for user account activation."""

    def get(self, request, uidb64, token):
        """Get method for user activation via email.

        Parses id from token and changes is_active = True
        """
        user_id = int(force_str(urlsafe_base64_decode(uidb64)))

        user = get_object_or_404(CustomUser, id=id)
        user.is_active = True
        user.save()

        logger.info(f"User {user} was activated")

        return redirect(reverse("api:user-detail", kwargs={"pk": user_id}))


class ResetPasswordView(GenericAPIView):
    """Generic view for reset password."""
    serializer_class = ResetPasswordSerializer
    model = CustomUser

    def post(self, request, uidb64, token):
        """Post method for password reset.

        Parses user id from token and changes user password
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

    RUD - Retrieve, Update, Destroy
    """
    permission_classes = [IsAccountOwnerOrReadOnly]

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    def perform_destroy(self, instance):
        """Reimplementation of the DESTROY (DELETE) method.

        Makes current user inactive by changing its" field
        """
        if instance.is_active:
            instance.is_active = False
            instance.save()

            logger.info(f"User {instance} was deactivated")

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomUserOrderDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for orders custom GET, PUT and DELETE methods.

    RUD - Retrieve, Update, Destroy
    """

    queryset = Order.objects.all()
    serializer_class = UserOrderDetailSerializer
    multiple_lookup_fields = ("user", "id")

    def get_object(self):
        """Method for getting order objects from user.

        Uses both order user id and order id lookup fields
        """
        queryset = self.get_queryset()
        user = self.kwargs["user"]
        obj = get_object_or_404(
            queryset,
            Q(customer=user) | Q(specialist=user),
            id=self.kwargs["id"],
        )
        self.check_object_permissions(self.request, obj)

        user = (
            obj.customer if self.kwargs["user"] == obj.customer.id else
            obj.specialist
        )

        logger.info(f"{obj} was got for the user {user} (id={user.id})")

        return obj


class BusinessListCreateView(ListCreateAPIView):
    """View for business creation and displaying list of all businesses.

    Gives basic info about all businesses
    """

    queryset = Business.objects.all()
    serializer_class = BusinessListCreateSerializer

    def get_permissions(self):
        """For business creation you need to be authentificated."""
        if self.request.method == "POST":
            self.permission_classes = (IsAccountOwnerOrReadOnly,)
        return super().get_permissions()
