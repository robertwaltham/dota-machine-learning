# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hero',
            fields=[
                ('name', models.CharField(max_length=255)),
                ('hero_id', models.IntegerField(default=0, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('name', models.CharField(max_length=255)),
                ('item_id', models.IntegerField(default=0, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('match_id', models.IntegerField(default=0, serialize=False, primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('match_seq_num', models.IntegerField()),
                ('has_been_processed', models.BooleanField(default=False)),
                ('radiant_win', models.BooleanField(default=False)),
                ('duration', models.IntegerField(default=0)),
                ('tower_status_radiant', models.SmallIntegerField(default=0)),
                ('tower_status_dire', models.SmallIntegerField(default=0)),
                ('barracks_status_radiant', models.SmallIntegerField(default=0)),
                ('barracks_status_dire', models.SmallIntegerField(default=0)),
                ('cluster', models.IntegerField(default=0)),
                ('first_blood_time', models.SmallIntegerField(default=0)),
                ('lobby_type', models.SmallIntegerField(default=0)),
                ('human_players', models.SmallIntegerField(default=0)),
                ('league_id', models.SmallIntegerField(default=0)),
                ('game_mode', models.SmallIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('name', models.CharField(max_length=255)),
                ('account_id', models.IntegerField(default=0, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlayerInMatch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player_slot', models.SmallIntegerField()),
                ('kills', models.SmallIntegerField()),
                ('deaths', models.SmallIntegerField()),
                ('assists', models.SmallIntegerField()),
                ('leaver_status', models.SmallIntegerField()),
                ('gold', models.SmallIntegerField()),
                ('last_hits', models.SmallIntegerField()),
                ('denies', models.SmallIntegerField()),
                ('gold_per_min', models.SmallIntegerField()),
                ('xp_per_min', models.SmallIntegerField()),
                ('gold_spent', models.SmallIntegerField()),
                ('hero_damage', models.SmallIntegerField()),
                ('tower_damage', models.SmallIntegerField()),
                ('hero_healing', models.SmallIntegerField()),
                ('level', models.SmallIntegerField()),
                ('hero', models.ForeignKey(to='DotaStats.Hero')),
                ('item_0', models.ForeignKey(related_name='item_0', to='DotaStats.Item')),
                ('item_1', models.ForeignKey(related_name='item_1', to='DotaStats.Item')),
                ('item_2', models.ForeignKey(related_name='item_2', to='DotaStats.Item')),
                ('item_3', models.ForeignKey(related_name='item_3', to='DotaStats.Item')),
                ('item_4', models.ForeignKey(related_name='item_4', to='DotaStats.Item')),
                ('item_5', models.ForeignKey(related_name='item_5', to='DotaStats.Item')),
                ('match', models.ForeignKey(to='DotaStats.Match')),
                ('player', models.ForeignKey(to='DotaStats.Player')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
