# Generated by Django 4.1.3 on 2022-12-24 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0039_alter_event_weekdays'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='weekdays',
        ),
    ]