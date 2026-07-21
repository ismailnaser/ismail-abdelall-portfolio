from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
]

# Serve uploaded media (profile/project images). On Render free disk is ephemeral —
# for permanent storage later use S3/Cloudinary.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
