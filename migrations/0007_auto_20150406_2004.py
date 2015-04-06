# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djcelery.picklefield


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0006_auto_20150406_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='scikitmodel',
            name='is_ready',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='scikitmodel',
            name='task_id',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scikitmodel',
            name='picked_model',
            field=djcelery.picklefield.PickledObjectField(default=None, null=True, editable=False),
            preserve_default=True,
        ),
    ]
