"""Module for all custom project tokens."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import logging

logger = logging.getLogger(__name__)


class OrderApprovingTokenGenerator(PasswordResetTokenGenerator):
    """The class creates an order token for sending an email
     message to the specialist to approve.
     """

    def _make_hash_value(self, order: object, timestamp: int) -> str:
        """Hash the order's primary key, status, and some order
        state(update_at) that's sure to change after a status reset
        to produce a token that is invalidated when it's used.

        Running this data through salted_hmac() prevents password cracking
        attempts using the reset token, provided the secret isn't compromised.

        Args:
            order (object): order instance
            timestamp (int): token creation timestamp
        Returns (str): hash value
        """
        # Truncate microseconds so that tokens are consistent even if the
        # database doesn't support microseconds.
        update_at_timestamp = order.update_at.replace(
            microsecond=0, tzinfo=None).timestamp()

        logger.info(f"Token for {order} was created")

        return f"{order.pk}{order.status}{update_at_timestamp}{timestamp}"
