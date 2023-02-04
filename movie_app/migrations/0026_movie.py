# Generated by Django 4.1.2 on 2023-02-02 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0025_country_language_film_country_film_lang_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie_app.film')),
                ('serie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie_app.serie')),
            ],
        ),
    ]