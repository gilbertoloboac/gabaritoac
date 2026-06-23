from django import template
from django.utils import timezone
from noticias.models import AnuncioSnippet

register = template.Library()

@register.simple_tag
def banner_topo():
    hoje = timezone.now().date()
    return AnuncioSnippet.objects.filter(
        ativo=True,
        posicao="topo_horizontal",
        data_inicio__lte=hoje,
        data_fim__gte=hoje,
    ).first()

@register.simple_tag
def banner_abaixo_mural():
    hoje = timezone.now().date()
    return AnuncioSnippet.objects.filter(
        ativo=True,
        posicao="abaixo_mural",
        data_inicio__lte=hoje,
        data_fim__gte=hoje,
    ).first()

@register.simple_tag
def banner_topo_noticias():
    hoje = timezone.now().date()
    return AnuncioSnippet.objects.filter(
        ativo=True,
        posicao="topo_noticias",
        data_inicio__lte=hoje,
        data_fim__gte=hoje,
    ).first()
