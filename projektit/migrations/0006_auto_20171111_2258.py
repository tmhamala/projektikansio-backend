# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 22:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0005_auto_20171111_2255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registereduser',
            name='avatar_base64',
            field=models.CharField(max_length=100000, null=True),
        ),
    ]