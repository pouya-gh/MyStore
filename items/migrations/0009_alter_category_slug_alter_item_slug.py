# Generated by Django 5.1.3 on 2025-01-04 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0008_shoppingcartitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="slug",
            field=models.SlugField(max_length=250, unique=True),
        ),
    ]
