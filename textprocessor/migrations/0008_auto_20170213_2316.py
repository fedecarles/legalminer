# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textprocessor', '0007_auto_20170211_0034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fallos',
            name='nr',
        ),
        migrations.AlterField(
            model_name='mynotes',
            name='note_id',
            field=models.CharField(default='b9e581ad-6', max_length=11, unique=True),
        ),
    ]
