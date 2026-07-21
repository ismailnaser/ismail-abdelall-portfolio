from .models import AboutPoint, NavItem, Project, Service, SiteSettings, Skill


def site_profile(request):
    settings = SiteSettings.load()
    return {
        "profile": settings,
        "projects": Project.objects.filter(is_published=True),
        "services": Service.objects.filter(is_visible=True),
        "skills": Skill.objects.filter(is_visible=True),
        "nav_items": NavItem.objects.filter(is_visible=True),
        "about_points": AboutPoint.objects.filter(is_visible=True),
    }
