#coding: utf-8
from datetime import datetime

import factory
from rates.models import Measure


class MeasureFactory(factory.Factory):
    measure = 16.20
    measure_date = datetime.now()
    rate = 'CDI'

    class Meta:
        model = Measure

      