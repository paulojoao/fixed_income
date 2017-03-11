#coding: utf-8
from django.http import HttpResponse

from rates.models import Measure
# Create your views here.


def get_rate(request):
    try:
        rate = request.GET.get('rate', None)
        date = request.GET.get('date', None)

        filters = {}
        if rate:
            filters['rate'] = rate
        if date:
            filters['measure_date'] = '2017-02-28'

        measure = Measure.objects.filter(**filters).order_by('-measure_date')[0]
        return HttpResponse(measure.measure)
    except IndexError:
        return HttpResponse('')
