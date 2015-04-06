# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0009_auto_20150406_2028'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='heroinprediction',
            name='hero',
        ),
        migrations.RemoveField(
            model_name='heroinprediction',
            name='match_prediction',
        ),
        migrations.DeleteModel(
            name='HeroInPrediction',
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='dire_player_0',
            field=models.ForeignKey(related_name='dire_player_0', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='dire_player_1',
            field=models.ForeignKey(related_name='dire_player_1', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='dire_player_2',
            field=models.ForeignKey(related_name='dire_player_2', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='dire_player_3',
            field=models.ForeignKey(related_name='dire_player_3', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='dire_player_4',
            field=models.ForeignKey(related_name='dire_player_4', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='dire_player_5',
            field=models.ForeignKey(related_name='dire_player_5', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='radiant_player_0',
            field=models.ForeignKey(related_name='radiant_player_0', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='radiant_player_1',
            field=models.ForeignKey(related_name='radiant_player_1', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='radiant_player_2',
            field=models.ForeignKey(related_name='radiant_player_2', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='radiant_player_3',
            field=models.ForeignKey(related_name='radiant_player_3', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='radiant_player_4',
            field=models.ForeignKey(related_name='radiant_player_4', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchprediction',
            name='radiant_player_5',
            field=models.ForeignKey(related_name='radiant_player_5', to='DotaStats.Hero', null=True),
            preserve_default=True,
        ),
    ]
