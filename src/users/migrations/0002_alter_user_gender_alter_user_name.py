# Generated by Django 5.1.3 on 2024-11-16 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="gender",
            field=models.CharField(choices=[("M", "남성"), ("F", "여성")], max_length=6),
        ),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(max_length=25),
        ),
    ]
