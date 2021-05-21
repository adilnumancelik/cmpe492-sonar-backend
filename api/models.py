# Create your models here.
from django.db import models

class Dummy(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')
    value = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['name']