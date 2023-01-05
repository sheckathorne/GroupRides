# Generated by Django 4.1.3 on 2022-12-24 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0027_alter_clubmembershiprequest_responder_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Days',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='weekdays',
            field=models.ManyToManyField(to='groupridesapp.days'),
        ),
    ]