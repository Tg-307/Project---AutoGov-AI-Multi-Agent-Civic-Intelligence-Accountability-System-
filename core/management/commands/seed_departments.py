from django.core.management.base import BaseCommand
from core.models import Department


DEPARTMENTS = [
    {'code': 'PWD', 'name': 'Public Works Department', 'email': 'pwd@gov.in'},
    {'code': 'MCD', 'name': 'Municipal Corporation Department', 'email': 'mcd@gov.in'},
    {'code': 'ELEC', 'name': 'Electricity & Street Lighting Department', 'email': 'elec@gov.in'},
    {'code': 'PHE', 'name': 'Public Health Engineering Department', 'email': 'phe@gov.in'},
    {'code': 'REVENUE', 'name': 'Revenue & Land Management Department', 'email': 'revenue@gov.in'},
    {'code': 'COLLECTOR', 'name': "District Collector's Office", 'email': 'collector@gov.in'},
]


class Command(BaseCommand):
    help = 'Seed initial department data'

    def handle(self, *args, **kwargs):
        for dept_data in DEPARTMENTS:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data,
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f"  [{status}] {dept.name}")
        self.stdout.write(self.style.SUCCESS('Department seeding complete.'))
