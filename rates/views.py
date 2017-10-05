#coding: utf-8
from datetime import datetime

from django.http import HttpResponse

from rates.models import Measure
# Create your views here.


def get_rate(request):
    date_pattern = "%d/%m/%Y"
    try:
        rate = request.GET.get('rate', None)
        date_str = request.GET.get('date', None)

        filters = {}
        if rate:
            filters['rate'] = rate
        if date_str:
            date = datetime.strptime(date_str, date_pattern)
            filters['measure_date'] = date

        measure = Measure.objects.filter(**filters).order_by('-measure_date')[0]
        return HttpResponse(measure.measure)
    except IndexError:
        return HttpResponse('')
