# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0005_match_skill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerinmatch',
            name='gold_spent',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
