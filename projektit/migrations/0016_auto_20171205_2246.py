# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-05 22:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0015_activationproject_numeric_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationproject',
            name='numeric_percentage',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='activationproject',
            name='step_percentage',
            field=models.FloatField(null=True),
        ),
    ]