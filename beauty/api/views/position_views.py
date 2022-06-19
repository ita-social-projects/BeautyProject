"""This module provides all needed position views."""

import logging

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework import status
from api.serializers.position_serializer import PositionInviteSerializer
from api.models import Position, CustomUser
from api.permissions import IsPositionOwner
from beauty.tokens import SpecialistInviteTokenGenerator
from rest_framework.permissions import IsAuthenticated
from beauty.utils import PositionAcceptEmail, RegisterInviteEmail
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

logger = logging.getLogger(__name__)


class InviteSpecialistToPosition(GenericAPIView):
    """This view is used for inviting specialists for a position."""
    queryset = Position.objects.all()
    serializer_class = PositionInviteSerializer
    permission_classes = (IsAuthenticated, IsPositionOwner)

    def post(self, request, *args, **kwargs):
        """POST method for sending invites for a position.

        When business owner wants to add a specialist to a Position, the owner
        simply adds an email and sends a request. This request is headed to
        the serializer. Serializer's job is to check whether an email is correct
        (or it will result in a HTTP_400_BAD_REQUEST) and that the user with such
        an email exists. If user exists, the user will recieve an invite with a
        link to confirm an invitation. Otherwise, there will be an email that
        invites to register on a site. There is no way for the owner to know
        if email exists in our database or not.

        Attributes:
            pk (int): stores an id of the Position in question

        Returns:
            HTTP 200: Email was sent.
            HTTP 400: User is already on the Position.
            HTTP 400: Serializaer error, wron email.

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_to_send = request.data.get("email")
        position_to_invite = self.get_object()
        context = {
            "inviter": request.user,
            "email": email_to_send,
            "position": position_to_invite,
        }

        logger.info(
            f"{request.user} (id={request.user.id}) is inviting user with email "
            f"'{email_to_send}' to {position_to_invite} (id={position_to_invite.id}).")

        if self.check_user(email_to_send, position_to_invite):
            logger.info("User exists, sending an invitation for a Position.")
            PositionAcceptEmail(
                request=request,
                context=context,
            ).send(to=[email_to_send])
        else:
            logger.info("User doesn't exist, sending an invitation for registration.")
            RegisterInviteEmail(
                request=request,
                context=context,
            ).send(to=[email_to_send])
        return Response(status=status.HTTP_200_OK)

    def check_user(self, user_email, position):
        """This method checks that all requirements are satisfied."""
        try:
            user = get_object_or_404(CustomUser,
                                     email=user_email,
                                     groups__name="Specialist",
                                     )
            if not user.position_set.filter(id=position.id):
                return True
            else:
                raise ValidationError({"user": "User is already on the Position."}, code=400)
        except CustomUser.DoesNotExist:
            return False


class InviteSpecialistApprove(GenericAPIView):
    """This view is used to accept an offer for a Position."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, user, position, token):
        """GET method for accepting an invitation for the Position.

        Attributes:
            user (str): encoded id of the user who is invited
            position (str): encoded id of the position
            token (str): token to check that request is correct

        Returns:
            HTTP 200: Accepted, token valid.
            HTTP 400: Invalid token.

        """
        user_id = force_str(urlsafe_base64_decode(user))
        position_id = force_str(urlsafe_base64_decode(position))
        logging.info("Accept Invitation link is accessed. "
                     f"Info: User ID {user_id} and Position ID {position_id}")

        if SpecialistInviteTokenGenerator().check_token(request.user, token):
            logger.info("Token is valid.")
            user = CustomUser.objects.get(pk=user_id)
            specialist_group = Group.objects.get(name="Specialist")
            specialist_group.user_set.add(user)
            position = Position.objects.get(pk=position_id)
            position.specialist.set((user,))
            position.save()
            return Response(status=status.HTTP_200_OK)
        else:
            logger.info("Token is invalid.")
            return Response(status=status.HTTP_400_BAD_REQUEST)
