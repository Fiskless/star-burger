# Generated by Django 3.0.7 on 2021-02-27 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_order_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(default='', max_length=200, verbose_name='Комментарий к заказу'),
        ),
    ]