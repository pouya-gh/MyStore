# Generated by Django 5.1.3 on 2025-01-01 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0006_alter_category_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="currency",
            field=models.TextField(
                choices=[("USD", "USA Dollar"), ("IRR", "Iranian Rial")],
                default="IRR",
                max_length=3,
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="price",
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=12),
        ),
    ]
