# Generated by Django 3.1.5 on 2021-01-21 11:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0002_streamdeck_brightness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='command',
            name='following_command',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='streamdeck.command'),
        ),
        migrations.AlterField(
            model_name='streamdeckkey',
            name='change_to_folder',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='folder_to_change', to='streamdeck.folder'),
        ),
        migrations.AlterField(
            model_name='streamdeckkey',
            name='command',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='streamdeck.command'),
        ),
    ]
