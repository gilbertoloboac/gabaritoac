from celery import shared_task
from django.core.management import call_command


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def importar_editais_ufac(self, *args, **kwargs):
    try:
        call_command("importar_editais_ufac", *args, **kwargs)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def importar_editais_ifac(self, *args, **kwargs):
    try:
        call_command("importar_editais_ifac", *args, **kwargs)
    except Exception as exc:
        raise self.retry(exc=exc)