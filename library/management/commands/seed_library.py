from django.core.management.base import BaseCommand
from library.seed_data import create_all_seed_data


class Command(BaseCommand):
    help = 'Seeds database with realistic authors, books, members, and circulation records'

    def handle(self, *args, **options):
        self.stdout.write("Seeding library sample data...")
        create_all_seed_data()
        self.stdout.write(self.style.SUCCESS("Successfully populated library catalog and circulation records!"))
