# Generated by Django 5.1.3 on 2024-11-13 05:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("chat", "0001_initial"),
        ("expert", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatroom",
            name="expert",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="expert.expert"),
        ),
    ]
