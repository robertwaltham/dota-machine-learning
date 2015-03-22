# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='id',
        ),
        migrations.AddField(
            model_name='match',
            name='match_id',
            field=models.IntegerField(default=0, serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='has_been_processed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='radiant_win',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
