"""This module provides a custom command 'populate'."""

from random import choices
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from api.tests.factories import (CustomUserFactory,
                                 OrderFactory,
                                 ReviewFactory)
from api.models import CustomUser


class Command(BaseCommand):
    """This class represents a 'populate' custom command.

    Command can clear the whole database, create a superuser and populate db.
    """

    user_ids = [num for num in range(1, 30)]
    help = "Populates database with Random data for testing."   # noqa

    def add_arguments(self, parser):
        """This method adds optional arguments to the command."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Cleans out the database, production safe",
        )
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Creates superuser, production safe",
        )

    def handle(self, *args, **options):
        """This method does all the logic for populating db."""
        if settings.DEBUG:
            if options["force"]:
                call_command("flush")
                call_command("makemigrations")
                call_command("migrate")
            if options["superuser"]:
                call_command("createsuperuser")
            CustomUserFactory.create_batch(15, is_active=True)
            OrderFactory.create_batch(15)
            for _ in range(15):
                reviewer_id, reviewee_id = choices(self.user_ids, k=2)
                ReviewFactory.create(
                    from_user=CustomUser.objects.get(pk=reviewer_id),
                    to_user=CustomUser.objects.get(pk=reviewee_id),
                )
            self.stdout.write("Successfully populated database.")
        else:
            raise CommandError("Can't execute in production...")
