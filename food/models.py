from django.db import models

# Create your models here.


class Food(models.Model):
    name = models.CharField(max_length=255)
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    contains_nuts = models.BooleanField()
    contains_gluten = models.BooleanField()
    contains_dairy = models.BooleanField()

    def __str__(self):
        return self.name