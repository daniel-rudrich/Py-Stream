# Generated by Django 3.1.5 on 2021-02-24 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0008_auto_20210224_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='command',
            name='command_type',
            field=models.CharField(choices=[('shell', 'shell'), ('hotkey', 'hotkey')], default='shell', max_length=6),
        ),
    ]
