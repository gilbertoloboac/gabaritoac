from django.db import migrations


def move_noticiaindexpage_under_home(apps, schema_editor):
    Page = apps.get_model("wagtailcore.Page")
    ContentType = apps.get_model("contenttypes.ContentType")
    NoticiaIndexPage = apps.get_model("noticias.NoticiaIndexPage")

    try:
        home = Page.objects.get(slug="home", depth=2)
        nip = Page.objects.get(slug="noticias")
    except Page.DoesNotExist:
        return

    # Check if NIP is already correct (child of home)
    if nip.path.startswith(home.path) and nip.depth == home.depth + 1:
        return

    # Use treebeard's move to reposition
    # In migrations, we need the real treebeard path logic.
    # We switch to the real model for the move operation.
    from wagtail.models import Page as RealPage

    real_home = RealPage.objects.get(pk=home.pk)
    real_nip = RealPage.objects.get(pk=nip.pk)
    real_nip.move(real_home, pos="last-child")


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0008_create_celery_periodic_tasks"),
    ]

    operations = [
        migrations.RunPython(
            move_noticiaindexpage_under_home, migrations.RunPython.noop
        ),
    ]
