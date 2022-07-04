"""This module provides you with all needed utility functions."""

import os

from datetime import timedelta, datetime, time

from typing import Tuple, List
from django.forms import ValidationError
import pytz
from rest_framework.reverse import reverse
from templated_mail.mail import BaseEmailMessage
from faker import Faker
from django.utils import timezone
from random import choice, randint


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


def validate_rounded_minutes_seconds(time_value):
    """Validate time value.

    Time must have zero seconds and minutes multiples of 5
    """
    assert isinstance(time_value, (datetime, time, timedelta)), \
        "Only datetime, time or timedelta objects"

    if isinstance(time_value, (datetime, time)):
        if isinstance(time_value, datetime):
            time_value = time_value.time()

        if time_value.minute % 5 and time_value.second != 0:
            raise ValidationError(
                "Time value must have zero seconds and minutes multiples of 5",
                params={"value": time_value},
            )

    if isinstance(time_value, timedelta):
        if (time_value.seconds / 60) % 5:
            raise ValidationError(
                "Time value must have minutes multiples of 5",
                params={"value": time_value},
            )


def validate_working_time_json(json):
    """Validate json for working time for every day."""
    for value in json.values():
        map(validate_rounded_minutes_seconds, value)


def time_to_string(time):
    """Cast time to string HH:MM."""
    return time.strftime("%H:%M")


def string_to_time(string):
    """Cast string HH:MM to time."""
    return datetime.strptime(string, "%H:%M").time()


class PositionAcceptEmail(BaseEmailMessage):
    """This is an email for confirming Position."""

    template_name = "email/position_accept_email.html"

    def get_context_data(self):
        """Get context data for rendering HTML messages."""
        context = super().get_context_data()
        context.update(self.create_approve_link(context.get("invite")))
        return context

    def create_approve_link(self, invite: object):
        """This method creates approve link."""
        from djoser.utils import encode_uid

        params = {
            "email": encode_uid(invite.email),
            "position": encode_uid(invite.position.id),
            "token": invite.token,
        }

        return {"approve_link": reverse("api:position-approve",
                                        kwargs=params | {"answer": encode_uid("confirm")},
                                        request=None),
                "decline_link": reverse("api:position-approve",
                                        kwargs=params | {"answer": encode_uid("decline")},
                                        request=None),
                }


class RegisterInviteEmail(BaseEmailMessage):
    """This email is sent to invite to register on site."""

    template_name = "email/register_invite_email.html"

    def get_context_data(self):
        """Get context data for rendering HTML messages."""
        context = super().get_context_data()
        context.update(self.create_invite_link(context.get("invite")))
        return context

    def create_invite_link(self, invite: object):
        """This method creates invite link."""
        from djoser.utils import encode_uid

        return {
            "register_link": reverse(
                "api:register-invite",
                kwargs={
                    "invite": encode_uid(invite.id),
                    "token": invite.token,
                },
                request=None),
        }


class SpecialistAnswerEmail(BaseEmailMessage):
    """This email is sent to notify owner on the Specialist's decision."""

    template_name = "email/specialist_decision.html"


def generate_working_time(start_time: str, end_time: str):
    """Generates working time."""
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    return {day: [start_time, end_time] for day in weekdays}


def custom_exception_handler(exc, context):
    """Custom exceptions handler.

    Args:
        exc: exceptions list or dict
        context: context data includes information about view and request

    Returns: response data
    """
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, list):
        data_list = [o for o in response.data if o]
        error_list = []
        for data in data_list:
            error_list.append({response.data.index(data): data})
        response.data = error_list
    return response


class RoundedTime:
    """Class with rounded time.

    Provide time with zero seconds and minutes multiplied by 5
    """

    minutes = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55)

    @classmethod
    def calculate_rounded_time_minutes_seconds(cls):
        """Datetime rigth now with rounded time.

        Returns datetime.now() with edited minutes and seconds
        """
        return timezone.now().replace(
            hour=randint(1, 23), minute=choice(cls.minutes),
            second=0, microsecond=0,
        )

    @classmethod
    def get_rounded_duration(cls):
        """Return timedelta with minutes multiplied by 5."""
        return timedelta(minutes=choice(cls.minutes))


def get_order_expiration_time(order, date_time, time_delta_hours=3):
    """Get expiration time for order.

    Args:
        order: Order instance
        date_time: datetime data
        time_delta_hours: time delta hours from creating an order or starting a working day

    Returns: date time expired order

    """
    from api.views.schedule import get_working_day

    working_day = get_working_day(order.service.position, date_time)
    eta = date_time + timedelta(hours=time_delta_hours)
    last_week_day = (order.created_at + timedelta(days=7)).date()
    if last_week_day == date_time.date():
        return None
    if working_day:
        start_working_datetime, end_working_datetime = [datetime.strptime(t, "%H:%M")
                                                        for t in working_day]
        if start_working_datetime.time() < eta.time() < end_working_datetime.time():
            return eta
        elif start_working_datetime.time() > eta.time():
            naive_datetime = timezone.datetime.combine(
                eta.date(), (start_working_datetime + timedelta(hours=time_delta_hours)).time())
            return timezone.make_aware(naive_datetime)

    next_day = (date_time + timedelta(days=1)).replace(hour=0, minute=0, second=0)
    return get_order_expiration_time(order, next_day)


class AutoDeclineOrderEmail(BaseEmailMessage):
    """Class for sending an email message which renders HTML for it."""

    template_name = "email/order_auto_decline_email.html"


class Chart:
    """Class for storing data, required for making a chart.

    labels: List[str]
    data: List[int]
    """

    def __init__(self, labels: List[str], data: List[int]) -> None:
        """."""
        labels_is_str = all(isinstance(label, str) for label in labels)
        if not labels_is_str:
            raise ValueError("Labels must be str type")

        data_is_int = all(isinstance(el, int) for el in data)
        if not data_is_int:
            raise ValueError("Data elements must be int type")

        self.labels = labels
        self.data = data
