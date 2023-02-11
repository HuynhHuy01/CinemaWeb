# Generated by Django 4.1.2 on 2023-02-10 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_app', '0028_delete_movie'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='trailer',
            field=models.FileField(blank=True, null=True, upload_to='uploads/trailers'),
        ),
        migrations.AddField(
            model_name='serie',
            name='trailer',
            field=models.FileField(blank=True, null=True, upload_to='uploads/trailers'),
        ),
    ]
