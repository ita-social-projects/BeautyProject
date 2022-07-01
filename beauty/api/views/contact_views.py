"""This module provides all views for website support."""

import logging

from beauty import settings
from api.serializers.contact_form_serializer import ContactFormSerializer

from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import redirect
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

logger = logging.getLogger(__name__)


class ContactFormView(CreateAPIView):
    """CreateAPIView for web site support form."""
    serializer_class = ContactFormSerializer

    def post(self, request, *args, **kwargs):
        """This method is used to send users questions to website's support."""
        serializer = ContactFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject = "Beauty Support"
        req_template = render_to_string("email/support_request.html", request.data)
        resp_template = render_to_string("email/support_request_confirmation.html", request.data)
        try:
            send_mail(subject, req_template, settings.EMAIL_HOST_USER,
                      ["testbeautyproject@gmail.com"], html_message=req_template)
            send_mail(subject, resp_template, settings.EMAIL_HOST_USER,
                      [request.data["email"]], html_message=resp_template)

            logger.info("Email was sent")
        except BadHeaderError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return redirect("api:contact-form")
