# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-05 21:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0014_auto_20171204_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationproject',
            name='numeric_total',
            field=models.FloatField(null=True),
        ),
    ]
