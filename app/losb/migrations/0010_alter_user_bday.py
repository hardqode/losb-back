# Generated by Django 5.1.2 on 2024-10-16 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('losb', '0009_alter_user_bday'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bday',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
