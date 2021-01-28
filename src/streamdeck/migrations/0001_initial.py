# Generated by Django 3.1.5 on 2021-01-27 10:45

from django.db import migrations, models
import django.db.models.deletion
import streamdeck.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Command', max_length=100)),
                ('command_string', models.TextField()),
                ('value', models.IntegerField(blank=True, null=True)),
                ('following_command', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='streamdeck.command')),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Streamdeck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('serial_number', models.CharField(max_length=50)),
                ('brightness', models.IntegerField(default=30)),
            ],
        ),
        migrations.CreateModel(
            name='StreamdeckModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('key_count', models.IntegerField()),
                ('keys_per_row', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='StreamdeckKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('text', models.CharField(blank=True, max_length=50)),
                ('image_source', models.ImageField(blank=True, null=True, upload_to=streamdeck.models.get_image_path)),
                ('change_to_folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='change_keys', to='streamdeck.folder')),
                ('command', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='streamdeck.command')),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keys', to='streamdeck.folder')),
                ('streamdeck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamdeck.streamdeck')),
            ],
        ),
        migrations.AddField(
            model_name='streamdeck',
            name='streamdeck_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streamdeck.streamdeckmodel'),
        ),
    ]
