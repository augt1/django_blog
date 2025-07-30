from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from apps.core.upload_paths import user_avatar_upload_path
from apps.core.validators import validate_image_file, validate_image_size

import uuid

class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """

    username = models.CharField(
        "username",
        max_length=150,
        blank=True,
        null=True,
    )

    email = models.EmailField(
        "email address",
        unique=True, 
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )

    image = models.ImageField(
        upload_to=user_avatar_upload_path,
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="Upload a profile picture (optional).",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"]),
            validate_image_size,
            validate_image_file,
        ],
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bio",
        help_text="Short biography (optional).",
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):
        if self.first_name and self.last_name:
            return self.get_full_name()
        elif self.first_name:
            return self.get_short_name()
        elif self.email:
            return self.email

    def get_absolute_url(self):
        return reverse("accounts:user_profile", kwargs={"user_id": self.uuid})
