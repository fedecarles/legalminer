# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-11 00:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textprocessor', '0006_auto_20170211_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mynotes',
            name='note_id',
            field=models.CharField(default='ed7b69bd-e', max_length=11, unique=True),
        ),
    ]
