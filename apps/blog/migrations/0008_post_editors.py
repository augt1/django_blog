# Generated by Django 5.2.3 on 2025-07-16 09:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_post_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='editors',
            field=models.ManyToManyField(blank=True, related_name='editable_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
