import re
from datetime import datetime, timedelta
from django.utils import timezone

MESES_BR = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

DATA_LIMITE = timezone.now() - timedelta(days=180)

STATUS_KEYWORDS = {
    "encerrado": "encerrado",
    "cancelado": "encerrado",
    "homologado": "encerrado",
    "resultado final": "encerrado",
    "prorrogado": "prorrogado",
}


def parse_data_publicacao(texto: str) -> datetime | None:
    texto = texto.strip()
    m = re.search(r"(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})", texto, re.IGNORECASE)
    if m:
        dia, mes_nome, ano = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        mes = MESES_BR.get(mes_nome)
        if mes:
            return timezone.make_aware(datetime(ano, mes, dia))
    m2 = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if m2:
        dia, mes, ano = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        if 1 <= mes <= 12:
            return timezone.make_aware(datetime(ano, mes, dia))
    return None


def extrair_numero_edital(titulo: str) -> str | None:
    m = re.search(
        rf'(?:EDITAL|Edital)\s*{ORD_NUM}?([A-Za-z0-9/._-]+?)(?:\s*[,\-–—]\s*|\s+DE\s+|\s*$)',
        titulo, re.IGNORECASE
    )
    if m:
        return re.sub(r'\s+', ' ', m.group(1)).strip()
    m2 = re.search(rf'{ORD_NUM}([A-Za-z0-9/._-]+)', titulo)
    if m2:
        return m2.group(1).strip()
    return None


ORD_NUM = r'[Nn][º°o]\s*'


def _find_numbers(text: str) -> list[str]:
    return re.findall(rf'{ORD_NUM}[A-Za-z0-9/._-]+', text)


def reformatar_titulo_edital(titulo: str, descricao: str | None = None) -> str:
    t = titulo.strip()

    m = re.match(
        rf'(?:EDITAL\s+)?(.+?)\s*{ORD_NUM}[^\-]+?\s*[-–—]\s*(.+)',
        t, re.IGNORECASE
    )
    if m:
        orgao = m.group(1).strip()
        subject = m.group(2).strip()
        numbers = _find_numbers(t)
        suffix = f" ({numbers[0]})" if numbers else ""
        return f"{subject}{suffix} - {orgao}"

    m2 = re.match(
        rf'(?:EDITAL\s+)?(?:{ORD_NUM})([^\-]+?)\s*[-–—]\s*(.+)',
        t, re.IGNORECASE
    )
    if m2:
        subject = m2.group(2).strip()
        numbers = _find_numbers(t)
        suffix = f" ({numbers[0]})" if numbers else ""
        return f"{subject}{suffix}"

    # Fallback: just strip the "EDITAL" prefix
    t2 = re.sub(r'^(EDITAL\s+|Edital\s+)', '', t)
    return t2.strip()


def detectar_status(texto: str) -> str | None:
    texto_lower = texto.lower()
    for keyword, status in STATUS_KEYWORDS.items():
        if keyword in texto_lower:
            return status
    return None
