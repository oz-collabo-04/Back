# Generated by Django 5.1.3 on 2024-11-29 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0004_alter_notification_notification_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="message",
            field=models.TextField(),
        ),
    ]