# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-07-09 14:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0039_auto_20190709_1316'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activationproject',
            old_name='challenge_category',
            new_name='category',
        ),
    ]
