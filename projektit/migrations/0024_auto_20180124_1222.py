# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-24 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0023_auto_20180122_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationproject',
            name='time_limit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activationproject',
            name='time_limit_days',
            field=models.IntegerField(default=30, null=True),
        ),
    ]