# Generated by Django 4.1.2 on 2022-12-01 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='slider',
            name='is_active',
            field=models.BooleanField(default=True, unique=True),
            preserve_default=False,
        ),
    ]