# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djcelery.picklefield


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0011_auto_20150406_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='data',
            field=djcelery.picklefield.PickledObjectField(default=None, null=True, editable=False),
            preserve_default=True,
        ),
    ]
