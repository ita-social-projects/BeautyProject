"""This module provides you with all needed utility functions"""

import os
from random import randint
from datetime import datetime, timedelta
from typing import Tuple


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
        if instance.id:
            new_name = instance.id
        else:
            new_name = instance.__class__.objects.all().last().id + 1

        new_path = os.path.join(instance.__class__.__name__.lower(),
                                f"{new_name}.{filename.split('.')[-1]}")

        if hasattr(instance, "avatar"):
            image = instance.avatar.path
        else:
            image = instance.logo.path

        path = os.path.join(os.path.split(image)[0], new_path)

        if os.path.exists(path):
            os.remove(path)
        return new_path


def get_random_start_end_datetime() -> Tuple[datetime, datetime]:
    """Gives random times for start, end of the working day"""
    start_time = datetime(
            2022, randint(1, 12), randint(1, 28), randint(0, 23)
        )
    return start_time, start_time + timedelta(hours=8)
