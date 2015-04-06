# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='account_id',
            field=models.BigIntegerField(default=0, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
