#coding: utf-8
from unittest import mock
from datetime import datetime, timedelta
from urllib.request import urlopen

import freezegun
from django.test import TestCase
from django.test import Client

from rates.factories import MeasureFactory
from rates.models import Measure
from rates.processors import Processor, CDIProcessor, IPCAProcessor
from rates.management.commands.import_rates import Command


class ProcessorTestCase(TestCase):
    @mock.patch('rates.processors.Processor.get_measure')
    def test_save(self, mk_get_value):
        mk_get_value.return_value = 10.0
        old_count = Measure.objects.count()
        processor = Processor()
        processor.save(None)
        new_count = Measure.objects.count()
        self.assertEquals(old_count+1, new_count)
    
    def test_get_last_running_date(self):
        measure1 = MeasureFactory.create(measure_date=datetime(2017,3,4,17,00,00), rate="CDI")
        measure1.save()

        measure2 = MeasureFactory.create(measure_date=datetime(2017,2,28,17,00,00), rate="IPCA")
        measure2.save()

        measure3 = MeasureFactory.create(measure_date=datetime(2017,2,27,17,00,00), rate="IPCA")
        measure3.save()

        processor = Processor()
        processor.rate = 'IPCA'
        last_run = processor.get_last_running_date()
        self.assertEquals(last_run, datetime(2017,2,28,17,00,00))

    def test_get_last_running_date_without_measure(self):
        processor = Processor()
        processor.rate = 'IPCA'
        processor.start_date = datetime(2017,2,27,17,00,00)
        last_run = processor.get_last_running_date()
        self.assertEquals(last_run, datetime(2017,2,27,17,00,00))
    
    @freezegun.freeze_time("2017-03-01 01:00:00")
    @mock.patch('rates.processors.Processor.get_last_running_date')
    @mock.patch('rates.processors.Processor.save')
    def test_execute(self, mk_save, mk_get_last_running_date):
        p = Processor()
        p.interval = timedelta(days=1)
        mk_get_last_running_date.return_value = datetime(2017, 2, 26,  0,1 , 0)
        p.execute()
        self.assertEquals(mk_save.call_count, 3)



class ProcessorA(object):
    def execute(self):
        pass


class ProcessorB(object):
    def execute(self):
        pass

class CDIProcessorTestCase(TestCase):

    def test_get_url(self):
        p = CDIProcessor()
        dt = datetime(2017, 3, 11)
        url = p.get_url(dt)
        self.assertEquals('ftp://ftp.cetip.com.br/MediaCDI/20170311.txt', url)

    def test_parse_value(self):
        raw = b'000001213                                                               \n'
        p = CDIProcessor()
        value = p.parse_value(raw)
        self.assertEquals(value, 12.13)

    @mock.patch('rates.processors.CDIProcessor.parse_value')
    @mock.patch('rates.processors.CDIProcessor.get_url')
    @mock.patch('urllib.request.urlopen')
    def test_get_measure(self, mk_urlopen, mk_get_url, mk_parse_value):
        mk_get_url.return_value = "http://www.google.com/"
        mock_urlopen = mock.Mock()

        p = CDIProcessor()
        p.get_measure('')
        mk_urlopen.assert_called_with("http://www.google.com/")

class IPCAProcessorTestCase(TestCase):
    def test_get_url(self):
        p = IPCAProcessor()
        dt = datetime(2020, 2, 24)
        url = p.get_url(dt)
        self.assertEquals(url, "http://api.sidra.ibge.gov.br/values/t/1737/p/202002/v/63/n1/1")


class TestCommand(TestCase):
    
    @mock.patch('rates.tests.ProcessorA.execute')
    @mock.patch('rates.tests.ProcessorB.execute')
    @mock.patch('rates.processors.Processor.__subclasses__')
    def test_handle(self, mk_subclass, mk_processorB, mk_processorA):
        p1 = mock.Mock()
        
        mk_subclass.return_value = [ProcessorA, ProcessorB]

        cmd = Command()
        cmd.handle()
        self.assertTrue(mk_processorA.called)
        self.assertTrue(mk_processorB.called)


class APITestCase(TestCase):

    def test_get(self):
        measure1 = MeasureFactory.create(measure_date=datetime(2017,3,4,17,00,00), rate="IPCA", measure=14.13)
        measure1.save()

        measure2 = MeasureFactory.create(measure_date=datetime(2017,2,28,17,00,00), rate="CDI", measure=12.5)
        measure2.save()

        url = '/rate'
        client = Client()
        response = client.get(url, {'filters': {'rate': 'CDI'}})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(float(response.content), 12.5)

    def test_get_none_measure(self):
        url = '/rate'
        client = Client()
        response = client.get(url, {'filters': {'rate': 'CDI'}})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, b'')

    def test_get_measure_filter(self):
        measure1 = MeasureFactory.create(measure_date=datetime(2017,3,4,0,0,0), rate="CDI", measure=14.13)
        measure1.save()

        measure2 = MeasureFactory.create(measure_date=datetime(2017,2,28,0,0,0), rate="CDI", measure=12.5)
        measure2.save()
        url = '/rate'
        filter = {'filters': {'rate': 'CDI', 'measure_date__lte': '28-02-2017'}}
        client = Client()
        response = client.get(url, filter)
        self.assertEquals(200, response.status_code)
        self.assertEquals(float(response.content), 12.5)

    def test_aggregate_function(self):
        measure1 = MeasureFactory.create(measure_date=datetime(2017,3,1,0,0,0), rate="IPCA", measure=1)
        measure1.save()

        measure2 = MeasureFactory.create(measure_date=datetime(2017,2,1,0,0,0), rate="IPCA", measure=1.5)
        measure2.save()

        url = '/rate'
        querystring = {
            'filters': {
                'rate': 'IPCA',
                'measure_date__gte': '01-02-2017',
                'measure_date__lte': '01-03-2017',
            },
            'function': 'Sum'
        } 
        client = Client()
        response = client.get(url, querystring)
        self.assertEquals(200, response.status_code)
        self.assertEquals(float(response.content), 2.5)
