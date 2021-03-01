# Generated by Django 3.1.5 on 2021-02-28 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('streamdeck', '0010_command_active_directory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotkeys',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key1', models.IntegerField()),
                ('key2', models.IntegerField(blank=True, null=True)),
                ('key3', models.IntegerField(blank=True, null=True)),
                ('key4', models.IntegerField(blank=True, null=True)),
                ('key5', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='command',
            name='value',
        ),
        migrations.AddField(
            model_name='command',
            name='hotkeys',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='streamdeck.hotkeys'),
        ),
    ]
