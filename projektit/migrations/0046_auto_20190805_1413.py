# Generated by Django 2.2.4 on 2019-08-05 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projektit', '0045_auto_20190801_2104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='like_count',
        ),
        migrations.AlterField(
            model_name='project',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='projektit.Registereduser'),
        ),
    ]