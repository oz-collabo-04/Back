# Generated by Django 5.1.3 on 2024-11-22 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="title",
            field=models.CharField(max_length=60),
        ),
    ]
