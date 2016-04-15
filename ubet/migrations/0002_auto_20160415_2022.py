# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-15 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ubet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group_link',
            name='position',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='group_link',
            unique_together=set([('user', 'group', 'position')]),
        ),
    ]