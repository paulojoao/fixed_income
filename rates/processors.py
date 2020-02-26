#coding: utf-8
import json
from enum import Enum
from urllib import request
from datetime import timedelta
from datetime import datetime

from django.utils import timezone

from rates.models import Measure


class Frequency(Enum):
    DAILY = 1
    MONTHLY = 1
    ANNUAL = 1


class Processor(object):
    rate = ""
    description = ""
    interval = timedelta(days=1)
    start_date = ""
    frequency = Frequency.DAILY

    def get_measure(self, date):
        raise NotImplemented

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

    def check_running(self, last_running_date):
        if (self.frequency == Frequency.DAILY):
            return last_running_date.date() == datetime.now().date()
        elif (self.frequency == Frequency.ANNUAL):
            return last_running_date.year() == datetime.now().year()
        elif (self.frequency == Frequency.MONTHLY and last_running_date.strftime('%m-%y') == datetime.now().strftime('%m-%y')):
            return True 
        else:
            return False

    def execute(self):
            last_running_date = self.get_last_running_date()
            
            next_running_date = last_running_date + self.interval
            now = timezone.now()
            pattern = "%d/%m/%y %H:%M"
            already_running = self.check_running(last_running_date)
            while not already_running:
                try:
                    import ipdb;ipdb.set_trace()
                    self.save(next_running_date)
                    next_running_date += self.interval
                    print('.')
                except Exception as err:
                    next_running_date += self.interval
                    print('F {}'.format(err))
                already_running = self.check_running(next_running_date)


class IPCAProcessor(Processor):
    rate = "IPCA"
    description = "Indice geral de preços ao consumidor"
    frequency = Frequency.MONTHLY
    start_date = datetime(2019, 1, 1)

    def get_url(self, date):
        url = "http://api.sidra.ibge.gov.br/values/t/1737/p/%s/v/63/n1/1" % (date.strftime('%Y%m'))
        return url

    def get_measure(self, date):
        url = self.get_url(date)
        data = request.urlopen(url).read()
        value = self.parse_value(data)
        return value

    def parse_value(self, data):
        parsed_data = json.loads(data)
        if (len(parsed_data) > 1):
            str_value = parsed_data[1].get("V")
            return float(str_value)
        else:
            return None


class CDIProcessor(Processor):
    rate = "CDI"
    description = "TODO"
    start_date = datetime(2012, 8, 20)
    frequency = Frequency.DAILY

    def get_measure(self, date):
        url = self.get_url(date)
        data = request.urlopen(url).read()
        value = self.parse_value(data)
        return value

    def get_url(self, date):
        st = 'ftp://ftp.cetip.com.br/MediaCDI/'+date.strftime('%Y%m%d') + '.txt'
        return st
    
    def parse_value(self, raw):
        r = raw.strip()
        return float(r) / 100
