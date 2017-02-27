from django.db import models


class Measure(models.Model):
    measure = models.FloatField()
    measure_date = models.DateTimeField()
    tax = models.CharField(max_length=20)

