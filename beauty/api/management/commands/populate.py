"""This module provides a custom command 'populate'."""

from random import randint
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

    help = "Populates database with Random data for testing."

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
            ReviewFactory.create_batch(
                10,
                from_user=CustomUser.objects.get(pk=randint(0, 30)),
                to_user=CustomUser.objects.get(pk=randint(0, 30)),
            )
            self.stdout.write("Successfully populated database.")
        else:
            raise CommandError("Can't execute in production...")
