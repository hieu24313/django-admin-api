# Generated by Django 4.2.3 on 2024-04-15 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0012_alter_fileupload_file_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="defaultavatar",
            name="key",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
