# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-08-01 18:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0042_auto_20190722_2158'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Activationproject',
            new_name='Project',
        ),
    ]
