# Generated by Django 4.1.3 on 2022-12-24 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0031_alter_event_weekdays'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='weekdays',
            field=models.CharField(blank=True, choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], max_length=8, null=True),
        ),
    ]