# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0014_auto_20150515_0244'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='valid_for_model',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='playerinmatch',
            name='hero',
            field=models.ForeignKey(related_name='heroinmatch', to='DotaStats.Hero'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='playerinmatch',
            name='match',
            field=models.ForeignKey(related_name='playerinmatch', to='DotaStats.Match'),
            preserve_default=True,
        ),
    ]
