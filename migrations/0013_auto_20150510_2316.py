# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DotaStats', '0012_match_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='localized_name',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='cost',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='localized_name',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='recipe',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='secret_shop',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='side_shop',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
