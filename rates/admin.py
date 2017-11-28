from django.contrib import admin
from .models import Measure



class MeasureAdmin(admin.ModelAdmin):
    list_display = ('measure_date', 'rate', 'measure', )

admin.site.register(Measure, MeasureAdmin)
# Register your models here.
