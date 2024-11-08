# Generated by Django 5.0.6 on 2024-11-06 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0055_alter_comment_options_alter_comment_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='rating',
            field=models.IntegerField(choices=[(1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')]),
        ),
    ]