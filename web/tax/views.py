#coding: utf-8
from django.http import HttpResponse

from tax.models import Measure
# Create your views here.

def get_rate(request):
    try:
        rate = request.GET['rate']

        measure = Measure.objects.filter(tax = rate).order_by('-measure_date')[0]
        return HttpResponse(measure.measure)
    except IndexError:
        return HttpResponse('')
        
    
    