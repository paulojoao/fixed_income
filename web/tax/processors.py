#coding: utf-8
from datetime import datetime

from tax.models import Measure

class Processor(object):
    name = ""
    description = ""
    frequency = ""
    start_date = ""

    def get_measure(self):
        raise NotImplemented()

    def running_time(sef):
        pass

    def save(self):
        value = self.get_measure()
        measure = Measure()
        measure.measure = value
        measure.tax = name
        measure.measure_date = datetime.now()

    


