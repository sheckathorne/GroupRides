# Generated by Django 4.1.3 on 2022-11-17 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0010_event_max_riders_eventoccurence_max_riders'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='group_classification',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('N', 'Novice'), ('NA', 'None')], default='B', max_length=2, verbose_name='Classification'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='ride_pace',
            field=models.CharField(default='17-19', max_length=10, verbose_name='Pace'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventoccurence',
            name='group_classification',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('N', 'Novice'), ('NA', 'None')], default='17-19', max_length=2, verbose_name='Classification'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventoccurence',
            name='ride_pace',
            field=models.CharField(default='17-19', max_length=10, verbose_name='Pace'),
            preserve_default=False,
        ),
    ]
