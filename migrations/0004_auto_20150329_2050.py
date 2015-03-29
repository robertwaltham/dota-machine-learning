# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0003_auto_20150322_0051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='id',
        ),
        migrations.AddField(
            model_name='player',
            name='account_id',
            field=models.IntegerField(default=0, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
