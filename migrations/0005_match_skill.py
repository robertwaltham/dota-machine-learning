# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0004_auto_20150406_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='skill',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
