# Generated by Django 5.0.6 on 2024-08-10 21:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0002_remove_accountmodel_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accountmodel",
            name="iam_provider_id",
            field=models.CharField(null=True),
        ),
    ]