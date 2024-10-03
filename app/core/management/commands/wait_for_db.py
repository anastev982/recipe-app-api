"""
Django command to wait for the database to be available
"""
import time

from psycopg2 import OperationalError as Psycopg20pError
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to wait for the database."""

    def handle(self, *args, **options):
       """Entripoint for command."""
       self.stdout.write('Waiting for database..')
       db_up = False
       while db_up is False:
           try:
               self.check(databases=['default'])
               db_up = True
           except (Psycopg20pError, OperationalError):
               self.stdout.write('Database unavailable, waiting 1 seckond...')
               time.sleep(1)
       self.stdout.write(self.style.SUCCESS('Database avaible!'))
