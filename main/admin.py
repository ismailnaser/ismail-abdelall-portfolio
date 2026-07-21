from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    AboutPoint,
    ContactMessage,
    NavItem,
    Project,
    ProjectImage,
    Service,
    SiteSettings,
    Skill,
)

admin.site.site_header = "إدارة المعرض"
admin.site.site_title = "لوحة التحكم"
admin.site.index_title = "مرحباً — اختر قسماً للتعديل"


def _save_with_cloudinary_guard(admin_obj, request, obj, form, change):
    try:
        super(type(admin_obj), admin_obj).save_model(request, obj, form, change)
    except Exception as exc:
        msg = str(exc)
        if "api_key" in msg.lower() or "AuthorizationRequired" in type(exc).__name__:
            raise ValidationError(
                "فشل رفع الصورة إلى Cloudinary: مفتاح API غير صحيح. "
                "راجع CLOUDINARY_API_KEY / CLOUDINARY_URL في Render "
                "واستبدل أي قيمة مثل <your_api_key> بالمفتاح الحقيقي من لوحة Cloudinary."
            ) from exc
        raise


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "caption_en", "caption_ar", "order")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    save_on_top = True
    fieldsets = (
        (
            "القسم التعريفي (أعلى الصفحة)",
            {
                "description": "يظهر قبل الهيرو: الصورة، الاسم، والدراسة. بعد اختيار الصورة حرّك مربع الاقتصاص لتحديد الجزء الظاهر.",
                "fields": (
                    "photo",
                    ("name_en", "name_ar"),
                    ("tagline_en", "tagline_ar"),
                    ("education_en", "education_ar"),
                    "intro_bio_en",
                    "intro_bio_ar",
                ),
            },
        ),
        (
            "قسم الهيرو (الصفحة الرئيسية)",
            {
                "description": "العنوان الكبير والنص اللي تحتّه وأزرار الدعوة للتفاعل.",
                "fields": (
                    "hero_title_en",
                    "hero_title_ar",
                    "hero_subtitle_en",
                    "hero_subtitle_ar",
                    ("hero_btn_projects_en", "hero_btn_projects_ar"),
                    ("hero_btn_contact_en", "hero_btn_contact_ar"),
                ),
            },
        ),
        (
            "من أنا",
            {
                "fields": ("about_en", "about_ar"),
            },
        ),
        (
            "عناوين الأقسام",
            {
                "description": "عدّل عناوين الأقسام الظاهرة في الموقع.",
                "fields": (
                    ("projects_title_en", "projects_title_ar"),
                    ("about_title_en", "about_title_ar"),
                    ("services_title_en", "services_title_ar"),
                    "services_lead_en",
                    "services_lead_ar",
                    ("skills_title_en", "skills_title_ar"),
                    ("contact_title_en", "contact_title_ar"),
                ),
            },
        ),
        (
            "التواصل وروابط التواصل",
            {
                "description": "الإيميل والواتساب وGitHub تظهر في قسم التواصل.",
                "fields": (
                    "contact_intro_en",
                    "contact_intro_ar",
                    ("email", "whatsapp"),
                    ("github_username", "github_url"),
                    ("contact_success_en", "contact_success_ar"),
                ),
            },
        ),
        (
            "نصوص صفحات المشاريع",
            {
                "classes": ("collapse",),
                "fields": (
                    ("details_btn_en", "details_btn_ar"),
                    ("project_back_en", "project_back_ar"),
                    ("project_gallery_title_en", "project_gallery_title_ar"),
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        _save_with_cloudinary_guard(self, request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse

        obj = SiteSettings.load()
        return redirect(reverse("admin:main_sitesettings_change", args=[obj.pk]))


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ("label_ar", "label_en", "section_id", "order", "is_visible")
    list_editable = ("order", "is_visible")
    list_display_links = ("label_ar", "label_en")
    list_filter = ("is_visible",)
    search_fields = ("label_en", "label_ar", "section_id")
    ordering = ("order",)
    save_on_top = True
    fieldsets = (
        (
            None,
            {
                "description": "روابط القائمة الجانبية. section_id لازم يطابق معرف القسم في الصفحة (مثل home أو projects).",
                "fields": (
                    ("label_en", "label_ar"),
                    "section_id",
                    ("order", "is_visible"),
                ),
            },
        ),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "thumb",
        "title_ar",
        "title_en",
        "order",
        "is_published",
        "gallery_count",
    )
    list_display_links = ("thumb", "title_ar", "title_en")
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title_en", "title_ar", "slug", "stack_en")
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = [ProjectImageInline]
    save_on_top = True
    ordering = ("order",)

    def save_model(self, request, obj, form, change):
        _save_with_cloudinary_guard(self, request, obj, form, change)

    fieldsets = (
        (
            "معلومات أساسية",
            {
                "description": "العنوان والصورة الرئيسية وحالة النشر. بعد اختيار الصورة حدّد جزء الاقتصاص اللي يظهر في الموقع.",
                "fields": (
                    ("title_en", "title_ar"),
                    "slug",
                    "image",
                    ("order", "is_published"),
                ),
            },
        ),
        (
            "بطاقة الصفحة الرئيسية",
            {
                "description": "النص القصير والتقنيات اللي تظهر على كرت المشروع.",
                "fields": (
                    "summary_en",
                    "summary_ar",
                    ("stack_en", "stack_ar"),
                ),
            },
        ),
        (
            "صفحة التفاصيل",
            {
                "description": "الوصف الكامل وروابط المشروع. أضف صور المعرض من الأسفل.",
                "fields": (
                    "detail_en",
                    "detail_ar",
                    ("live_url", "github_url"),
                ),
            },
        ),
    )

    @admin.display(description="صورة")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="admin-thumb" alt="" />',
                obj.image.url,
            )
        return mark_safe('<span style="color:#9aa8a3">بدون صورة</span>')

    @admin.display(description="معرض")
    def gallery_count(self, obj):
        count = obj.gallery_images.count()
        return f"{count} صورة" if count else "—"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title_ar", "title_en", "order", "is_visible")
    list_display_links = ("title_ar", "title_en")
    list_editable = ("order", "is_visible")
    search_fields = ("title_en", "title_ar", "desc_en", "desc_ar")
    ordering = ("order",)
    save_on_top = True
    fieldsets = (
        (
            None,
            {
                "description": "خدماتك المعروضة في قسم الخدمات.",
                "fields": (
                    ("title_en", "title_ar"),
                    "desc_en",
                    "desc_ar",
                    ("order", "is_visible"),
                ),
            },
        ),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("name",)
    ordering = ("order",)
    save_on_top = True


@admin.register(AboutPoint)
class AboutPointAdmin(admin.ModelAdmin):
    list_display = ("text_ar", "text_en", "order", "is_visible")
    list_display_links = ("text_ar", "text_en")
    list_editable = ("order", "is_visible")
    ordering = ("order",)
    save_on_top = True
    fieldsets = (
        (
            None,
            {
                "description": "نقاط تظهر تحت فقرة «من أنا».",
                "fields": (
                    "text_en",
                    "text_ar",
                    ("order", "is_visible"),
                ),
            },
        ),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("status_icon", "name", "email", "short_message", "created_at", "is_read")
    list_display_links = ("name", "email")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = ("mark_as_read", "mark_as_unread")
    fieldsets = (
        (
            "تفاصيل الرسالة",
            {
                "fields": ("name", "email", "created_at", "is_read", "message"),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description="")
    def status_icon(self, obj):
        if obj.is_read:
            return mark_safe('<i class="fas fa-envelope-open" title="مقروءة"></i>')
        return mark_safe('<i class="fas fa-envelope" title="جديدة"></i>')

    @admin.display(description="الرسالة")
    def short_message(self, obj):
        text = obj.message.strip().replace("\n", " ")
        return text[:60] + ("…" if len(text) > 60 else "")

    @admin.action(description="تعليم كمقروءة")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"تم تعليم {updated} رسالة كمقروءة.")

    @admin.action(description="تعليم كغير مقروءة")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"تم تعليم {updated} رسالة كغير مقروءة.")
