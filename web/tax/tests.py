#coding: utf-8
from unittest import mock
from datetime import datetime, timedelta

from freezegun import freeze_time
from django.test import TestCase

from tax.factories import MeasureFactory
from tax.models import Measure
from tax.processors import Processor 


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
    
    @freeze_time("2017-03-01 01:00:00")
    @mock.patch('tax.processors.Processor.get_last_running_date')
    @mock.patch('tax.processors.Processor.save')
    def test_execute(self, mk_get_last_running_date, mk_save):
        p = Processor()
        mk_get_last_running_date.return_value = datetime(2017, 3, 1, 17 ,0 , 0)
        p.execute()
        self.assertEquals(mk_save.call_count, 2)


class TestCommand(TestCase):
    pass

