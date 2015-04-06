# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0002_auto_20150406_0007'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScikitModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('picked_model', models.TextField()),
                ('algorithm', models.CharField(max_length=255)),
                ('min_date', models.DateTimeField()),
                ('max_date', models.DateTimeField()),
                ('match_count', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
