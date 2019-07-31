# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-15 19:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0021_auto_20180107_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=50, null=True)),
                ('action_maker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_maker', to='projektit.Registereduser')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projektit.Activationproject')),
            ],
        ),
        migrations.AlterField(
            model_name='step',
            name='description',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='step',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='projektit.Step'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projektit.Registereduser'),
        ),
    ]