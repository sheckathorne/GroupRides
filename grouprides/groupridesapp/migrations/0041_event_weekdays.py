# Generated by Django 4.1.3 on 2022-12-24 12:32

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0040_remove_event_weekdays'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='weekdays',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1), blank=True, choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], default=list, null=True, size=None),
        ),
    ]
