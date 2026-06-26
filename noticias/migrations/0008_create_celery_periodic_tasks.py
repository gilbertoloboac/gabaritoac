from django.db import migrations


def create_periodic_tasks(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat.CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat.PeriodicTask")

    if PeriodicTask.objects.filter(
        task__in=["noticias.tasks.importar_editais_ufac", "noticias.tasks.importar_editais_ifac"],
    ).exists():
        return

    schedule_ufac, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="*/6",
        day_of_month="*",
        month_of_year="*",
        day_of_week="*",
        timezone="America/Rio_Branco",
    )

    schedule_ifac, _ = CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="*/6",
        day_of_month="*",
        month_of_year="*",
        day_of_week="*",
        timezone="America/Rio_Branco",
    )

    PeriodicTask.objects.get_or_create(
        name="importar-editais-ufac",
        defaults=dict(
            task="noticias.tasks.importar_editais_ufac",
            crontab=schedule_ufac,
            enabled=True,
            description="Importa editais do portal UFAC via RSS a cada 6 horas",
        ),
    )

    PeriodicTask.objects.get_or_create(
        name="importar-editais-ifac",
        defaults=dict(
            task="noticias.tasks.importar_editais_ifac",
            crontab=schedule_ifac,
            enabled=True,
            description="Importa editais do portal IFAC a cada 6 horas",
        ),
    )


def remove_periodic_tasks(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat.PeriodicTask")
    PeriodicTask.objects.filter(
        task__in=["noticias.tasks.importar_editais_ufac", "noticias.tasks.importar_editais_ifac"],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0007_create_noticiaindexpage"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(create_periodic_tasks, remove_periodic_tasks),
    ]
