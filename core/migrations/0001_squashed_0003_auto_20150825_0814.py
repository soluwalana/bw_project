# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'core', '0001_initial'), (b'core', '0002_auto_20150824_0113'), (b'core', '0003_auto_20150825_0814')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1024)),
                ('cur_price', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expires', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bid_amount', models.PositiveIntegerField()),
                ('bid_time', models.DateTimeField(auto_now_add=True)),
                ('auction', models.ForeignKey(to='core.Auction')),
                ('bidder', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='auction',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='auction',
            name='list_price',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='auction',
            unique_together=set([('owner', 'item_name')]),
        ),
    ]
