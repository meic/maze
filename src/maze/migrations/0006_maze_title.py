# Generated by Django 3.2.7 on 2021-09-10 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maze', '0005_auto_20210906_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='maze',
            name='title',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
