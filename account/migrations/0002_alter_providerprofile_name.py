# Generated by Django 5.1.3 on 2024-12-03 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="providerprofile",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
