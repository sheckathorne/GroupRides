# Generated by Django 4.1.3 on 2022-11-28 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0013_alter_eventoccurencemessage_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='logo_url',
            field=models.CharField(max_length=500, verbose_name='Logo URL'),
        ),
        migrations.AlterField(
            model_name='clubmembership',
            name='membership_type',
            field=models.IntegerField(choices=[(1, 'Creator'), (2, 'Admin'), (3, 'Ride Leader'), (4, 'Member'), (5, 'Non-Member')], verbose_name='Membership Type'),
        ),
        migrations.AlterField(
            model_name='event',
            name='privacy',
            field=models.IntegerField(choices=[(4, 'Current Members'), (5, 'Open')], verbose_name='Privacy'),
        ),
        migrations.AlterField(
            model_name='eventoccurence',
            name='privacy',
            field=models.IntegerField(choices=[(4, 'Current Members'), (5, 'Open')], verbose_name='Privacy'),
        ),
    ]
