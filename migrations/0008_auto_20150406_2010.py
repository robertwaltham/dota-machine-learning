# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0007_auto_20150406_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scikitmodel',
            name='algorithm',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scikitmodel',
            name='match_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scikitmodel',
            name='max_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scikitmodel',
            name='min_date',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
