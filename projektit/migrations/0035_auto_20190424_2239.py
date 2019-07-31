# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-04-24 22:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0034_auto_20190424_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectlike',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_likers', to='projektit.Activationproject'),
        ),
        migrations.AlterField(
            model_name='steplike',
            name='step',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='step_likes', to='projektit.Step'),
        ),
    ]