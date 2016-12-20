# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-17 22:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fallos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nr', models.IntegerField(default=0)),
                ('corte', models.CharField(blank=True, max_length=255, null=True)),
                ('exp', models.CharField(blank=True, max_length=100, null=True)),
                ('autos', models.TextField(blank=True, null=True)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('sobre', models.CharField(blank=True, max_length=255, null=True)),
                ('text', models.TextField(blank=True, max_length=999999, null=True)),
                ('actora', models.CharField(blank=True, max_length=255, null=True)),
                ('demandada', models.CharField(blank=True, max_length=255, null=True)),
                ('jueces', models.CharField(blank=True, max_length=255, null=True)),
                ('leyes', models.CharField(blank=True, max_length=255, null=True)),
                ('citados', models.TextField(blank=True, null=True)),
                ('lugar', models.CharField(blank=True, max_length=150, null=True)),
                ('provincia', models.CharField(blank=True, max_length=150, null=True)),
                ('voces', models.TextField(blank=True, null=True)),
                ('materia', models.TextField(blank=True, null=True)),
                ('slug', models.SlugField(editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
