# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse

from apps.accounts.utils import user_avatar_upload_path
from apps.core.utils import delete_image_and_thumbnails
from apps.core.validators import validate_image_file, validate_image_size


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

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        elif self.email:
            return self.email

    def clean(self):
        if self.email:
            qs = User.objects.filter(email__iexact=self.email).exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {
                        "email": "User with this email already exists.",
                    }
                )

    def save(self, *args, **kwargs):
        # Find is old image exists and is not the same as the new one
        if self.pk:
            old_image = self._meta.model.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                delete_image_and_thumbnails(old_image)
        self.full_clean()

        super().save(*args, **kwargs)

    def delete(self):
        if self.image:
            delete_image_and_thumbnails(self.image)
        super().delete()

    def get_absolute_url(self):
        return reverse("accounts:user_profile", kwargs={"user_id": self.id})
