# Generated by Django 4.1.3 on 2022-11-20 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0014_route_start_location_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='ride_pace',
        ),
        migrations.RemoveField(
            model_name='eventoccurence',
            name='ride_pace',
        ),
        migrations.AddField(
            model_name='event',
            name='lower_pace_range',
            field=models.PositiveIntegerField(default=1, verbose_name='Lower Pace Range'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='upper_pace_range',
            field=models.PositiveIntegerField(default=1, verbose_name='Upper Pace Range'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventoccurence',
            name='lower_pace_range',
            field=models.PositiveIntegerField(default=1, verbose_name='Lower Pace Range'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventoccurence',
            name='upper_pace_range',
            field=models.PositiveIntegerField(default=1, verbose_name='Upper Pace Range'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='max_riders',
            field=models.PositiveIntegerField(verbose_name='Max Riders'),
        ),
        migrations.AlterField(
            model_name='eventoccurence',
            name='max_riders',
            field=models.PositiveIntegerField(verbose_name='Max Riders'),
        ),
    ]