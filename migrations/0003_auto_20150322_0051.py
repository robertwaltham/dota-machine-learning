# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0002_auto_20150322_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='barracks_status_dire',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='barracks_status_radiant',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='cluster',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='duration',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='first_blood_time',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='game_mode',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='human_players',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='league_id',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='lobby_type',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='tower_status_dire',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='match',
            name='tower_status_radiant',
            field=models.SmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
