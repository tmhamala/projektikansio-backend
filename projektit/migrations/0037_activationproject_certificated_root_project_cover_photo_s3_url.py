# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-21 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0036_auto_20190425_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationproject',
            name='certificated_root_project_cover_photo_s3_url',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
