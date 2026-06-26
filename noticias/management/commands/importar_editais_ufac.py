import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from lxml import etree
from django.core.management.base import BaseCommand, CommandError

from noticias.models import NoticiaPage, NoticiaIndexPage, FonteSnippet, CategoriaSnippet
from noticias.utils.editais import (
    parse_data_publicacao,
    reformatar_titulo_edital,
    extrair_numero_edital,
    detectar_status,
    DATA_LIMITE,
)

RSS_URL = "https://www3.ufac.br/editais/RSS"
TIMEOUT = 30
NS_RSS = "http://purl.org/rss/1.0/"
NS_DC = "http://purl.org/dc/elements/1.1/"

PRO_SIGLAS = {
    "PROAES", "PROGRAD", "PROPEG", "PROPLAN", "PROGEP",
    "PROCULT", "PROAD", "NAI", "NEABI", "CCBN", "CCET",
    "CCSD", "CELA", "CFCH", "CCNT", "CCJSA", "NIEAD",
}


def extract_orgao(url: str) -> str:
    path = urlparse(url).path.strip("/")
    parts = path.split("/")

    if len(parts) >= 2 and parts[0] == "centros":
        slug = parts[1]
    elif parts:
        slug = parts[0]
    else:
        return "UFAC"

    name = slug.upper().replace("-", " ").replace("_", " ").strip()
    name = re.sub(r"\s+", " ", name)
    words = name.split()
    cleaned = [w.upper() if w.upper() in PRO_SIGLAS else w.capitalize() for w in words]
    return " ".join(cleaned)


def parse_rfc3339(text: str):
    text = text.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Importa editais do portal UFAC (www3.ufac.br) via feed RSS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas exibe o que seria importado sem salvar",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        parent = NoticiaIndexPage.objects.first()
        if not parent:
            raise CommandError("Nenhuma NoticiaIndexPage encontrada na árvore.")

        fonte, _ = FonteSnippet.objects.get_or_create(
            nome="UFAC",
            defaults={"url_base": "https://www3.ufac.br"},
        )
        cat, _ = CategoriaSnippet.objects.get_or_create(
            slug="editais",
            defaults={"nome": "Editais", "cor_badge": "#DC2626"},
        )

        self.stdout.write(f"Parent: {parent.title} (id={parent.id})")
        self.stdout.write(f"Fonte: {fonte.nome} | Categoria: {cat.nome}")
        self.stdout.write(f"Fetching RSS: {RSS_URL} ...")

        try:
            resp = requests.get(RSS_URL, timeout=TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise CommandError(f"Erro ao acessar RSS: {e}")

        root = etree.fromstring(resp.content)
        items = root.findall(f"{{{NS_RSS}}}item")
        self.stdout.write(f"Encontrados {len(items)} itens no RSS.\n")

        criados = 0
        atualizados = 0
        ignorados = 0
        antigos = 0

        for item in items:
            title_raw = item.findtext(f"{{{NS_RSS}}}title", "").strip()
            link = item.findtext(f"{{{NS_RSS}}}link", "").strip()
            desc = item.findtext(f"{{{NS_RSS}}}description", "").strip()

            if not title_raw or not link:
                ignorados += 1
                continue

            if title_raw.lower().startswith("link para"):
                ignorados += 1
                continue

            pub_date = None
            dc_date = item.find(f"{{{NS_DC}}}date")
            if dc_date is not None and dc_date.text:
                pub_date = parse_rfc3339(dc_date.text)

            # Skip old editais
            if pub_date and pub_date < DATA_LIMITE:
                antigos += 1
                continue

            orgao = extract_orgao(link)

            # Reformat title: subject first, number after
            title = reformatar_titulo_edital(title_raw, desc)
            numero = extrair_numero_edital(title_raw)

            # Detect status from title + description
            full_text = f"{title_raw} {desc}".lower()
            status = detectar_status(full_text) or "aberto"

            short_link = link.rstrip("/")
            short_link = re.sub(r"/link-.*$", "", short_link)
            if len(short_link) > 490:
                self.stderr.write(f"    URL muito longa ({len(short_link)} chars), ignorando")
                ignorados += 1
                continue

            self.stdout.write(f"  [{orgao}] {title[:80]}")
            self.stdout.write(f"    Status: {status}")
            if numero:
                self.stdout.write(f"    Nº: {numero}")
            if pub_date:
                self.stdout.write(f"    Data: {pub_date.date()}")

            if dry_run:
                continue

            existing = NoticiaPage.objects.filter(
                fonte_original_url=short_link
            ).first()

            if existing:
                changed = False
                updates = {}
                if existing.orgao_responsavel != orgao:
                    updates["orgao_responsavel"] = orgao
                    changed = True
                if existing.status_edital != status:
                    updates["status_edital"] = status
                    changed = True
                if numero and existing.numero_edital != numero:
                    updates["numero_edital"] = numero
                    changed = True
                if changed:
                    NoticiaPage.objects.filter(pk=existing.pk).update(**updates)
                atualizados += 1
                continue

            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:80]
            orig_slug = slug
            counter = 1
            while NoticiaPage.objects.filter(slug=slug).exists():
                slug = f"{orig_slug}-{counter}"
                counter += 1

            try:
                page = NoticiaPage(
                    title=title,
                    slug=slug,
                    intro=desc[:500] if desc else f"Edital {orgao}",
                    corpo='[]',
                    orgao_responsavel=orgao,
                    numero_edital=numero,
                    link_pdf_oficial=short_link,
                    fonte_original_url=short_link,
                    status_edital=status,
                    gerado_por_ia=True,
                    revisado=False,
                    fonte=fonte,
                    categoria=cat,
                )
                if pub_date:
                    page.first_published_at = pub_date

                parent.add_child(instance=page)

                revision = page.save_revision(user=None, log_action=True)
                revision.publish()
                criados += 1
                self.stdout.write(f"    -> Criado e publicado (slug={slug})")

            except Exception as e:
                self.stderr.write(f"    -> ERRO: {e}")
                ignorados += 1

        self.stdout.write("\n--- RESUMO ---")
        self.stdout.write(f"Criados:     {criados}")
        self.stdout.write(f"Atualizados: {atualizados}")
        self.stdout.write(f"Ignorados:   {ignorados}")
        self.stdout.write(f"Antigos:     {antigos}")
