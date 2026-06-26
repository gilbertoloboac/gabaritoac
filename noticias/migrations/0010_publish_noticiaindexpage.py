from django.db import migrations


def publish_noticiaindexpage(apps, schema_editor):
    NoticiaIndexPage = apps.get_model("noticias.NoticiaIndexPage")
    Page = apps.get_model("wagtailcore.Page")

    nip = NoticiaIndexPage.objects.filter(slug="noticias").first()
    if not nip:
        return

    page = Page.objects.get(pk=nip.pk)
    if page.live:
        return

    from wagtail.models import Page as RealPage

    real_page = RealPage.objects.get(pk=nip.pk)
    revision = real_page.save_revision(user=None, log_action=True)
    revision.publish()


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0009_move_noticiaindexpage_under_home"),
    ]

    operations = [
        migrations.RunPython(publish_noticiaindexpage, migrations.RunPython.noop),
    ]
