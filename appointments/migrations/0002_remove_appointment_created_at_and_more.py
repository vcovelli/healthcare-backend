# Generated by Django 5.1.4 on 2025-01-17 17:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="appointment",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="date_time",
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="description",
        ),
        migrations.RemoveField(
            model_name="appointment",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="appointment",
            name="date",
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="appointment",
            name="time",
            field=models.TimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="appointment",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="appointment",
            name="title",
            field=models.CharField(max_length=225),
        ),
    ]
