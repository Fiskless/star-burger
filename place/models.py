from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.CharField('адрес', max_length=100, unique=True)
    lat = models.FloatField('Ширина', max_length=20)
    lon = models.FloatField('Долгота', max_length=20)
    time = models.DateTimeField("Дата запроса к геокодеру",
                                default=timezone.now,
                                db_index=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'место'
        verbose_name_plural = 'места'
