"""This module is for testing position inviting."""

from djoser.utils import encode_uid
from django.test import TestCase
from django.core import mail
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from api.models import Invitation
from .factories import (CustomUserFactory,
                        PositionFactory,
                        GroupFactory)


class TestInvitePosition(TestCase):
    """This class represents a TestCase for inviting users."""

    def setUp(self) -> None:
        """This method sets up all the needed info for tests."""
        self.groups = GroupFactory.groups_for_test()
        self.position = PositionFactory()
        self.business = self.position.business
        self.owner = self.position.business.owner
        self.groups.owner.user_set.add(self.owner)
        self.specialist = CustomUserFactory()
        self.groups.specialist.user_set.add(self.specialist)
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_unauthorized_cant_invite(self):
        """Unauthorized user can't invite other users."""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        self.assertEqual(response.status_code, 401)

    def test_email_invitation_is_sent(self):
        """Owner can invite specialists to Position."""
        response = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        self.invitation = Invitation.objects.first()

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.specialist.email, mail.outbox[0].to)
        self.assertIn(self.position.name, mail.outbox[0].subject)
        self.assertIn(self.invitation.token, mail.outbox[0].html)

    def test_you_can_only_invite_one_time(self):
        """Owner can invite specialists to Position only once."""
        response_first = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        response_second = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        self.assertEqual(response_first.status_code, 200)
        self.assertEqual(response_second.status_code, 400)

    def test_specialist_can_decline(self):
        """Specialist can decline invitation."""
        response_invite = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        self.invitation = Invitation.objects.first()
        self.id_of_invitation = self.invitation.id
        response_decline = self.client.get(
            path=reverse("api:position-approve",
                         kwargs={
                             "email": encode_uid(self.invitation.email),
                             "position": encode_uid(self.invitation.position.id),
                             "token": self.invitation.token,
                             "answer": encode_uid("decline"),
                         },
                         ),
        )
        self.assertEqual(response_invite.status_code, 200)
        self.assertEqual(response_decline.status_code, 200)
        self.assertEqual(Invitation.objects.all().count(), 0)
        self.assertEqual(Invitation.objects.all().count(), 0)
        self.assertNotEqual(self.specialist, self.position.specialist.all().first())

    def test_specialist_can_approve(self):
        """Specialist can approve invitation."""
        response_invite = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        self.invitation = Invitation.objects.first()
        self.id_of_invitation = self.invitation.id
        response_decline = self.client.get(
            path=reverse("api:position-approve",
                         kwargs={
                             "email": encode_uid(self.invitation.email),
                             "position": encode_uid(self.invitation.position.id),
                             "token": self.invitation.token,
                             "answer": encode_uid("approve"),
                         },
                         ),
        )
        self.assertEqual(response_invite.status_code, 200)
        self.assertEqual(response_decline.status_code, 200)
        self.assertEqual(Invitation.objects.all().count(), 0)
        self.assertEqual(self.specialist, self.position.specialist.all().first())

    def test_cant_invite_specialist_if_already_appointed(self):
        """Owner can't invite to Position, if User is already appointed."""
        self.position.specialist.set((self.specialist,))
        response_invite = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": self.specialist.email},
        )
        self.assertEqual(response_invite.status_code, 400)

    def test_notregistered_user_is_invited(self):
        """Owner can invite other users if they are not registered."""
        email_for_register = "notregistered@gmail.com"
        response_invite = self.client.post(
            path=reverse("api:position-add-specialist",
                         kwargs={"pk": self.position.id}),
            data={"email": email_for_register},
        )
        self.invitation = Invitation.objects.first()

        self.assertEqual(response_invite.status_code, 200)
        self.assertIn(email_for_register, mail.outbox[0].to)
        self.assertIn(self.position.name, mail.outbox[0].subject)
        self.assertIn(self.invitation.token, mail.outbox[0].html)
