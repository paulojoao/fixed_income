#coding: utf-8
from datetime import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render
import django.db.models

from rates.models import Measure
# Create your views here.


def get_rate(request):
    date_pattern = "%d-%m-%Y"
    try:
        raw_filters = request.GET.get('filters', None)
        function = request.GET.get('function')
        filters = json.loads(raw_filters.replace("'", '"'))
        for key in filters.keys():
            if 'date' in key:
                raw_value = filters[key]
                filters[key] = datetime.strptime(raw_value, date_pattern)
        queryset = Measure.objects.filter(**filters)
        if(function):
            aggregate = getattr(django.db.models, function)('measure')
            value = queryset.aggregate(aggregate)
            key = "measure__" + function.lower()
            value = value.get(key,None)
            return HttpResponse(value)
        else:
            values = ",".join([str(x.measure) for x in queryset])
            return HttpResponse(values)
    except IndexError:
        return HttpResponse('')

def get_home(request):
    return render(request, 'index.html')