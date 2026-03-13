from django.core.management.base import BaseCommand
from raksha.models import CrisisRequest
from raksha.assignment import assign_volunteer_to_request


class Command(BaseCommand):
    help = 'Assign volunteers to high-priority unassigned requests'

    def handle(self, *args, **options):
        qs = CrisisRequest.objects.filter(priority_score__gte=70.0)
        count = 0
        for req in qs:
            if not req.assignments.exists():
                ass = assign_volunteer_to_request(req)
                if ass:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'Assigned {count} requests'))
