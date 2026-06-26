import re
from datetime import datetime

import requests
from lxml import html
from django.core.management.base import BaseCommand, CommandError

from noticias.models import NoticiaPage, NoticiaIndexPage, FonteSnippet, CategoriaSnippet
from noticias.utils.editais import (
    parse_data_publicacao,
    reformatar_titulo_edital,
    extrair_numero_edital,
    detectar_status,
    DATA_LIMITE,
)

BASE_URL = "https://editais.ifac.edu.br"
TIMEOUT = 30

SECOES = [
    ("quero-trabalhar-no-ifac", "editais"),
    ("quero-estudar-no-ifac", "editais"),
    ("sou-estudante-do-ifac", "editais"),
    ("sou-servidor-do-ifac", "editais"),
    ("quero-ser-parceiro-do-ifac", "editais"),
]

ORGAO_MAP = {
    "quero-trabalhar-no-ifac": "IFAC - Trabalhe Conosco",
    "quero-estudar-no-ifac": "IFAC - Processos Seletivos",
    "sou-estudante-do-ifac": "IFAC - Estudante",
    "sou-servidor-do-ifac": "IFAC - Servidor",
    "sou-da-comunidade": "IFAC - Comunidade",
    "quero-ser-parceiro-do-ifac": "IFAC - Parcerias",
}


def parse_badges(header_el) -> dict:
    badges = {"novo": False, "atualizado": False, "retificado": False, "status_from_bg": "aberto"}
    classes = header_el.get("class", "")
    spans = header_el.findall(".//span")
    for span in spans:
        texto = span.text_content().strip().lower()
        if texto == "novo":
            badges["novo"] = True
        elif texto == "atualizado":
            badges["atualizado"] = True
        elif texto == "retificado":
            badges["retificado"] = True
    if "bg-secondary" in classes:
        badges["status_from_bg"] = "encerrado"
    elif "bg-warning" in classes:
        badges["status_from_bg"] = "prorrogado"
    elif "bg-danger" in classes:
        badges["status_from_bg"] = "encerrado"
    return badges


def parse_card(card, orgao: str, secao_path: str):
    header_el = card.find_class("card-header")
    body_el = card.find_class("card-body")
    footer_el = card.find_class("card-footer")

    if not header_el or not body_el or not footer_el:
        return None

    title_raw = header_el[0].text_content().strip() if header_el else ""
    description = body_el[0].text_content().strip() if body_el else ""
    footer_text = footer_el[0].text_content().strip() if footer_el else ""

    # Strip badge text from title
    title_clean = re.sub(r'\s*(Novo|Atualizado|Retificado)\s*', '', title_raw, flags=re.IGNORECASE).strip()
    title_clean = re.sub(r'\s+', ' ', title_clean)

    pub_date = parse_data_publicacao(footer_text)

    link_el = footer_el[0].find(".//a") if footer_el else None
    link = ""
    if link_el is not None:
        href = link_el.get("href", "")
        if href:
            link = f"{BASE_URL}{href}" if href.startswith("/") else href

    if not title_clean or not link:
        return None

    badges = parse_badges(header_el[0])

    full_text = f"{title_clean} {description} {footer_text}".lower()
    status = detectar_status(full_text) or badges["status_from_bg"]

    # Reformat title: subject first, number after
    new_title = reformatar_titulo_edital(title_clean, description)
    numero = extrair_numero_edital(title_clean)

    return {
        "title": new_title,
        "title_raw": title_clean,
        "numero_edital": numero,
        "description": description,
        "link": link,
        "pub_date": pub_date,
        "orgao": orgao,
        "badges": badges,
        "status_edital": status,
    }


def fetch_secao(session, url: str, logger=None):
    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        return resp.text
    except requests.RequestException as e:
        if logger:
            logger(f"Erro ao acessar {url}: {e}")
        return None


