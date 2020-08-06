# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-19 01:58
from __future__ import unicode_literals

from corehq.sql_db.operations import RawSQLMigration
from django.db import migrations, models

from custom.icds_reports.const import SQL_TEMPLATES_ROOT

migrator = RawSQLMigration((SQL_TEMPLATES_ROOT, 'database_views'))


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0170_auto_20200210_1142'),
    ]
    operations = [
        migrations.AddField(
            model_name='aggservicedeliveryreport',
            name='children_0_3',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='aggservicedeliveryreport',
            name='children_3_5',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='aggservicedeliveryreport',
            name='gm_0_3',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='aggservicedeliveryreport',
            name='gm_3_5',
            field=models.IntegerField(null=True),
        )
    ]
