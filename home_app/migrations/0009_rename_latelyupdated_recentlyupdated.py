# Generated by Django 4.1.2 on 2023-02-06 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0026_movie'),
        ('home_app', '0008_latelyupdated'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LatelyUpdated',
            new_name='RecentlyUpdated',
        ),
    ]