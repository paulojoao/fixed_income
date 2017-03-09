#coding: utf-8
from unittest import mock
from datetime import datetime, timedelta

import freezegun
from django.test import TestCase
from django.test import Client

from tax.factories import MeasureFactory
from tax.models import Measure
from tax.processors import Processor 
from tax.management.commands.import_tax import Command


class ProcessorTestCase(TestCase):
    @mock.patch('tax.processors.Processor.get_measure')
    def test_save(self, mk_get_value):
        mk_get_value.return_value = 10.0
        old_count = Measure.objects.count()
        processor = Processor()
        processor.save()
        new_count = Measure.objects.count()
        self.assertEquals(old_count, new_count)
    
    def test_get_last_running_date(self):
        measure1 = MeasureFactory.create(measure_date=datetime(2017,3,4,17,00,00), tax="CDI")
        measure1.save()

        measure2 = MeasureFactory.create(measure_date=datetime(2017,2,28,17,00,00), tax="IPCA")
        measure2.save()

        measure3 = MeasureFactory.create(measure_date=datetime(2017,2,27,17,00,00), tax="IPCA")
        measure3.save()

        processor = Processor()
        processor.tax = 'IPCA'
        last_run = processor.get_last_running_date()
        self.assertEquals(last_run, datetime(2017,2,28,17,00,00))

    def test_get_last_running_date_without_measure(self):
        processor = Processor()
        processor.tax = 'IPCA'
        processor.start_date = datetime(2017,2,27,17,00,00)
        last_run = processor.get_last_running_date()
        self.assertEquals(last_run, datetime(2017,2,27,17,00,00))
    
    @freezegun.freeze_time("2017-03-01 01:00:00")
    @mock.patch('tax.processors.Processor.get_last_running_date')
    @mock.patch('tax.processors.Processor.save')
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

class TestCommand(TestCase):
    
    @mock.patch('tax.tests.ProcessorA.execute')
    @mock.patch('tax.tests.ProcessorB.execute')
    @mock.patch('tax.processors.Processor.__subclasses__')
    def test_handle(self, mk_subclass, mk_processorB, mk_processorA):
        p1 = mock.Mock()
        
        mk_subclass.return_value = [ProcessorA, ProcessorB]

        cmd = Command()
        cmd.handle()
        self.assertTrue(mk_processorA.called)
        self.assertTrue(mk_processorB.called)


class APITestCase(TestCase):

    def test_get(self):
        measure1 = MeasureFactory.create(measure_date=datetime(2017,3,4,17,00,00), tax="CDI", measure=14.13)
        measure1.save()

        measure2 = MeasureFactory.create(measure_date=datetime(2017,2,28,17,00,00), tax="IPCA", measure=12.5)
        measure2.save()

        url = '/rate'
        client = Client()
        response = client.get(url, {'rate': 'CDI'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(float(response.content), 14.13)