class Command(BaseCommand):
    help = "Importa editais do portal IFAC (editais.ifac.edu.br) via scraping HTML"

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
            nome="IFAC",
            defaults={"url_base": BASE_URL},
        )
        cat, _ = CategoriaSnippet.objects.get_or_create(
            slug="editais",
            defaults={"nome": "Editais", "cor_badge": "#DC2626"},
        )

        criados = 0
        atualizados = 0
        ignorados = 0
        antigos = 0

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        })

        for secao_path, sub_path in SECOES:
            secao_full = f"{secao_path}/{sub_path}"
            orgao = ORGAO_MAP.get(secao_path, "IFAC")

            self.stdout.write(f"\n=== Seção: {secao_full} ({orgao}) ===")

            pagina = 1
            sem_resultados = False

            while not sem_resultados:
                self.stdout.write(f"  Página {pagina}...")

                content = fetch_secao(session, f"{BASE_URL}/{secao_full}/?page={pagina}", logger=self.stderr.write)
                if content is None or len(content) < 1000:
                    self.stdout.write("    (fim da paginação ou erro)")
                    break

                try:
                    tree = html.fromstring(content)
                except Exception as e:
                    self.stderr.write(f"    Erro ao parsear HTML: {e}")
                    break

                cards = tree.find_class("card")
                cards = [c for c in cards if c.find_class("card-header") and c.find_class("card-body")]

                if not cards:
                    self.stdout.write("    (sem cards — fim da paginação)")
                    break

                for card in cards:
                    parsed = parse_card(card, orgao, secao_full)
                    if not parsed:
                        ignorados += 1
                        continue

                    title = parsed["title"]
                    link = parsed["link"]
                    desc = parsed["description"]
                    pub_date = parsed["pub_date"]
                    status = parsed["status_edital"]
                    badges = parsed["badges"]
                    numero = parsed["numero_edital"]

                    if title.lower().startswith("link para"):
                        ignorados += 1
                        continue

                    # Skip editais older than DATA_LIMITE
                    if pub_date and pub_date < DATA_LIMITE:
                        antigos += 1
                        continue

                    short_link = link.rstrip("/")

                    if len(short_link) > 490:
                        self.stderr.write(f"    URL muito longa, ignorando")
                        ignorados += 1
                        continue

                    badge_str = ""
                    if badges.get("novo"):
                        badge_str += " [NOVO]"
                    if badges.get("atualizado"):
                        badge_str += " [ATUALIZADO]"
                    if badges.get("retificado"):
                        badge_str += " [RETIFICADO]"

                    self.stdout.write(f"  [{orgao}]{badge_str} {title[:80]}")
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
                        # If Atualizado badge, create new revision
                        if badges.get("atualizado"):
                            existing.save_revision(user=None, log_action=True)
                            self.stdout.write(f"    -> Revisão criada (atualização detectada)")
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
                            title=title.strip(),
                            slug=slug,
                            intro=desc[:500] if desc else f"Edital {orgao}",
                            corpo='[]',
                            orgao_responsavel=orgao,
                            numero_edital=numero,
                            link_pdf_oficial=link,
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

                        page.save_revision(user=None, log_action=True)
                        page.unpublish()
                        criados += 1
                        self.stdout.write(f"    -> Criado como draft (slug={slug})")

                    except Exception as e:
                        self.stderr.write(f"    -> ERRO: {e}")
                        ignorados += 1

                page_links = tree.xpath('//a[contains(@href, "page=")]/@href')
                max_page = 0
                for pl in page_links:
                    m = re.search(r"page[=/](\d+)", pl)
                    if m:
                        mp = int(m.group(1))
                        if mp > max_page:
                            max_page = mp

                pagina += 1
                if pagina > max_page:
                    sem_resultados = True

        self.stdout.write("\n--- RESUMO ---")
        self.stdout.write(f"Criados:     {criados}")
        self.stdout.write(f"Atualizados: {atualizados}")
        self.stdout.write(f"Ignorados:   {ignorados}")
        self.stdout.write(f"Antigos:     {antigos}")
