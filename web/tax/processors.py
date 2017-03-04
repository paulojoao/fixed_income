#coding: utf-8
from datetime import datetime
from django.utils import timezone

from tax.models import Measure


class Processor(object):
    tax = ""
    description = ""
    interval = ""
    start_date = ""

    def get_measure(self):
        raise NotImplemented()

    def running_time(self):
        last_measure = Measure.objects.filter(tax=self.tax).order_by('measure_date')[0]
        now = timezone.now()
        next_run = last_measure.measure_date + self.interval
        return now > next_run

    def save(self):
        value = self.get_measure()
        measure = Measure()
        measure.measure = value
        measure.tax = self.tax
        measure.measure_date = datetime.now()

    def execute(self):
        if self.running_time:
            self.save()