# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-09 22:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textprocessor', '0006_favorites'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favorites',
            name='fav',
        ),
        migrations.AddField(
            model_name='favorites',
            name='fav_autos',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='favorites',
            name='fav_url',
            field=models.TextField(blank=True, null=True),
        ),
    ]
