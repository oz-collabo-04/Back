# Generated by Django 5.1.3 on 2024-12-10 09:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0004_alter_cancelmanager_reservation_and_more"),
        ("reviews", "0006_alter_reviewimages_review"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="reservation",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="reservations.reservation"),
        ),
    ]