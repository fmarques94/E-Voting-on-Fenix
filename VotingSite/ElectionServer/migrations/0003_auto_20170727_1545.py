# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-27 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ElectionServer', '0002_voter_proofrandomvalues'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ballot',
            name='election',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ElectionServer.Election'),
        ),
    ]