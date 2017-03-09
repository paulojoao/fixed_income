#coding: utf-8
from django.core.management.base import BaseCommand, CommandError

from tax.models import Measure
from tax.processors import Processor

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        processors = Processor.__subclasses__()
        for p in processors:
            processor = p()
            processor.execute()
