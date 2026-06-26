from django.db import migrations


def create_noticiaindexpage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    NoticiaIndexPage = apps.get_model("noticias.NoticiaIndexPage")

    if NoticiaIndexPage.objects.exists():
        return

    homepage = Page.objects.filter(depth=2, slug="home").first()
    if not homepage:
        return

    content_type, _ = ContentType.objects.get_or_create(
        model="noticiaindexpage", app_label="noticias",
    )

    page = NoticiaIndexPage.objects.create(
        title="Noticias",
        draft_title="Noticias",
        slug="noticias",
        content_type=content_type,
        path=homepage.path + "0001",
        depth=homepage.depth + 1,
        numchild=0,
        url_path=homepage.url_path + "noticias/",
        intro="",
    )

    Page.objects.filter(pk=homepage.pk).update(numchild=1)


def remove_noticiaindexpage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    NoticiaIndexPage = apps.get_model("noticias.NoticiaIndexPage")
    NoticiaIndexPage.objects.filter(slug="noticias").delete()
    ContentType.objects.filter(model="noticiaindexpage", app_label="noticias").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("noticias", "0006_noticiapage_revisado"),
    ]

    operations = [
        migrations.RunPython(create_noticiaindexpage, remove_noticiaindexpage),
    ]
