# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-28 23:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0028_auto_20180127_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registereduser',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
