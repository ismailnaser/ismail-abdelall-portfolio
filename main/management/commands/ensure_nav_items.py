from django.core.management.base import BaseCommand

from main import site_data
from main.models import NavItem


class Command(BaseCommand):
    help = "Create default sidebar nav links if none exist (safe for production deploy)"

    def handle(self, *args, **options):
        if NavItem.objects.exists():
            self.stdout.write(self.style.SUCCESS("Nav links already exist — skipped."))
            return

        for i, item in enumerate(site_data.NAV_ITEMS):
            NavItem.objects.create(
                section_id=item["id"],
                label_en=item["label_en"],
                label_ar=item["label_ar"],
                order=i,
                is_visible=True,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(site_data.NAV_ITEMS)} default nav links.")
        )
