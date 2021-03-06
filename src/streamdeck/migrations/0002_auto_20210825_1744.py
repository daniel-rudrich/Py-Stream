# Generated by Django 3.1.5 on 2021-08-25 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='streamdeckkey',
            name='font',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='streamdeckkey',
            name='text_color',
            field=models.CharField(default='white', max_length=20),
        ),
        migrations.AddField(
            model_name='streamdeckkey',
            name='text_position',
            field=models.CharField(choices=[('center', 'center'), ('top', 'top'), ('bottom', 'bottom')], default='center', max_length=6),
        ),
        migrations.AddField(
            model_name='streamdeckkey',
            name='text_size',
            field=models.IntegerField(default=14),
        ),
    ]
