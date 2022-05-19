"""This module provides you with all needed utility functions"""

import os


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
