# Generated by Django 4.1.3 on 2022-12-05 04:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groupridesapp', '0022_alter_clubmembership_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clubmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
