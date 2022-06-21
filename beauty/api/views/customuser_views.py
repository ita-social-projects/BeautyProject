"""This module provides all user's views."""

import logging

from django.contrib.auth.models import Group
from api.models import Invitation, CustomUser, Position
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from api.serializers.customuser_serializers import InviteUserCreate
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.response import Response
from rest_framework import status
from beauty.tokens import SpecialistInviteTokenGenerator
from beauty.utils import SpecialistAnswerEmail


logger = logging.getLogger(__name__)


class InviteRegisterView(GenericAPIView):
    """This class is used for registration via the invite link.

    Attributes:
        invitation (Invitation): encoded invitation id
        token (str): token to check that request is correct

    Returns:
        HTTP 200: Accepted, token valid.
        HTTP 400: {"serializer": "Wrong input data"}
        HTTP 400: {"token": "Token is invalid"}

    """

    serializer_class = InviteUserCreate
    permission_classes = (AllowAny,)

    def post(self, request, invite, token):
        """This method is used to register through an invitation.

        After registration, this method makes user a Specialist and assigns
        the user to a Position in question. Invitation is deleted.
        """
        serializer = self.get_serializer(data=request.data)
        invitation = Invitation.objects.get(pk=force_str(urlsafe_base64_decode(invite)))
        owner = Position.objects.get(pk=invitation.position.id).business.owner

        if SpecialistInviteTokenGenerator().check_token(invitation, token):
            if serializer.is_valid():
                serializer.save(
                    email=invitation.email,
                    is_active=True,
                )
                user = CustomUser.objects.get(email=invitation.email)
                specialist_group = Group.objects.get(name="Specialist")
                specialist_group.user_set.add(user)
                position = Position.objects.get(pk=invitation.position.id)
                position.specialist.set((user,))
                invitation.delete()
                position.save()
                SpecialistAnswerEmail(
                    request=request,
                    context={
                        "invite": invitation,
                        "answer": "accepted",
                    },
                ).send(to=[owner.email])
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"serializer": "Wrong input data"},
                )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"token": "Token is invalid"},
            )
