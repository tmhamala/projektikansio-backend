# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0003_auto_20171029_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='registereduser',
            name='avatar_base64',
            field=models.CharField(max_length=5000, null=True),
        ),
    ]