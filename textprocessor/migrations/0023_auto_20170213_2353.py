# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 23:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('textprocessor', '0022_auto_20170213_2351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mynotes',
            name='user',
        ),
        migrations.DeleteModel(
            name='MyNotes',
        ),
    ]
