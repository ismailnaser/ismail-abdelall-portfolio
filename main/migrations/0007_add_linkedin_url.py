from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_portfolio_v2_experience_layout"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="linkedin_url",
            field=models.URLField(
                blank=True,
                default="https://www.linkedin.com/in/ismail-nsr",
                help_text="رابط ملف LinkedIn الكامل",
                verbose_name="LinkedIn",
            ),
        ),
    ]
