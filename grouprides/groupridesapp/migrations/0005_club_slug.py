# Generated by Django 4.1.3 on 2022-11-24 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0004_alter_event_privacy_alter_eventoccurence_privacy_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='slug',
            field=models.SlugField(default='shawnee-trail-cycling-club'),
            preserve_default=False,
        ),
    ]
