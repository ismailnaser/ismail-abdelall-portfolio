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
from .translation import fill_empty_en_from_ar

admin.site.site_header = "إدارة المعرض"
admin.site.site_title = "لوحة التحكم"
admin.site.index_title = "مرحباً — اختر قسماً للتعديل"

_AR_EN_HINT = (
    "اكتب النص بالعربي؛ إذا تركت الحقل الإنجليزي فارغاً يُترجم تلقائياً عند الحفظ. "
    "لو عبّيت الإنجليزي بنفسك ما رح ينكتب فوقه."
)


class AutoTranslateAdminMixin:
    """Allow empty EN fields in forms; fill them from AR on save."""

    def get_form(self, request, obj=None, change=False, **kwargs):
        Form = super().get_form(request, obj, change=change, **kwargs)

        class AutoTranslateForm(Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for name, field in self.fields.items():
                    if name.endswith("_en"):
                        field.required = False
                        if "يُترجم من العربي" not in (field.help_text or ""):
                            field.help_text = (
                                (field.help_text + " — " if field.help_text else "")
                                + "اختياري: يُترجم من العربي إن تُرك فارغاً"
                            )

        AutoTranslateForm.__name__ = getattr(Form, "__name__", "AutoTranslateForm")
        return AutoTranslateForm

    def save_model(self, request, obj, form, change):
        _apply_ar_to_en(request, obj)
        super().save_model(request, obj, form, change)


class AdminImageMediaMixin:
    """Optional crop UI on default Django admin."""

    class Media:
        css = {"all": ("css/admin-image.css",)}
        js = ("js/admin-image-preview.js",)


def _save_with_cloudinary_guard(admin_obj, request, obj, form, change):
    try:
        admin.ModelAdmin.save_model(admin_obj, request, obj, form, change)
    except Exception as exc:
        msg = str(exc)
        if "api_key" in msg.lower() or "AuthorizationRequired" in type(exc).__name__:
            raise ValidationError(
                "فشل رفع الصورة إلى Cloudinary: مفتاح API غير صحيح. "
                "راجع CLOUDINARY_API_KEY / CLOUDINARY_URL في Render "
                "واستبدل أي قيمة مثل <your_api_key> بالمفتاح الحقيقي من لوحة Cloudinary."
            ) from exc
        raise


def _apply_ar_to_en(request, obj, *, notify=True) -> list[str]:
    filled = fill_empty_en_from_ar(obj)
    if notify and filled and request is not None:
        messages.info(
            request,
            f"تُرجم تلقائياً إلى الإنجليزية: {', '.join(filled)}",
        )
    return filled


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "caption_ar", "caption_en", "order")


