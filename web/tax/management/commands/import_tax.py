#coding: utf-8
from django.core.management.base import BaseCommand, CommandError
from tax.models import Measure


class Command(BaseCommand):

    def get_processors(self):
        pass

    