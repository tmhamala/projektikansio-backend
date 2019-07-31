# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-25 23:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0035_auto_20190424_2239'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectfollow',
            name='project',
        ),
        migrations.RemoveField(
            model_name='projectfollow',
            name='user',
        ),
        migrations.AddField(
            model_name='registereduser',
            name='notifications_read',
            field=models.DateTimeField(default=datetime.datetime(1800, 1, 1, 0, 0)),
        ),
        migrations.DeleteModel(
            name='ProjectFollow',
        ),
    ]