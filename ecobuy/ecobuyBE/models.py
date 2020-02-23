from django.db import models
from schedule.models import Object

class EcoUser(models.Model):
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=200)
    ecobuy_rate = models.FloatField('rate')
    number_of_products = models.IntegerField()
    
    objects = models.Manager()
    
    def __str__(self):
        return f"{self.email}: ({self.ecobuy_rate}, {self.number_of_products})"
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(EcoUser, on_delete=models.CASCADE)
    ecobuy_rate = models.FloatField('rate')
    country = models.CharField(max_length=200)
    dimensions = models.CharField(max_length=200)
    weight = models.CharField(max_length=200)
    material = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    
    objects = models.Manager()
    
    
    def __str__(self):
        return f"{self.name}: {self.user} ({self.ecobuy_rate}, {self.country})"