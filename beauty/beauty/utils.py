"""This module provides you with all needed utility functions."""

import os

from datetime import timedelta, datetime
from typing import Tuple
import pytz
from rest_framework.reverse import reverse
from templated_mail.mail import BaseEmailMessage
from faker import Faker
from .tokens import SpecialistInviteTokenGenerator

faker = Faker()


class ModelsUtils:
    """This class provides utility functions for models."""

    @staticmethod
    def upload_location(instance, filename: str) -> str:
        """This method purpose is to generate path for saving medial files.

        Args:
            instance: Instance of a model
            filename: Name of a media file

        Returns:
            str: Path to the media file
        """
        if instance.id:
            new_name = instance.id
        else:
            new_name = instance.__class__.objects.all().last().id + 1

        new_path = os.path.join(
            instance.__class__.__name__.lower(),
            f"{new_name}.{filename.split('.')[-1]}",
        )

        if hasattr(instance, "avatar"):
            image = instance.avatar.path
        else:
            image = instance.logo.path

        path = os.path.join(os.path.split(image)[0], new_path)

        if os.path.exists(path):
            os.remove(path)
        return new_path


def get_random_start_end_datetime() -> Tuple[datetime, datetime]:
    """Gives random times for start, end of the working day."""
    start_time = faker.date_time_this_century(tzinfo=pytz.UTC)
    return start_time, start_time + timedelta(hours=8)


class ApprovingOrderEmail(BaseEmailMessage):
    """Send approving order email.

    Send email message to the specialist for
    change order status with two links:
    - for approve order;
    - for decline order.
    """

    template_name = "email/order_approve.html"

    def get_context_data(self):
        """Get context data for rendering HTML messages."""
        context = super().get_context_data()

        order = context.get("order")

        context.update(order_approve_decline_urls(order))

        return context


class StatusOrderEmail(BaseEmailMessage):
    """Class for sending an email message which renders HTML for it."""

    template_name = "email/customer_order_status.html"


class CancelOrderEmail(BaseEmailMessage):
    """Class for sending an email message which renders HTML for it."""

    template_name = "email/order_cancel.html"


def order_approve_decline_urls(order: object, approve_name="url_for_approve",
                               decline_name="url_for_decline", request=None) -> dict:
    """Get URLs for approving and declining orders.

    Args:
        approve_name (str): key name for approving URL
        decline_name (str): key name for declining URL
        request: request data
        order (Order): Order instance

    Returns:
        urls(dict): dict with URLs
    """
    from djoser.utils import encode_uid

    urls = {}
    params = {"uid": encode_uid(order.pk), "token": order.token}

    url_approved_params = params | {"status": encode_uid("approved")}
    urls[approve_name] = reverse("api:order-approving",
                                 kwargs=url_approved_params, request=request)

    url_declined_params = params | {"status": encode_uid("declined")}
    urls[decline_name] = reverse("api:order-approving",
                                 kwargs=url_declined_params, request=request)
    return urls


def time_to_string(time):
    """Cast time to string HH:MM."""
    return time.strftime("%H:%M")


def string_to_time(string):
    """Cast string HH:MM to time."""
    return datetime.strptime(string, "%H:%M")


class PositionAcceptEmail(BaseEmailMessage):
    """This is an email for confirming Position."""

    template_name = "email/position_accept_email.html"

    def get_context_data(self):
        """Get context data for rendering HTML messages."""
        context = super().get_context_data()

        pos = context.get("position")
        user = context.get("inviter")
        email = context.get("email")

        context.update(self.create_approve_link(user.id, pos, email))

        return context

    def create_approve_link(self, inviter: int, position: int, email: str):
        """This method creates approve link."""
        from api.models import CustomUser
        from djoser.utils import encode_uid

        user = CustomUser.objects.get(email=email)
        params = {
            "user": encode_uid(inviter),
            "position": encode_uid(position),
            "token": SpecialistInviteTokenGenerator().make_token(user=user),
        }

        return {"approve_link": reverse("api:position-approve",
                                        kwargs=params, request=None),
                }


class RegisterInviteEmail(BaseEmailMessage):
    """This email is sent to invite to register on site."""

    template_name = "email/register_invite_email.html"
