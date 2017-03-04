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

    @freeze_time("2017-02-27 18:00:00")
    def test_running_time(self):
        measure = MeasureFactory(measure_date=datetime(2017, 2, 26, 17, 59, 00))
        measure.save()
        p = Processor()
        p.interval = timedelta(days=1)
        p.tax = 'CDI'
        self.assertTrue(p.running_time())
    

    @freeze_time("2017-02-27 18:00:00")
    def test_running_time_false(self):
        measure = MeasureFactory(measure_date=datetime(2017,2,27,17,00,00))
        measure.save()
        p = Processor()
        p.interval = timedelta(days=1)
        p.tax = 'CDI'
        self.assertEquals(p.running_time(), False)

    
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


class TestCommand(TestCase):
    pass

