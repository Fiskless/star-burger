from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, F, DecimalField
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон',
                                     max_length=50, blank=True)

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 verbose_name='категория',
                                 related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2,
                                validators=[MinValueValidator(0)])
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False,
                                         db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE,
                                   related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True,
                                       db_index=True)

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQueryset(models.QuerySet):

    def order_price(self):
        total_price = self.annotate(
            total_price=Sum(F('products__price') * F('products__quantity'),
            output_field=DecimalField())
        )
        return total_price


class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ("Необработанный", "необработанный"),
        ("Обработанный", "обработанный")
    ]

    PAYMENT_METHOD_CHOICES = [
        ("Наличностью", "наличностью"),
        ("Электронно", "электронно")
    ]

    order_status = models.CharField("Статус заказа", max_length=20,
                                    choices=ORDER_STATUS_CHOICES,
                                    default="необработанный",
                                    db_index=True)
    payment_method = models.CharField("Способ оплаты", max_length=20,
                                      choices=PAYMENT_METHOD_CHOICES,
                                      blank=True,
                                      db_index=True)
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Телефон')
    address = models.CharField('Адрес', max_length=100)
    comment = models.TextField('Комментарий к заказу',
                               max_length=200,
                               blank=True)
    registrated_at = models.DateTimeField("Время создания заказа",
                                          default=timezone.now,
                                          db_index=True)
    called_at = models.DateTimeField("Время звонка", blank=True, null=True,
                                     db_index=True)
    delivered_at = models.DateTimeField("Время доставки",
                                        blank=True, null=True,
                                        db_index=True)
    restaurant = models.ForeignKey(Restaurant,
                                   on_delete=models.CASCADE,
                                   related_name='orders',
                                   verbose_name="Ресторан",
                                   null=True,
                                   blank=True)

    objects = OrderQueryset.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return (f"{self.firstname} {self.lastname}, {self.address}")


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='order_items',
                                verbose_name="товар")
    quantity = models.IntegerField('количество',
                                   validators=[MinValueValidator(0)])
    price = models.DecimalField('цена', max_digits=8, decimal_places=2,
                                validators=[MinValueValidator(0)])
    order = models.ForeignKey(Order, verbose_name='заказ',
                              on_delete=models.CASCADE,
                              related_name='products')

    class Meta:
        verbose_name = 'заказанный товар'
        verbose_name_plural = 'заказанные товары'

    def __str__(self):
        return self.product.name


