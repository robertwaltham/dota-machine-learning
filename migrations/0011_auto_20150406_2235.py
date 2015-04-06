# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0010_auto_20150406_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchprediction',
            name='predicted_radiant_win',
            field=models.NullBooleanField(default=None),
            preserve_default=True,
        ),
    ]
