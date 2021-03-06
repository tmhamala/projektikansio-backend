# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-22 12:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0011_registereduser_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registereduser',
            name='avatar_base64',
        ),
        migrations.AddField(
            model_name='activationproject',
            name='numeric_goal',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='activationproject',
            name='step_goal',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='step',
            name='rating',
            field=models.FloatField(null=True),
        ),
    ]
