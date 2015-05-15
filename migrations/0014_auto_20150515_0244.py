# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0013_auto_20150510_2316'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='playerinmatch',
            unique_together=set([('match', 'player_slot')]),
        ),
    ]
