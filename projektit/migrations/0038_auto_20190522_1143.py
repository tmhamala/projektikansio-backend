# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-22 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0037_activationproject_certificated_root_project_cover_photo_s3_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='registereduser',
            name='avatar_s3_key',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='avatar_s3_url',
            field=models.CharField(max_length=200, null=True),
        ),
    ]