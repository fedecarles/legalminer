# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 23:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('textprocessor', '0015_auto_20170213_2330'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyNotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_id', models.CharField(default='44c26790-b', max_length=11, unique=True)),
                ('autos', models.TextField(blank=True, null=True)),
                ('text', models.TextField(blank=True, max_length=9999999, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
