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
    MONTHLY = 2
    ANNUAL = 3


class Processor(object):
    rate = ""
    description = ""
    interval = timedelta(days=1)
    start_date = ""
    frequency = Frequency.DAILY

    def __init__(self):
        print("Iniciando processor para a taxa: %s \t frequência %s" %(self.rate, self.frequency))

    def get_measure(self, date):
        raise NotImplemented

    def get_measure_date(self, date):
        raise NotImplemented

    def save(self, date):
        if (not self.already_running(date)):
            print("Buscando dados do %s no dia %s" %(self.rate, date.strftime("%d-%m-%y")))
            value = self.get_measure(date)
            measure = Measure()
            measure.measure = value
            measure.rate = self.rate
            measure.measure_date = self.get_measure_date(date)
            measure.save()
        else:
            print("já foi executada a busca do %s no dia %s" %(self.rate, date.strftime("%d-%m-%y")))

    def already_running(self, last_running_date):
        print('Taxa: \t %s \t Frequencia: %s.\t última execução: %s' %(self.rate, self.frequency, last_running_date))
        if (self.frequency == Frequency.DAILY):
            return last_running_date.date() == datetime.now().date()
        elif (self.frequency == Frequency.ANNUAL):
            return last_running_date.year() == datetime.now().year()
        elif (self.frequency == Frequency.MONTHLY):
            return last_running_date.strftime('%m-%y') == datetime.now().strftime('%m-%y')
        else:
            return False

    def get_date(self, date):
        if self.frequency == Frequency.DAILY:
            return date 
        elif self.frequency == Frequency.MONTHLY:
            return date


    def get_last_running_date(self):
        print("Buscando data de ultima leitura do %s" %(self.rate))
        date = None
        try:
            measure = Measure.objects.filter(rate=self.rate).order_by('-measure_date')[0]
            date = measure.measure_date
        except IndexError:
            date = self.start_date
        print("Data de última leitura: %s" %(date.strftime("%d-%m-%y")))
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
                except Exception as err:
                    next_running_date += self.interval
                    print('F {}'.format(err))


class IPCAProcessor(Processor):
    rate = "IPCA"
    description = "Indice geral de preços ao consumidor"
    frequency = Frequency.MONTHLY
    start_date = datetime(2001, 1, 1)

    def get_url(self, date):
        date.replace(day=1)
        date = date - datetime.timedelta(days=1)

        url = "http://api.sidra.ibge.gov.br/values/t/1737/p/%s%s/v/63/n1/1" % (date.year(), date.month())
        return url

    def get_measure_date(self, date):
        date.replace(day=1)
        date = date - datetime.timedelta(days=1)
        return date

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

    def get_measure_date(self, date):
        return date

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
