# Generated by Django 3.2.6 on 2021-08-13 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Maze',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('height', models.IntegerField()),
                ('width', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('seen', models.BooleanField(default=False)),
                ('path_north', models.BooleanField(default=False)),
                ('path_south', models.BooleanField(default=False)),
                ('path_east', models.BooleanField(default=False)),
                ('path_west', models.BooleanField(default=False)),
                ('maze', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maze.maze')),
            ],
        ),
    ]
