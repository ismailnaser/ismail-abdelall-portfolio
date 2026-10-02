from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_longer_slug_and_image_paths"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="kind_ar",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="kind_en",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="period_ar",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="period_en",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="role_ar",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="project",
            name="role_en",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="service",
            name="period_ar",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="service",
            name="period_en",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="service",
            name="role_ar",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="service",
            name="role_en",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="service",
            name="tags_ar",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="service",
            name="tags_en",
            field=models.CharField(blank=True, default="", max_length=300),
        ),
        migrations.AddField(
            model_name="skill",
            name="category",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
    ]
