# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0003_scikitmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerinmatch',
            name='hero_damage',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
