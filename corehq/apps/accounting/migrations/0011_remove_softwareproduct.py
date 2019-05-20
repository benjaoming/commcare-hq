# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-24 02:10
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations, models




def _copy_product_name_to_product_rate_name(apps, schema_editor):
    SoftwareProductRate = apps.get_model('accounting', 'SoftwareProductRate')
    for product_rate in SoftwareProductRate.objects.all():
        product_rate.name = product_rate.product.name
        product_rate.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0010_remove_softwareproduct_product_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='softwareproductrate',
            name='name',
            field=models.CharField(default='temp', max_length=40),
            preserve_default=False,
        ),
        migrations.RunPython(_copy_product_name_to_product_rate_name),
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),
        migrations.RemoveField(
            model_name='softwareproductrate',
            name='product',
        ),
        migrations.DeleteModel(
            name='SoftwareProduct',
        ),
    ]
