# Generated by Django 5.1.3 on 2024-12-16 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0002_alter_item_submission_review_message"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="submission_review_message",
            field=models.TextField(blank=True, default="", null=True),
        ),
    ]
