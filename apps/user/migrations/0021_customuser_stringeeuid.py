# Generated by Django 4.2.3 on 2024-04-19 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0020_alter_baseinformation_character_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="stringeeUID",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]