# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-25 23:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0024_auto_20180124_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activationproject',
            name='numeric_percentage',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='activationproject',
            name='numeric_total',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='activationproject',
            name='step_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='activationproject',
            name='step_percentage',
            field=models.FloatField(default=0, null=True),
        ),
    ]
