#coding: utf-8
from datetime import datetime
from django.utils import timezone

from rates.models import Measure


class Processor(object):
    rate = ""
    description = ""
    interval = ""
    start_date = ""

    def get_measure(self, date):
        raise NotImplemented()

    def save(self):
        value = self.get_measure()
        measure = Measure()
        measure.measure = value
        measure.rate = self.rate
        measure.measure_date = datetime.now()

    def get_last_running_date(self):
        date = None
        try:
            measure = Measure.objects.filter(rate=self.rate).order_by('-measure_date')[0]
            date = measure.measure_date
        except IndexError:
            date = self.start_date
        return date

    def execute(self):
        last_running_date = self.get_last_running_date()
        next_running_date = last_running_date + self.interval
        now = timezone.now()
        while next_running_date < now:
            self.save(next_running_date)
            next_running_date += self.interval