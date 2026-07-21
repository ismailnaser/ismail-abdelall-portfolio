from django.shortcuts import get_object_or_404, render

from .forms import ContactForm
from .models import ContactMessage, Project


def home(request):
    form = ContactForm(request.POST or None)
    sent = False

    if request.method == "POST":
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"],
            )
            sent = True
            form = ContactForm()

    return render(
        request,
        "index.html",
        {
            "form": form,
            "contact_sent": sent,
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    return render(
        request,
        "project_detail.html",
        {"project": project, "gallery_images": project.gallery_images.all()},
    )
