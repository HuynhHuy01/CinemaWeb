# Generated by Django 5.0.6 on 2024-10-24 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0041_alter_shows_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='uuid',
        ),
        migrations.AddField(
            model_name='bookings',
            name='bookid',
            field=models.CharField(blank=True, editable=False, max_length=8, unique=True),
        ),
    ]