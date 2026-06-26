from django.db import migrations


def publish_noticiaindexpage(apps, schema_editor):
    from wagtail.models import Page

    nip = Page.objects.filter(slug="noticias", content_type__app_label="noticias", content_type__model="noticiaindexpage").first()
    if not nip:
        return

    revision = nip.save_revision(user=None, log_action=True)
    revision.publish()


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0009_move_noticiaindexpage_under_home"),
    ]

    operations = [
        migrations.RunPython(publish_noticiaindexpage, migrations.RunPython.noop),
    ]
