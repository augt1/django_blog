import os
from django.utils import timezone


def post_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    base_name = instance.slug

    filename = f"{base_name}.{extension}"

    created = instance.published_at or timezone.now()

    return os.path.join("posts", f"{created.year}", f"{created.month}" , f"post_{base_name}", filename)
