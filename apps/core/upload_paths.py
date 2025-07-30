import os

from django.utils import timezone
from django.utils.text import slugify


def post_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    base_name = instance.slug

    filename = f"{base_name}.{extension}"

    created = instance.published_at or timezone.now()

    return os.path.join(
        "posts", f"{created.year}", f"{created.month}", f"post_{base_name}", filename
    )


def user_avatar_upload_path(instance, filename):
    extension = filename.split(".")[-1]

    if instance.get_full_name():
        base_name = slugify(instance.get_full_name())

    else:
        base_name = slugify(instance.email.split("@")[0])

    filename = f"{instance.uuid}-{base_name}.{extension}"

    return os.path.join("avatars", f"user_{base_name}", filename)
