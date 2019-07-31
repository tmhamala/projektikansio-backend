# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-02 22:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0012_auto_20171122_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationproject',
            name='goal',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='activationproject',
            name='step_count',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='step',
            name='numeric_value',
            field=models.FloatField(null=True),
        ),
    ]