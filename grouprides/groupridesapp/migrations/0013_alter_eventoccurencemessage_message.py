# Generated by Django 4.1.3 on 2022-11-27 23:02

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0012_alter_eventoccurencemessage_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoccurencemessage',
            name='message',
            field=tinymce.models.HTMLField(),
        ),
    ]