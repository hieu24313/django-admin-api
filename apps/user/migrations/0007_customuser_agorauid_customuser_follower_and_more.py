# Generated by Django 4.2.3 on 2024-04-03 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0006_alter_customuser_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="agoraUID",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="follower",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customuser",
            name="following",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_block",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_busy",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_fake",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customuser",
            name="is_live",
            field=models.BooleanField(default=False),
        ),
    ]