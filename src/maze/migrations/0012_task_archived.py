# Generated by Django 4.2.11 on 2024-03-21 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("maze", "0011_set_last_updated"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="archived",
            field=models.BooleanField(default=False),
        ),
    ]
