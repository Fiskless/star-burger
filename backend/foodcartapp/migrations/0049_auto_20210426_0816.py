# Generated by Django 3.0.7 on 2021-04-26 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20210426_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='address',
            field=models.CharField(blank=True, max_length=100, unique=True, verbose_name='адрес'),
        ),
    ]