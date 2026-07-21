from django.core.management.base import BaseCommand

from main import site_data
from main.models import AboutPoint, NavItem, Project, Service, SiteSettings, Skill


class Command(BaseCommand):
    help = "Import portfolio content from main/site_data.py into the database"

    def handle(self, *args, **options):
        p = site_data.PROFILE
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        settings.name_en = p["name_en"]
        settings.name_ar = p["name_ar"]
        settings.tagline_en = p["tagline_en"]
        settings.tagline_ar = p["tagline_ar"]
        settings.hero_title_en = p["hero_title_en"]
        settings.hero_title_ar = p["hero_title_ar"]
        settings.hero_subtitle_en = p["hero_subtitle_en"]
        settings.hero_subtitle_ar = p["hero_subtitle_ar"]
        settings.about_en = p["about_en"]
        settings.about_ar = p["about_ar"]
        settings.contact_intro_en = p["contact_intro_en"]
        settings.contact_intro_ar = p["contact_intro_ar"]
        settings.email = p["email"]
        settings.whatsapp = p["whatsapp"]
        settings.github_username = p["github_username"]
        settings.github_url = p["github_url"]
        settings.save()

        for i, (en, ar) in enumerate(
            zip(p["about_points_en"], p["about_points_ar"])
        ):
            AboutPoint.objects.update_or_create(
                text_en=en,
                defaults={"text_ar": ar, "order": i, "is_visible": True},
            )

        for i, item in enumerate(site_data.NAV_ITEMS):
            NavItem.objects.update_or_create(
                section_id=item["id"],
                defaults={
                    "label_en": item["label_en"],
                    "label_ar": item["label_ar"],
                    "order": i,
                    "is_visible": True,
                },
            )

        for i, proj in enumerate(site_data.PROJECTS):
            Project.objects.update_or_create(
                slug=proj["slug"],
                defaults={
                    "title_en": proj["title_en"],
                    "title_ar": proj["title_ar"],
                    "summary_en": proj["summary_en"],
                    "summary_ar": proj["summary_ar"],
                    "stack_en": proj["stack_en"],
                    "stack_ar": proj["stack_ar"],
                    "live_url": proj.get("live_url") or "",
                    "github_url": proj.get("github_url") or "",
                    "order": i,
                    "is_published": True,
                },
            )

        for i, svc in enumerate(site_data.SERVICES):
            Service.objects.update_or_create(
                title_en=svc["title_en"],
                defaults={
                    "title_ar": svc["title_ar"],
                    "desc_en": svc["desc_en"],
                    "desc_ar": svc["desc_ar"],
                    "order": i,
                    "is_visible": True,
                },
            )

        for i, name in enumerate(site_data.SKILLS):
            Skill.objects.update_or_create(
                name=name,
                defaults={"order": i, "is_visible": True},
            )

        self.stdout.write(self.style.SUCCESS("Portfolio data imported successfully."))
