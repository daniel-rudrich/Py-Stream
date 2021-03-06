# Generated by Django 3.1.5 on 2021-09-22 14:52

from django.db import migrations, models
import streamdeck.models


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0005_auto_20210916_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamdeck',
            name='screensaver_image',
            field=models.FileField(blank=True, null=True, upload_to=streamdeck.models.get_image_path_screensaver),
        ),
        migrations.AddField(
            model_name='streamdeck',
            name='screensaver_time',
            field=models.IntegerField(default=60),
        ),
    ]
