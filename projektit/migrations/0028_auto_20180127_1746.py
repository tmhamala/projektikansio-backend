# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-27 17:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0027_auto_20180127_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registereduser',
            name='password_reset_token_valid_until',
            field=models.DateTimeField(default=datetime.datetime(1800, 1, 1, 0, 0)),
        ),
    ]
