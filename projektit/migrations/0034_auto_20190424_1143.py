# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-24 11:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0033_auto_20190224_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_comments', to='projektit.Activationproject'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='step',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='step_comments', to='projektit.Step'),
        ),
    ]
