# Generated by Django 3.2.25 on 2024-10-21 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_rename_prise_recipe_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
