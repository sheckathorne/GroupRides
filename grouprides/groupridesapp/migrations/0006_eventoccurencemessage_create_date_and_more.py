# Generated by Django 4.1.3 on 2022-11-25 13:21

import datetime
from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0005_club_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventoccurencemessage',
            name='create_date',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2022, 11, 25, 13, 21, 11, 699674, tzinfo=datetime.timezone.utc), verbose_name='Date Created'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eventoccurencemessage',
            name='message',
            field=tinymce.models.HTMLField(blank=True, default=''),
        ),
    ]
