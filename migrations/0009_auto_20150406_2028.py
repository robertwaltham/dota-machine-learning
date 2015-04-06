# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0008_auto_20150406_2010'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroInPrediction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('player_on_radiant', models.BooleanField(default=True)),
                ('hero', models.ForeignKey(to='DotaStats.Hero')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MatchPrediction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('predicted_radiant_win', models.NullBooleanField()),
                ('model', models.ForeignKey(to='DotaStats.ScikitModel')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='heroinprediction',
            name='match_prediction',
            field=models.ForeignKey(to='DotaStats.MatchPrediction'),
            preserve_default=True,
        ),
    ]
