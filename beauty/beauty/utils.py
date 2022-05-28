"""This module provides you with all needed utility functions"""

import os
from rest_framework.reverse import reverse
from templated_mail.mail import BaseEmailMessage
from beauty.tokens import OrderApprovingTokenGenerator


class ModelsUtils:
    """This class provides utility functions for models"""

    @staticmethod
    def upload_location(instance, filename: str) -> str:
        """This method purpose is to generate path for saving medial files

        Args:
            instance: Instance of a model
            filename: Name of a media file

        Returns:
            str: Path to the media file
        """
        new_name = instance.id if instance.id else instance.__class__.objects.all().last().id + 1
        new_path = os.path.join(instance.__class__.__name__.lower(),
                                f"{new_name}.{filename.split('.')[-1]}")
        if hasattr(instance, "avatar"):
            image = instance.avatar.path
        else:
            image = instance.logo.path
        path = os.path.join(os.path.split(image)[0],
                            new_path)
        if os.path.exists(path):
            os.remove(path)
        return new_path


class ApprovingOrderEmail(BaseEmailMessage):
    """Send email message to the specialist for change order status with two links:
    - for approve order;
    - for decline order.
    """

    template_name = "email/order_approve.html"

    def get_context_data(self):
        """Get context data for rendering HTML messages."""
        from djoser.utils import encode_uid
        context = super().get_context_data()

        order = context.get("order")
        token = OrderApprovingTokenGenerator().make_token(order)

        params = {"uid": encode_uid(order.pk), "token": token}

        url_approved_params = params | {"status": encode_uid("approved")}
        context["url_approved"] = reverse("api:order-approving",
                                          kwargs=url_approved_params)

        url_declined_params = params | {"status": encode_uid("declined")}
        context["url_approved"] = reverse("api:order-approving",
                                          kwargs=url_approved_params)

        context["url_declined"] = reverse("api:order-approving",
                                          kwargs=url_declined_params)
        return context


class StatusOrderEmail(BaseEmailMessage):
    """Class for sending an email message which renders HTML for it."""

    template_name = "email/customer_order_status.html"
