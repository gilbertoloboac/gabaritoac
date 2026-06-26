from django.core.management.base import BaseCommand
from wagtail.models import Page
from noticias.models import NoticiaIndexPage


class Command(BaseCommand):
    help = "Garante que a NoticiaIndexPage existe, está na árvore correta e publicada"

    def handle(self, *args, **options):
        home = Page.objects.filter(slug="home", depth=2).first()
        if not home:
            self.stderr.write("HomePage (slug='home', depth=2) não encontrada.")
            return

        self.stdout.write(f"HomePage: pk={home.pk}, path={home.path}, depth={home.depth}")

        nip = NoticiaIndexPage.objects.filter(slug="noticias").first()

        if not nip:
            self.stdout.write("NoticiaIndexPage não existe. Criando...")
            nip = NoticiaIndexPage(
                title="Notícias",
                slug="noticias",
                intro="",
            )
            home.add_child(instance=nip)
            self.stdout.write(self.style.SUCCESS(f"Criada: pk={nip.pk}, path={nip.path}"))
        else:
            page = Page.objects.get(pk=nip.pk)
            self.stdout.write(f"NoticiaIndexPage existe: pk={nip.pk}, path={page.path}, depth={page.depth}, live={page.live}")

        real_nip = Page.objects.get(pk=nip.pk)

        is_child_of_home = real_nip.depth == home.depth + 1 and real_nip.path.startswith(home.path)
        if not is_child_of_home:
            self.stdout.write("NoticiaIndexPage não é filha da HomePage. Movendo...")
            real_nip.move(home, pos="last-child")
            real_nip.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(f"Movida: path={real_nip.path}, depth={real_nip.depth}"))

        if not real_nip.live:
            self.stdout.write("NoticiaIndexPage não está publicada. Publicando...")
            revision = real_nip.save_revision(user=None, log_action=True)
            revision.publish()
            real_nip.refresh_from_db()
            self.stdout.write(self.style.SUCCESS(f"Publicada: live={real_nip.live}"))
        else:
            self.stdout.write(self.style.SUCCESS("NoticiaIndexPage já está publicada."))

        self.stdout.write(self.style.SUCCESS(f"\nURL: /noticias/ → path={real_nip.path}, url_path={real_nip.url_path}"))
