# Generated by Django 4.2.3 on 2024-04-08 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0006_room_is_used_randomqueue_privatequeue"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="is_accepted",
            field=models.BooleanField(default=False),
        ),
    ]
