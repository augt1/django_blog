# Generated by Django 5.2.3 on 2025-07-02 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='published',
        ),
        migrations.AddField(
            model_name='post',
            name='publish',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
