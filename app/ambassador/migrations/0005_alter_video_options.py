# Generated by Django 5.1.2 on 2024-12-02 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ambassador', '0004_alter_video_location'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['-created_at'], 'verbose_name': 'Видео', 'verbose_name_plural': 'Видео'},
        ),
    ]