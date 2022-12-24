# Generated by Django 4.1.3 on 2022-12-24 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0028_days_event_weekdays'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='weekdays',
        ),
        migrations.DeleteModel(
            name='Days',
        ),
        migrations.AddField(
            model_name='event',
            name='weekdays',
            field=models.CharField(choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], default=1, max_length=8),
            preserve_default=False,
        ),
    ]
