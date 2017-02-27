#coding: utf-8
from unittest import mock

from django.test import TestCase
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

