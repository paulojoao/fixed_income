#coding: utf-8
from datetime import datetime
import json

from django.http import HttpResponse
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
        else:
            value = queryset[0].measure

        return HttpResponse(value)
    except IndexError:
        return HttpResponse('')
