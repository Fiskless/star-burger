# Generated by Django 3.0.7 on 2021-02-27 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_orderproduct_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Необработанный', 'необработанный'), ('Обработанный', 'обработанный')], default='необработанный', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
