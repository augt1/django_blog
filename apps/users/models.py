
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.utils import user_avatar_upload_path


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """

    image = models.ImageField(
        upload_to=user_avatar_upload_path,
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="Upload a profile picture (optional).",
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bio",
        help_text="Short biography (optional).",
    )
