# Generated by Django 3.1.5 on 2021-01-21 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0006_auto_20210121_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='command',
            name='value',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
