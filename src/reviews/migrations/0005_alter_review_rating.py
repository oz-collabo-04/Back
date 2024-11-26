# Generated by Django 5.1.3 on 2024-11-25 02:14

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0004_remove_review_title_alter_reviewimages_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.DecimalField(
                choices=[
                    (Decimal("0.5"), "zero_point_five"),
                    (Decimal("1.0"), "one"),
                    (Decimal("1.5"), "one_point_five"),
                    (Decimal("2.0"), "two"),
                    (Decimal("2.5"), "two_point_five"),
                    (Decimal("3.0"), "three"),
                    (Decimal("3.5"), "three_point_five"),
                    (Decimal("4.0"), "four"),
                    (Decimal("4.5"), "four_point_five"),
                    (Decimal("5.0"), "five"),
                ],
                decimal_places=1,
                max_digits=2,
            ),
        ),
    ]
