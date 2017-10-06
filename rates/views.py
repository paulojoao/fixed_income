#coding: utf-8
from datetime import datetime
import json
from django.http import HttpResponse

from rates.models import Measure
# Create your views here.


def get_rate(request):
    date_pattern = "%d-%m-%Y"
    try:
        import ipdb;ipdb.set_trace()
        # filters = {}
        raw_filters = request.GET.get('filters', None)
        filters = json.loads(raw_filters.replace("'", '"'))
        for key in filters.keys():
            if 'date' in key:
                raw_value = filters[key]
                filters[key] = datetime.strptime(raw_value, date_pattern)
        print(filters)
        measure = Measure.objects.filter(**filters)[0]
        return HttpResponse(measure.measure)
    except IndexError:
        return HttpResponse('')
