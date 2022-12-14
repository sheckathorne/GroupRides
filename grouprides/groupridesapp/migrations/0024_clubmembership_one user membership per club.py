# Generated by Django 4.1.3 on 2022-12-06 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupridesapp', '0023_alter_clubmembership_user'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='clubmembership',
            constraint=models.UniqueConstraint(fields=('user', 'club'), name='One user membership per club'),
        ),
    ]
