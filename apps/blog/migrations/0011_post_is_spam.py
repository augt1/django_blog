# Generated by Django 5.2.3 on 2025-07-21 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_comment_is_spam_alter_post_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_spam',
            field=models.BooleanField(default=False),
        ),
    ]
