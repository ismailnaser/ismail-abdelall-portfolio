from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SiteSettings(models.Model):
    """Single row — all global portfolio text & contact info."""

    name_en = models.CharField(max_length=120, default="Your Name")
    name_ar = models.CharField(max_length=120, default="اسمك")
    tagline_en = models.CharField(max_length=200, default="Full-Stack Developer")
    tagline_ar = models.CharField(max_length=200, default="مطور ويب متكامل")

    # Intro profile (shown above the hero)
    photo = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        verbose_name="الصورة الشخصية",
        help_text="صورة مصغرة تظهر في القسم التعريفي أعلى الصفحة",
    )
    education_en = models.CharField(
        max_length=200,
        blank=True,
        default="Computer Science Student",
        verbose_name="الدراسة (EN)",
    )
    education_ar = models.CharField(
        max_length=200,
        blank=True,
        default="طالب علوم حاسوب",
        verbose_name="الدراسة (AR)",
    )
    location_en = models.CharField(
        max_length=120,
        blank=True,
        default="Palestine",
        verbose_name="الموقع (EN)",
    )
    location_ar = models.CharField(
        max_length=120,
        blank=True,
        default="فلسطين",
        verbose_name="الموقع (AR)",
    )
    intro_bio_en = models.CharField(
        max_length=280,
        blank=True,
        default="Building clean full-stack web products.",
        verbose_name="نبذة قصيرة (EN)",
        help_text="سطر قصير تحت الاسم في القسم التعريفي",
    )
    intro_bio_ar = models.CharField(
        max_length=280,
        blank=True,
        default="أبني منتجات ويب متكاملة ونظيفة.",
        verbose_name="نبذة قصيرة (AR)",
    )

    hero_title_en = models.TextField(blank=True, default="")
    hero_title_ar = models.TextField(blank=True, default="")
    hero_subtitle_en = models.TextField(blank=True, default="")
    hero_subtitle_ar = models.TextField(blank=True, default="")
    about_en = models.TextField(blank=True, default="")
    about_ar = models.TextField(blank=True, default="")
    contact_intro_en = models.TextField(blank=True, default="")
    contact_intro_ar = models.TextField(blank=True, default="")

    email = models.EmailField(default="you@example.com")
    whatsapp = models.CharField(
        max_length=20,
        help_text="أرقام فقط مع رمز الدولة، مثال: 970592533678",
        default="970000000000",
    )
    github_username = models.CharField(max_length=80, default="yourusername")
    github_url = models.URLField(default="https://github.com/yourusername")

    hero_btn_projects_en = models.CharField(max_length=60, default="View Projects")
    hero_btn_projects_ar = models.CharField(max_length=60, default="عرض المشاريع")
    hero_btn_contact_en = models.CharField(max_length=60, default="Contact Me")
    hero_btn_contact_ar = models.CharField(max_length=60, default="تواصل معي")

    projects_title_en = models.CharField(max_length=120, default="Featured Projects")
    projects_title_ar = models.CharField(max_length=120, default="المشاريع المميزة")
    about_title_en = models.CharField(max_length=120, default="Who I Am")
    about_title_ar = models.CharField(max_length=120, default="من أنا")
    services_title_en = models.CharField(max_length=120, default="Services")
    services_title_ar = models.CharField(max_length=120, default="الخدمات")
    services_lead_en = models.TextField(
        default="I deliver clean, scalable, and maintainable software solutions."
    )
    services_lead_ar = models.TextField(default="أقدّم حلول برمجية نظيفة وقابلة للتوسع.")
    skills_title_en = models.CharField(max_length=120, default="Core Skills")
    skills_title_ar = models.CharField(max_length=120, default="المهارات الأساسية")
    contact_title_en = models.CharField(max_length=120, default="Contact")
    contact_title_ar = models.CharField(max_length=120, default="تواصل")

    contact_success_en = models.CharField(
        max_length=200,
        default="Your message was sent successfully. Thank you!",
    )
    contact_success_ar = models.CharField(
        max_length=200,
        default="تم إرسال رسالتك بنجاح. شكراً لك!",
    )

    project_back_en = models.CharField(max_length=80, default="Back to projects")
    project_back_ar = models.CharField(max_length=80, default="العودة للمشاريع")
    project_gallery_title_en = models.CharField(max_length=120, default="Photo Gallery")
    project_gallery_title_ar = models.CharField(max_length=120, default="معرض الصور")
    details_btn_en = models.CharField(max_length=60, default="Details")
    details_btn_ar = models.CharField(max_length=60, default="التفاصيل")

    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"

    def __str__(self):
        return self.name_en

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class NavItem(models.Model):
    section_id = models.SlugField(
        max_length=40,
        unique=True,
        help_text="معرف القسم في الصفحة مثل: home أو projects أو about",
    )
    label_en = models.CharField(max_length=80)
    label_ar = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "section_id"]
        verbose_name = "رابط التنقل"
        verbose_name_plural = "روابط التنقل"

    def __str__(self):
        return self.label_en


class Project(models.Model):
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    title_en = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200)
    summary_en = models.TextField(help_text="نص قصير يظهر على كرت المشروع في الصفحة الرئيسية")
    summary_ar = models.TextField()
    detail_en = models.TextField(
        blank=True,
        default="",
        help_text="الوصف الكامل في صفحة تفاصيل المشروع",
    )
    detail_ar = models.TextField(blank=True, default="")
    stack_en = models.CharField(max_length=300)
    stack_ar = models.CharField(max_length=300)
    live_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title_en"]
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"

    def __str__(self):
        return self.title_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en) or "project"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image = models.ImageField(upload_to="projects/gallery/")
    caption_en = models.CharField(max_length=200, blank=True, default="")
    caption_ar = models.CharField(max_length=200, blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "صورة معرض"
        verbose_name_plural = "صور المعرض"

    def __str__(self):
        return f"{self.project.title_en} — image {self.pk}"


class Service(models.Model):
    title_en = models.CharField(max_length=120)
    title_ar = models.CharField(max_length=120)
    desc_en = models.TextField()
    desc_ar = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title_en"]
        verbose_name = "خدمة"
        verbose_name_plural = "الخدمات"

    def __str__(self):
        return self.title_en


class Skill(models.Model):
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "مهارة"
        verbose_name_plural = "المهارات"

    def __str__(self):
        return self.name


class AboutPoint(models.Model):
    text_en = models.CharField(max_length=300)
    text_ar = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "نقطة تعريف"
        verbose_name_plural = "نقاط التعريف"

    def __str__(self):
        return self.text_en

    @property
    def en(self):
        return self.text_en

    @property
    def ar(self):
        return self.text_ar


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d}"
