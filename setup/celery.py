import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings.production")

app = Celery("gabaritoac")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Explicitly discover tasks from known packages.
# Using force=True and listing packages directly avoids timing issues
# with Django's app registry initialization.
app.autodiscover_tasks(["noticias"], force=True)

app.conf.beat_schedule = {
    "importar-editais-ufac": {
        "task": "noticias.tasks.importar_editais_ufac",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "importar-editais-ifac": {
        "task": "noticias.tasks.importar_editais_ifac",
        "schedule": crontab(minute=30, hour="*/6"),
    },
}

app.conf.timezone = "America/Rio_Branco"