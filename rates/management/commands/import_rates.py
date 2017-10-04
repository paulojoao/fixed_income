#coding: utf-8
from django.core.management.base import BaseCommand, CommandError

from rates.models import Measure
from rates.processors import Processor

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        processors = Processor.__subclasses__()
        for p in processors:
            processor = p()
            processor.execute()