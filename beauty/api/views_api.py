"""This module provides all needed api views."""

import logging

from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import status

from rest_framework.generics import (GenericAPIView, ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     RetrieveAPIView,
                                     get_object_or_404)
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import action

from djoser.views import UserViewSet as DjoserUserViewSet

from .models import (Business, CustomUser, Position, Service)

from .permissions import (IsAdminOrThisBusinessOwner, IsOwner,
                          IsPositionOwner, IsProfileOwner, ReadOnly)

from .serializers.business_serializers import (BusinessCreateSerializer,
                                               BusinessesSerializer,
                                               BusinessGetAllInfoSerializers,
                                               BusinessDetailSerializer)

from .serializers.customuser_serializers import (CustomUserDetailSerializer,
                                                 CustomUserSerializer,
                                                 ResetPasswordSerializer,
                                                 SpecialistInformationSerializer,
                                                 SpecialistDetailSerializer)
from .serializers.review_serializers import ReviewAddSerializer
from .serializers.position_serializer import PositionSerializer
from .serializers.service_serializers import ServiceSerializer


logger = logging.getLogger(__name__)


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for users custom POST methods."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserActivationView(GenericAPIView):
    """Generic view for user account activation."""

    def get(self, request: object, uidb64: str, token: str):
        """Activate use account and redirect to personal page.

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

    permission_classes = [IsProfileOwner]

    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        """Return a needed serializer_class for specific object.

        If the user is a Specialist, return SpecialistInformationSerializer.
        If the user is a User, return a CustomUserSerializer.
        """
        if CustomUser.objects.filter(id=self.kwargs.get("pk"),
                                     groups__name__icontains="specialist"):
            logger.info(f"User {self.kwargs.get('pk')} is a specialist.")

            return SpecialistInformationSerializer

        logger.info(f"User {self.kwargs.get('pk')} is not specialist.")

        return CustomUserDetailSerializer

    def destroy(self, request, *args, **kwargs):
        """Reimplementation of the DESTROY (DELETE) method.

        Instead of deleting a User, it makes User inactive by modifing
        its 'is_active' field. Only an authentificated Users can change
        themselves. Endpoint is used in the User Profile.
        """
        instance = self.get_object()

        if instance.is_active:
            instance.is_active = False
            instance.save()
            logger.info(f"User {instance} was deactivated.")
            return Response(status=status.HTTP_200_OK)

        logger.info(f"User {instance} (id={instance.id}) is already "
                    f"deactivated, but tried doing it again.")
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SpecialistDetailView(RetrieveAPIView):
    """Generic API for specialists custom GET method."""

    queryset = CustomUser.objects.filter(groups__name__icontains="specialist")
    serializer_class = SpecialistDetailSerializer


class PositionListCreateView(ListCreateAPIView):
    """Generic API for position POST methods."""

    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated, IsPositionOwner)

    def get_queryset(self):
        """Filter position for current owner."""
        positions = Position.objects.filter(business__owner=self.request.user)
        logger.info(f"Got positions for owner id = {self.request.user.id}")

        return positions


class PositionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """Generic API for position PUT, GET, DELTE methods."""

    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated,
                          IsPositionOwner)


class BusinessesListCreateAPIView(ListCreateAPIView):
    """List View for all businesses of current user & new business creation."""

    permission_classes = (IsAdminOrThisBusinessOwner & IsOwner,)

    def get_serializer_class(self):
        """Return specific Serializer.

        BusinessCreateSerializer for businesses creation or
        BusinessesSerializer for list.
        """
        if self.request.method == "POST":
            return BusinessCreateSerializer
        return BusinessesSerializer

    def get_queryset(self):
        """Filter businesses of current user(owner)."""
        owner = get_object_or_404(CustomUser, id=self.request.user.id)

        logger.info(f"Got businesses from owner {owner}")

        return owner.businesses.all()

    def post(self, request, *args, **kwargs):
        """Creates a business.

        Creates business and adds an authenticated user as an owner to it.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save(owner=request.user)

        logger.info(f"{business} was created")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BusinessDetailRUDView(RetrieveUpdateDestroyAPIView):
    """RUD View for access business detail information or/and edit it.

    RUD - Retrieve, Update, Destroy.
    """

    permission_classes = (IsAdminOrThisBusinessOwner | ReadOnly,)
    queryset = Business.objects.all()

    def get_serializer_class(self):
        """Gets different serializers depending on current user roles.

        BusinessAllDetailSerializer for owner of current business or
        BusinessDetailSerializer for others.
        """
        try:
            is_owner = self.request.user.is_owner
            if is_owner and (self.get_object().owner == self.request.user):
                return BusinessGetAllInfoSerializers
        except AttributeError:
            logger.warning(
                f"{self.request.user} is not a"
                "authorised to access this content",
            )
        return BusinessDetailSerializer


class ReviewAddView(GenericAPIView):
    """Create Review view.

    This class represents a view which is accessed when someone
    is trying to create a new Review. It makes use of the POST method,
    other methods are not allowed in this view.
    """

    serializer_class = ReviewAddSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, user):
        """This is a POST method of the view."""
        serializer = ReviewAddSerializer(data=request.data)
        author = self.request.user
        to_user = CustomUser.objects.get(pk=user)
        if serializer.is_valid():
            serializer.save(
                from_user=author,
                to_user=to_user,
            )
            logger.info(
                f"User {author} (id = {author.id}) posted a review for"
                f"{to_user} (id = {to_user.id})",
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            logger.info(
                "Error validating review: "
                f"Field {serializer.errors.popitem()}",
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AllServicesListCreateView(ListCreateAPIView):
    """ListView to display all services or service creation."""

    permission_classes = [IsOwner | ReadOnly]

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    logger.debug("View to display all services that can be provided.")


class ServiceUpdateView(RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating or deleting service info."""

    permission_classes = [IsOwner | ReadOnly]

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    logger.debug("A view for retrieving, updating or deleting a service instance.")


class UserViewSet(DjoserUserViewSet):
    """This class is implemented to disable djoser DELETE method."""

    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        """Delete is now forbidden for this method."""
        return super().me(request, *args, **kwargs)
