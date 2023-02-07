# Generated by Django 4.1.2 on 2023-02-07 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0026_movie'),
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_movies',
            field=models.ManyToManyField(blank=True, related_name='saved_movies', to='movie_app.movie'),
        ),
    ]