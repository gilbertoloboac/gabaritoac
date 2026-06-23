from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel
from noticias.models import NoticiaPage, CategoriaSnippet

class HomePage(Page):
    # Permite páginas filhas
    subpage_types = ['noticias.NoticiaIndexPage', 'home.SobrePage', 'home.NewsletterPage']

    def get_context(self, request):
        context = super().get_context(request)
        
        # 1. Puxa todas as notícias publicadas
        noticias_vivas = NoticiaPage.objects.live().public()

        # 2. Hero Split: Notícia Principal (Destaque=True)
        context['noticia_principal'] = noticias_vivas.filter(destaque=True).order_by('destaque_ordem', '-first_published_at').first()
        
        # 3. Mural de Editais: Só revisados, agrupados por status, máx 8 na Home
        cat_editais = CategoriaSnippet.objects.filter(slug="editais").first()
        mural_qs = noticias_vivas.filter(revisado=True)
        if cat_editais:
            mural_qs = mural_qs.filter(categoria=cat_editais)

        todos_editais = list(mural_qs.order_by('prazo_inscricao', '-first_published_at')[:8])
        grupos = {"ultimos_dias": [], "aberto": [], "encerrado": []}
        for e in todos_editais:
            _, key = e.status_inscricao
            if key in grupos:
                grupos[key].append(e)

        context['mural_editais_urgentes'] = grupos['ultimos_dias']
        context['mural_editais_abertos'] = grupos['aberto']
        context['mural_editais_encerrados'] = grupos['encerrado']

        # 5. Grid Inferior: últimas notícias (exclui as de destaque)
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
    email = models.EmailField(unique=True, verbose_name="E-mail")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de inscrição")

    class Meta:
        verbose_name = "Inscrição Newsletter"
        verbose_name_plural = "Inscrições Newsletter"

    def __str__(self):
        return f"{self.nome} <{self.email}>"


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

    def serve(self, request):
        from django.shortcuts import render, redirect

        if getattr(request, 'is_preview', False):
            return render(request, 'home/newsletter_page.html', {'page': self})

        if request.method == 'POST':
            nome = request.POST.get('nome', '').strip()
            email = request.POST.get('email', '').strip()
            erro = None

            if not nome or not email:
                erro = "Preencha todos os campos."
            elif NewsletterSignup.objects.filter(email=email).exists():
                erro = "Este e-mail já está cadastrado."

            if erro:
                return render(request, 'home/newsletter_page.html', {
                    'page': self,
                    'erro': erro,
                    'nome': nome,
                    'email': email,
                })

            NewsletterSignup.objects.create(nome=nome, email=email)

            try:
                send_mail(
                    subject=f"Nova inscrição na newsletter: {nome}",
                    message=f"{nome} <{email}> se inscreveu na newsletter.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            return render(request, 'home/newsletter_page.html', {
                'page': self,
                'sucesso': True,
            })

        return render(request, 'home/newsletter_page.html', {
            'page': self,
        })