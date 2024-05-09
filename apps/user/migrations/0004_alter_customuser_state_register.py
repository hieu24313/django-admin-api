# Generated by Django 4.2.11 on 2024-04-02 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_customuser_state_register'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='state_register',
            field=models.CharField(blank=True, choices=[('INFOR', 'INFOR'), ('SHARE', 'SHARE'), ('DONE', 'DONE')], max_length=5, null=True),
        ),
    ]