# Generated by Django 5.2.3 on 2025-07-04 11:50

import django.core.validators
from django.db import migrations, models

import apps.core.upload_paths


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_bio_user_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="image",
            field=models.ImageField(
                blank=True,
                help_text="Upload a profile picture (optional).",
                null=True,
                upload_to=apps.core.upload_paths.user_avatar_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png", "gif"]
                    )
                ],
                verbose_name="Avatar",
            ),
        ),
    ]
