# Personal Portfolio (Django Templates only)

**No React. No Vite.** This project uses **Django templates** + static HTML/CSS/JS — the same approach as [Radar Tech](https://radartech85.pythonanywhere.com/).

Same layout and sections (Home, Projects, About, Services, Skills, Contact), Tailwind CDN, dark mode, and Arabic/English toggle.

**Theme:** violet / rose (different from Radar Tech’s blue palette).

## Quick start

```bash
cd "I:\my portfolio"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Customize your content

Edit **`main/site_data.py`**:

- Name, taglines, about text
- Projects (titles, summaries, links, images)
- Services, skills
- Email, WhatsApp, GitHub

## Deploy (e.g. PythonAnywhere)

1. Upload project files
2. Create virtualenv and `pip install -r requirements.txt`
3. Set `ALLOWED_HOSTS` and a real `SECRET_KEY` in `config/settings.py`
4. Point WSGI to `config.wsgi.application`
5. Run `python manage.py collectstatic` if you serve static files separately
