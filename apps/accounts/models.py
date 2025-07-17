# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.accounts.utils import user_avatar_upload_path
from apps.core.utils import delete_image_and_thumbanails
from apps.core.validators import validate_image_size


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
        ],
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bio",
        help_text="Short biography (optional).",
    )

    def save(self, *args, **kwargs):
        # Find is old image exists and is not the same as the new one
        if self.pk:
            old_image = self._meta.model.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                delete_image_and_thumbanails(old_image)

        super().save(*args, **kwargs)
    
    def delete(self):
        if self.image:
            delete_image_and_thumbanails(self.image)
        super().delete()
