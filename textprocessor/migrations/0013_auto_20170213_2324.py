# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 23:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('textprocessor', '0012_auto_20170213_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='fallos',
            name='likes',
            field=models.ManyToManyField(related_name='likes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mynotes',
            name='note_id',
            field=models.CharField(default='1a38dfaf-6', max_length=11, unique=True),
        ),
    ]