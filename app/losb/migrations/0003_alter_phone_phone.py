# Generated by Django 5.1.2 on 2024-10-16 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('losb', '0002_remove_user_last_login_remove_user_last_loginnn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='phone',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
