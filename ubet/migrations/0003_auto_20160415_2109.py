# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 18:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ubet', '0002_auto_20160415_2022'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='group_link',
            unique_together=set([('group', 'position')]),
        ),
    ]
