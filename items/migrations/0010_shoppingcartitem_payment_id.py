# Generated by Django 5.1.3 on 2025-01-07 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0009_alter_category_slug_alter_item_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcartitem",
            name="payment_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
