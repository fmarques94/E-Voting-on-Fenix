# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 20:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ElectionServer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trustee',
            name='decryptionProofRandom',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='trustee',
            name='keyShareProofRandom',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='trustee',
            name='publicKeyShare',
            field=models.TextField(null=True),
        ),
    ]
