# Generated by Django 4.1.3 on 2022-11-21 04:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0002_rename_route_url_route_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventoccurencemember',
            name='event_occurence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_occurence_member', to='groupridesapp.eventoccurence'),
        ),
    ]