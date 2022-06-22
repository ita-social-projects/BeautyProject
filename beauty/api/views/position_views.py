"""This module provides all needed position views."""

import logging

from django.http import Http404
from django.db import IntegrityError
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework import status
from api.serializers.position_serializer import PositionInviteSerializer
from api.models import Position, CustomUser, Invitation
from api.permissions import IsPositionOwner
from beauty.tokens import SpecialistInviteTokenGenerator
from rest_framework.permissions import IsAuthenticated
from beauty.utils import PositionAcceptEmail, RegisterInviteEmail, SpecialistAnswerEmail
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
        email exists. If user exists, the user will recieve an invite with a
        link to confirm an invitation. Otherwise, there will be an email that
        invites to register on a site. There is no way for the owner to know
        if email exists in our database or not.

        Returns:
            HTTP 200: All is good, email was sent.
            HTTP 400: {"user": "User is already on the Position."}
            HTTP 400: {"email": ["Enter a valid email address."]}
            HTTP 400: {"error": "User has been already invited"}

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_to_send = request.data.get("email")
        position_to_invite = self.get_object()

        logger.info(
            f"{request.user} (id={request.user.id}) is inviting user with email "
            f"'{email_to_send}' to {position_to_invite} (id={position_to_invite.id}).")

        try:
            invite = Invitation(
                email=email_to_send,
                position=position_to_invite,
            )
            if self.check_user(email_to_send, position_to_invite):
                invite.save()
                logger.info("User exists, sending an invitation for a Position.")
                PositionAcceptEmail(
                    request=request,
                    context={"invite": invite},
                ).send(to=[email_to_send])
            else:
                invite.save()
                logger.info("User doesn't exist, sending an invitation for registration.")
                RegisterInviteEmail(
                    request=request,
                    context={"invite": invite},
                ).send(to=[email_to_send])
            return Response(status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "User has been already invited."},
            )

    def check_user(self, user_email, position):
        """This method checks that all requirements are satisfied."""
        try:
            user = get_object_or_404(CustomUser,
                                     email=user_email,
                                     )
            if not user.position_set.filter(id=position.id):
                return True
            else:
                raise ValidationError({"user": "User is already on the Position."}, code=400)
        except Http404:
            return False


class InviteSpecialistApprove(GenericAPIView):
    """This view is used to accept an offer for a Position."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, email, position, token, answer):
        """GET method for accepting an invitation for the Position.

        Attributes:
            email (str): encoded email of the user who is invited
            position (str): encoded id of the position
            token (str): token to check that request is correct
            answer (str) ["confirm" | "decline"]: answer to the invitation

        Returns:
            HTTP 200: Accepted, token valid.
            HTTP 400: {"error": "Token is invalid"}

        """
        try:
            user_email = force_str(urlsafe_base64_decode(email))
            position_id = force_str(urlsafe_base64_decode(position))
            answer = force_str(urlsafe_base64_decode(answer))
            logging.info("Accept Invitation link is accessed. "
                         f"Info: User '{user_email}' and Position ID {position_id}")
            invitation = Invitation.objects.get(
                email=user_email,
                position=position_id,
            )
            if SpecialistInviteTokenGenerator().check_token(invitation, token):
                logger.info("Token is valid.")
                owner = Position.objects.get(pk=position_id).business.owner
                if answer == "decline":
                    SpecialistAnswerEmail(
                        request=request,
                        context={
                            "invite": invitation,
                            "answer": "declined",
                        },
                    ).send(to=[owner.email])
                    invitation.delete()
                else:
                    SpecialistAnswerEmail(
                        request=request,
                        context={
                            "invite": invitation,
                            "answer": "accepted",
                        },
                    ).send(to=[owner.email])
                    user = CustomUser.objects.get(email=user_email)
                    specialist_group = Group.objects.get(name="Specialist")
                    specialist_group.user_set.add(user)
                    position = Position.objects.get(pk=position_id)
                    position.specialist.set((user,))
                    invitation.delete()
                    position.save()
                return Response(status=status.HTTP_200_OK)
            else:
                logger.info("Token is invalid.")
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "Token is invalid"},
                )

        except Invitation.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "This link is not valid anymore."},
            )
