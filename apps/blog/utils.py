import os

from django.contrib.auth.models import Group
from django.utils import timezone


def post_image_upload_path(instance, filename):
    extension = filename.split(".")[-1]
    base_name = instance.slug

    filename = f"{base_name}.{extension}"

    created = instance.published_at or timezone.now()

    return os.path.join(
        "posts", f"{created.year}", f"{created.month}", f"post_{base_name}", filename
    )


def assign_user_groups(instance):
    if instance.author:
        authors_group, _ = Group.objects.get_or_create(name="Authors")
        print(f"Added {instance.author} to 'Authors' group")
        instance.author.groups.add(authors_group)

    if instance.editors.exists():
        editors_group, _ = Group.objects.get_or_create(name="Editors")
        for editor in instance.editors.all():
            print(f"Added {editor} to 'Editors' group")
            editor.groups.add(editors_group)