@admin.register(SiteSettings)
class SiteSettingsAdmin(AdminImageMediaMixin, AutoTranslateAdminMixin, admin.ModelAdmin):
    save_on_top = True
    fieldsets = (
        (
            "القسم التعريفي (أعلى الصفحة)",
            {
                "description": (
                    "يظهر قبل الهيرو: الصورة، الاسم، والدراسة. "
                    f"{_AR_EN_HINT} الاقتصاص اختياري — الصورة بتنحفظ كاملة إلا إذا فعّلت الاقتصاص."
                ),
                "fields": (
                    "photo",
                    ("name_ar", "name_en"),
                    ("tagline_ar", "tagline_en"),
                    ("education_ar", "education_en"),
                    "intro_bio_ar",
                    "intro_bio_en",
                ),
            },
        ),
        (
            "قسم الهيرو (الصفحة الرئيسية)",
            {
                "description": f"العنوان الكبير والنص اللي تحتّه وأزرار الدعوة للتفاعل. {_AR_EN_HINT}",
                "fields": (
                    "hero_title_ar",
                    "hero_title_en",
                    "hero_subtitle_ar",
                    "hero_subtitle_en",
                    ("hero_btn_projects_ar", "hero_btn_projects_en"),
                    ("hero_btn_contact_ar", "hero_btn_contact_en"),
                ),
            },
        ),
        (
            "من أنا",
            {
                "description": _AR_EN_HINT,
                "fields": ("about_ar", "about_en"),
            },
        ),
        (
            "عناوين الأقسام",
            {
                "description": f"عدّل عناوين الأقسام الظاهرة في الموقع. {_AR_EN_HINT}",
                "fields": (
                    ("projects_title_ar", "projects_title_en"),
                    ("about_title_ar", "about_title_en"),
                    ("services_title_ar", "services_title_en"),
                    "services_lead_ar",
                    "services_lead_en",
                    ("skills_title_ar", "skills_title_en"),
                    ("contact_title_ar", "contact_title_en"),
                ),
            },
        ),
        (
            "التواصل وروابط التواصل",
            {
                "description": f"الإيميل والواتساب وGitHub تظهر في قسم التواصل. {_AR_EN_HINT}",
                "fields": (
                    "contact_intro_ar",
                    "contact_intro_en",
                    ("email", "whatsapp"),
                    ("github_username", "github_url"),
                    ("contact_success_ar", "contact_success_en"),
                ),
            },
        ),
        (
            "نصوص صفحات المشاريع",
            {
                "classes": ("collapse",),
                "description": _AR_EN_HINT,
                "fields": (
                    ("details_btn_ar", "details_btn_en"),
                    ("project_back_ar", "project_back_en"),
                    ("project_gallery_title_ar", "project_gallery_title_en"),
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        _apply_ar_to_en(request, obj)
        _save_with_cloudinary_guard(self, request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse

        obj = SiteSettings.load()
        return redirect(reverse("admin:main_sitesettings_change", args=[obj.pk]))


@admin.register(NavItem)
class NavItemAdmin(AutoTranslateAdminMixin, admin.ModelAdmin):
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
                "description": (
                    "روابط القائمة الجانبية. section_id لازم يطابق معرف القسم في الصفحة "
                    f"(مثل home أو projects). {_AR_EN_HINT}"
                ),
                "fields": (
                    ("label_ar", "label_en"),
                    "section_id",
                    ("order", "is_visible"),
                ),
            },
        ),
    )


@admin.register(Project)
class ProjectAdmin(AdminImageMediaMixin, AutoTranslateAdminMixin, admin.ModelAdmin):
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

    fieldsets = (
        (
            "معلومات أساسية",
            {
                "description": (
                    "اكتب العنوان بالعربي واترك الإنجليزي فارغاً ليُترجم عند الحفظ "
                    "(وإلا املأ الإنجليزي يدوياً). الاقتصاص اختياري بعد اختيار الصورة."
                ),
                "fields": (
                    ("title_ar", "title_en"),
                    "slug",
                    "image",
                    ("order", "is_published"),
                ),
            },
        ),
        (
            "بطاقة الصفحة الرئيسية",
            {
                "description": f"النص القصير والتقنيات اللي تظهر على كرت المشروع. {_AR_EN_HINT}",
                "fields": (
                    "summary_ar",
                    "summary_en",
                    ("stack_ar", "stack_en"),
                ),
            },
        ),
        (
            "صفحة التفاصيل",
            {
                "description": f"الوصف الكامل وروابط المشروع. أضف صور المعرض من الأسفل. {_AR_EN_HINT}",
                "fields": (
                    "detail_ar",
                    "detail_en",
                    ("live_url", "github_url"),
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        _apply_ar_to_en(request, obj)
        _save_with_cloudinary_guard(self, request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for obj in instances:
            _apply_ar_to_en(request, obj, notify=False)
            obj.save()
        formset.save_m2m()

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
class ServiceAdmin(AutoTranslateAdminMixin, admin.ModelAdmin):
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
                "description": f"خدماتك المعروضة في قسم الخدمات. {_AR_EN_HINT}",
                "fields": (
                    ("title_ar", "title_en"),
                    "desc_ar",
                    "desc_en",
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
class AboutPointAdmin(AutoTranslateAdminMixin, admin.ModelAdmin):
    list_display = ("text_ar", "text_en", "order", "is_visible")
    list_display_links = ("text_ar", "text_en")
    list_editable = ("order", "is_visible")
    ordering = ("order",)
    save_on_top = True
    fieldsets = (
        (
            None,
            {
                "description": f"نقاط تظهر تحت فقرة «من أنا». {_AR_EN_HINT}",
                "fields": (
                    "text_ar",
                    "text_en",
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
        return "مقروءة" if obj.is_read else "جديدة"

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
