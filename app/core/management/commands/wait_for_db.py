import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as OperationalError1


class Command(BaseCommand):
    """Django command to pause execution until DB is available"""
    def handle(self, *args, **kwargs):
        self.stdout.write('Waiting for database...')
        time.sleep(1)
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                self.stdout.write("-------DB CONN-------")
                self.stdout.write(db_conn)
            except (OperationalError, OperationalError1, Exception):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database is now available'))
