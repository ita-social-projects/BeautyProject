"""This module provides you with all needed utility functions."""

import os

from datetime import timedelta, datetime, time

from typing import Tuple
from django.forms import ValidationError
import pytz
from rest_framework.reverse import reverse
from templated_mail.mail import BaseEmailMessage
from faker import Faker
from django.utils import timezone
from random import choice, randint
import calendar


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
    week_days = [day.capitalize()
                 for day in calendar.HTMLCalendar.cssclasses]
    return {day: [start_time, end_time] for day in week_days}


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


def string_interval_to_time_interval(str_interval: list):
    """Returns list of time objects."""
    return (string_to_time(str_interval[0]),
            string_to_time(str_interval[1]))


def is_inside_interval(main_interval: tuple, inner_interval: tuple):
    """Return True if inner interval is inside main_interval."""
    return (
        inner_interval[0] >= main_interval[0]
    ) and (
        inner_interval[1] <= main_interval[1]
    )


def is_working_time_reduced(working_time, new_working_time):
    """Returns true, if any day hours was reduced."""
    changed_days = set(working_time).intersection(new_working_time)
    for day in changed_days:

        if working_time[day] == new_working_time[day]:
            continue
        if len(working_time[day]) < len(new_working_time[day]):
            continue
        if len(working_time[day]) > len(new_working_time[day]):
            return True

        new_interval = string_interval_to_time_interval(
            new_working_time[day],
        )

        old_interval = string_interval_to_time_interval(
            working_time[day],
        )
        if is_inside_interval(old_interval, new_interval):
            return True
    return False


def is_order_fit_working_time(order, working_time: dict):
    """Returns True if order fit working_time."""
    week_days = [day.capitalize()
                 for day in calendar.HTMLCalendar.cssclasses]

    order_day = order.start_time.weekday()
    # If day became weekend
    if working_time[week_days[order_day]] == []:
        return False

    order_interval = [order.start_time.time(), order.end_time.time()]
    # If working day not changed (missing field in patch)
    try:
        working_interval = string_interval_to_time_interval(
            working_time[week_days[order_day]],
        )
    except KeyError:
        return True
    return is_inside_interval(working_interval, order_interval)


def get_working_time_from_dict(data) -> dict:
    """Raises errors if validation fails, returns working_time."""
    week_days = [day.capitalize() for day in calendar.HTMLCalendar.cssclasses]
    days_in_data = set(week_days).intersection(set(data.keys()))
    working_time = {day: [] for day in days_in_data}

    for day in days_in_data:

        amount_of_data = len(data[day])
        if amount_of_data not in [0, 2]:
            raise ValidationError(
                {day: "Must contain 2 elements or 0."},
            )

        if amount_of_data == 2:

            try:
                opening_time = string_to_time(data[day][0])
                closing_time = string_to_time(data[day][1])
                working_time[day].append(time_to_string(opening_time))
                working_time[day].append(time_to_string(closing_time))
            except ValueError:
                raise ValidationError(
                    {day: "Day schedule does not match the template\
                            ['HH:MM', 'HH:MM']."},
                )

            if opening_time > closing_time:

                raise ValidationError(
                    {day:
                        "working hours must begin before they end."},
                )

            if opening_time == closing_time:
                working_time[day] = []

    return working_time
