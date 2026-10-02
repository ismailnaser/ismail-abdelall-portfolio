from django.core.management.base import BaseCommand

from main import site_data
from main.models import AboutPoint, NavItem, Project, Service, SiteSettings, Skill


class Command(BaseCommand):
    help = "Import portfolio content from main/site_data.py into the database"

    def handle(self, *args, **options):
        p = site_data.PROFILE
        settings, _ = SiteSettings.objects.get_or_create(pk=1)

        for field in (
            "name_en",
            "name_ar",
            "tagline_en",
            "tagline_ar",
            "location_en",
            "location_ar",
            "education_en",
            "education_ar",
            "intro_bio_en",
            "intro_bio_ar",
            "hero_title_en",
            "hero_title_ar",
            "hero_subtitle_en",
            "hero_subtitle_ar",
            "about_en",
            "about_ar",
            "contact_intro_en",
            "contact_intro_ar",
            "email",
            "whatsapp",
            "github_username",
            "github_url",
            "linkedin_url",
        ):
            if field in p:
                setattr(settings, field, p[field])
        settings.save()

        AboutPoint.objects.all().delete()
        for i, (en, ar) in enumerate(zip(p["about_points_en"], p["about_points_ar"])):
            AboutPoint.objects.create(
                text_en=en, text_ar=ar, order=i, is_visible=True
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

        keep_slugs = {proj["slug"] for proj in site_data.PROJECTS}
        Project.objects.exclude(slug__in=keep_slugs).update(is_published=False)
        for i, proj in enumerate(site_data.PROJECTS):
            Project.objects.update_or_create(
                slug=proj["slug"],
                defaults={
                    "title_en": proj["title_en"],
                    "title_ar": proj["title_ar"],
                    "summary_en": proj["summary_en"],
                    "summary_ar": proj["summary_ar"],
                    "detail_en": proj.get("detail_en", ""),
                    "detail_ar": proj.get("detail_ar", ""),
                    "stack_en": proj["stack_en"],
                    "stack_ar": proj["stack_ar"],
                    "kind_en": proj.get("kind_en", ""),
                    "kind_ar": proj.get("kind_ar", ""),
                    "period_en": proj.get("period_en", ""),
                    "period_ar": proj.get("period_ar", ""),
                    "role_en": proj.get("role_en", ""),
                    "role_ar": proj.get("role_ar", ""),
                    "live_url": proj.get("live_url") or "",
                    "github_url": proj.get("github_url") or "",
                    "order": i,
                    "is_published": True,
                },
            )

        keep_services = {svc["title_en"] for svc in site_data.SERVICES}
        Service.objects.exclude(title_en__in=keep_services).update(is_visible=False)
        for i, svc in enumerate(site_data.SERVICES):
            Service.objects.update_or_create(
                title_en=svc["title_en"],
                defaults={
                    "title_ar": svc["title_ar"],
                    "desc_en": svc["desc_en"],
                    "desc_ar": svc["desc_ar"],
                    "period_en": svc.get("period_en", ""),
                    "period_ar": svc.get("period_ar", ""),
                    "role_en": svc.get("role_en", ""),
                    "role_ar": svc.get("role_ar", ""),
                    "tags_en": svc.get("tags_en", ""),
                    "tags_ar": svc.get("tags_ar", ""),
                    "order": i,
                    "is_visible": True,
                },
            )

        keep_skills = set(site_data.SKILLS)
        Skill.objects.exclude(name__in=keep_skills).update(is_visible=False)
        for i, name in enumerate(site_data.SKILLS):
            Skill.objects.update_or_create(
                name=name,
                defaults={"order": i, "is_visible": True, "category": ""},
            )

        self.stdout.write(self.style.SUCCESS("Portfolio data imported successfully."))
