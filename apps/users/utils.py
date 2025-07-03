import os
from django.utils.text import slugify


def user_avatar_upload_path(instance, filename):
    extension = filename.split(".")[-1]

    if instance.get_full_name():
        base_name = slugify(instance.get_full_name())
    elif instance.username:
        base_name = slugify(instance.username)
    elif instance.email:
        base_name = slugify(instance.email.split("@")[0])
    else:
        base_name = "user"

    filename = f"{base_name}.{extension}"

    return os.path.join("avatars", f"user_{base_name}", filename)