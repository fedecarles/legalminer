# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 23:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textprocessor', '0008_auto_20170213_2316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fallos',
            name='likes',
        ),
        migrations.AlterField(
            model_name='mynotes',
            name='note_id',
            field=models.CharField(default='2c32b0fb-1', max_length=11, unique=True),
        ),
    ]
