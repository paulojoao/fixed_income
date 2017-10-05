#coding: utf-8
from urllib import request
from datetime import timedelta
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

    def save(self, date):
        value = self.get_measure(date)
        measure = Measure()
        measure.measure = value
        measure.rate = self.rate
        measure.measure_date = datetime.now()
        measure.save()

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
                try:
                    self.save(next_running_date)
                    next_running_date += self.interval
                    print('.')
                except Exception:
                    next_running_date += self.interval
                    print('F')

class CDIProcessor(Processor):
    rate = "CDI"
    description = "TODO"
    interval = timedelta(days=1)
    start_date = datetime(2012, 8, 20)

    def get_measure(self, date):
        url = self.get_url(date)
        print(url)
        data = request.urlopen(url).read()
        value = self.parse_value(data)
        return value

    def get_url(self, date):
        st = 'ftp://ftp.cetip.com.br/MediaCDI/'+date.strftime('%Y%m%d') + '.txt'
        return st
    
    def parse_value(self, raw):
        r = raw.strip()
        return float(r) / 100
