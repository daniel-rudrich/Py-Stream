# Generated by Django 3.1.5 on 2021-09-29 09:32

from django.db import migrations, models
import streamdeck.models


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0007_auto_20210922_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamdeck',
            name='screensaver_image',
            field=models.FileField(blank=True, default='F:\\Uni\\Master\\5.Semester SS2021\\Masterarbeit\\git-repo\\streamdeck-application\\src\\media/assets/default_image.png', null=True, upload_to=streamdeck.models.get_image_path_screensaver),
        ),
    ]
