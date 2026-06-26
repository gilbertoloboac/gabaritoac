from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel
from noticias.models import NoticiaPage, CategoriaSnippet

class HomePage(Page):
    # Permite páginas filhas
    subpage_types = ['noticias.NoticiaIndexPage', 'home.SobrePage', 'home.NewsletterPage', 'home.PoliticaPrivacidadePage', 'home.ContatoPage']

    def get_context(self, request):
        context = super().get_context(request)
        
        noticias_vivas = NoticiaPage.objects.live().public()

        context['noticia_principal'] = noticias_vivas.order_by('-first_published_at').first()
        
        cat_editais = CategoriaSnippet.objects.filter(slug="editais").first()
        mural_qs = noticias_vivas
        if cat_editais:
            mural_qs = mural_qs.filter(categoria=cat_editais)

        todos_editais = list(mural_qs.order_by('prazo_inscricao', '-first_published_at')[:12])
        grupos = {"ultimos_dias": [], "aberto": [], "encerrado": []}
        for e in todos_editais:
            _, key = e.status_inscricao
            if key in grupos:
                grupos[key].append(e)

        context['mural_editais_urgentes'] = grupos['ultimos_dias']
        context['mural_editais_abertos'] = grupos['aberto']
        context['mural_editais_encerrados'] = grupos['encerrado']

        destaques_ids = noticias_vivas.filter(destaque=True).values_list('id', flat=True)
        context['ultimas_noticias'] = noticias_vivas.exclude(id__in=destaques_ids).order_by('-first_published_at')[:6]

        return context


class SobrePage(Page):
    subpage_types = []
    parent_page_types = ['home.HomePage']

    imagem = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    corpo = StreamField([
        ("paragrafo", blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul'])),
        ("imagem", ImageChooserBlock()),
        ("citacao", blocks.BlockQuoteBlock()),
    ], use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField('corpo'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('imagem'),
        FieldPanel('corpo'),
    ]


class NewsletterSignup(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome")
    whatsapp = models.CharField(max_length=20, unique=True, verbose_name="WhatsApp", help_text="Número com DDD, apenas números (ex: 5599999999999)")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de inscrição")
    consentimento = models.BooleanField(default=False, verbose_name="Autorizo o tratamento dos meus dados pessoais conforme a Política de Privacidade")
    consentimento_em = models.DateTimeField(null=True, blank=True, verbose_name="Data do consentimento")

    class Meta:
        verbose_name = "Inscrição WhatsApp"
        verbose_name_plural = "Inscrições WhatsApp"

    def __str__(self):
        return f"{self.nome} — {self.whatsapp}"


class NewsletterPage(Page):
    subpage_types = []
    parent_page_types = ['home.HomePage']

    corpo = StreamField([
        ("paragrafo", blocks.RichTextBlock(features=['h2', 'h3', 'bold', 'italic', 'link'])),
    ], use_json_field=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('corpo'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('corpo'),
    ]

    class Meta:
        verbose_name = "Página WhatsApp"
        verbose_name_plural = "Páginas WhatsApp"

    def serve(self, request):
        from django.shortcuts import render

        return render(request, 'home/newsletter_page.html', {'page': self})


class PoliticaPrivacidadePage(Page):
    subpage_types = []
    parent_page_types = ['home.HomePage']

    corpo = StreamField([
        ("paragrafo", blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul'])),
        ("citacao", blocks.BlockQuoteBlock()),
    ], use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField('corpo'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('corpo'),
    ]

    class Meta:
        verbose_name = "Política de Privacidade"
        verbose_name_plural = "Políticas de Privacidade"


class ContatoPage(Page):
    subpage_types = []
    parent_page_types = ['home.HomePage']

    corpo = StreamField([
        ("paragrafo", blocks.RichTextBlock(features=['h2', 'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul'])),
    ], use_json_field=True)

    dpo_email = models.EmailField(
        verbose_name="E-mail do DPO/Encarregado",
        help_text="E-mail para contato do Encarregado de Dados (LGPD Art. 41)",
        default="dpo@gabaritoac.com.br",
    )

    search_fields = Page.search_fields + [
        index.SearchField('corpo'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('corpo'),
        FieldPanel('dpo_email'),
    ]

    class Meta:
        verbose_name = "Contato / DPO"
        verbose_name_plural = "Contatos / DPO"