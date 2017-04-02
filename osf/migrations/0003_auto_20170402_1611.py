# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-02 21:11
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0002_add_lower_index_to_tags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelManagers(
            name='fileversion',
            managers=[
                ('includable_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='abstractnode',
            name='public_comments',
        ),
        migrations.RemoveField(
            model_name='osfuser',
            name='piwik_token',
        ),
    ]