# Generated by Django 4.2.11 on 2024-05-04 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_book_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fiendship',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]