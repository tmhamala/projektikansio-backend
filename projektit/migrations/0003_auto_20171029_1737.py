# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-29 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0002_registereduser'),
    ]

    operations = [
        migrations.AddField(
            model_name='registereduser',
            name='email',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='info',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]