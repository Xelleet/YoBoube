# Generated by Django 4.2.20 on 2025-05-21 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_videoview'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='is_short',
            field=models.BooleanField(default=False),
        ),
    ]
