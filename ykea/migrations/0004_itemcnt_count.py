# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-09 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ykea', '0003_auto_20180426_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcnt',
            name='count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]