# Generated by Django 2.1.2 on 2019-01-16 22:07
import django.contrib.postgres.fields.jsonb
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Msg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255, verbose_name='Type')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'NEW'), (2, 'PENDING'), (3, 'DONE'), (4, 'ERROR')], default=1, verbose_name='Status')),
                ('language', models.CharField(max_length=32, verbose_name='Language')),
                ('recipients', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Recipients')),
                ('context', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='Context')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
        ),
    ]
