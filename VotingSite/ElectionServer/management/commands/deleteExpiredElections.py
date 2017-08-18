from django.core.management.base import BaseCommand, CommandError
from ElectionServer.models import Election
import datetime

class Command(BaseCommand):
    help = 'Deletes elections that have ended over 30 days ago'

    def handle(self, *args, **options):
        try:
            elections = Election.objects.all()
            for election in elections:
                if election.endDate<datetime.datetime.now()-datetime.timedelta(days=30):
                    election.delete()
        except Exception:
            print("An error occurred")