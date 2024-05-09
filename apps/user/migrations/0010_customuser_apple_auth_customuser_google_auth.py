# Generated by Django 4.2.3 on 2024-04-05 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0009_remove_customuser_is_coin_plan"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="apple_auth",
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="google_auth",
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]