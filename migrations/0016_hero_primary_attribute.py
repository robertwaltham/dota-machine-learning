# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0015_auto_20150608_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='primary_attribute',
            field=models.IntegerField(default=0, choices=[(0, b'STR'), (1, b'AGI'), (2, b'INT')]),
            preserve_default=True,
        ),
    ]
