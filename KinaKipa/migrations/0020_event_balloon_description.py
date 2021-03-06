# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-07 17:45
from __future__ import unicode_literals

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('KinaKipa', '0019_auto_20180207_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='balloon_description',
            field=tinymce.models.HTMLField(default='', help_text='Short description for balloon on the map', verbose_name='Balloon description'),
            preserve_default=False,
        ),
    ]
