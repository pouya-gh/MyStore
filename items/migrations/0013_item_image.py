# Generated by Django 5.1.3 on 2025-01-27 07:12

import items.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0012_remove_shoppingcartitem_payment_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="image",
            field=models.ImageField(
                blank=True, upload_to=items.models._item_image_directory_path
            ),
        ),
    ]
