# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0004_auto_20150329_2050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hero',
            name='id',
        ),
        migrations.RemoveField(
            model_name='item',
            name='id',
        ),
        migrations.AddField(
            model_name='hero',
            name='hero_id',
            field=models.IntegerField(default=0, serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='item_id',
            field=models.IntegerField(default=0, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
