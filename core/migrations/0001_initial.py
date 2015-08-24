# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

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
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=1024)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='bid',
            name='bidder',
            field=models.ForeignKey(to='core.User'),
        ),
        migrations.AddField(
            model_name='auction',
            name='owner',
            field=models.ForeignKey(to='core.User'),
        ),
    ]
