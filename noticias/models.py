from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

# ==========================================
# 1. SNIPPETS (Auxiliares e Gestão de Anúncios)
# ==========================================

@register_snippet
class FonteSnippet(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Fonte")
    url_base = models.URLField(verbose_name="URL Base")
    
    def __str__(self):
        return self.nome

@register_snippet
class CategoriaSnippet(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    slug = models.SlugField(max_length=100, unique=True)
    cor_badge = models.CharField(
        max_length=7, 
        default="#4B5563", 
        help_text="Código Hexadecimal para a cor no layout (Ex: #2563EB)"
    )

    def __str__(self):
        return self.nome

@register_snippet
class AnuncioSnippet(models.Model):
    cliente = models.CharField(max_length=255)
    imagem = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    link = models.URLField()
    posicao = models.CharField(
        max_length=50,
        choices=[
            ("topo_horizontal", "Banner Topo Horizontal (728x90) — Home"),
            ("abaixo_mural", "Abaixo do Mural de Editais (728x90) — Home"),
            ("topo_noticias", "Topo do Feed de Notícias (728x90)"),
            ("lateral_feed", "Sidebar Lateral (300x250) — Notícias"),
            ("intercalado_cards", "Intercalado no Feed de Cards"),
        ]
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cliente} - {self.get_posicao_display()}"


# ==========================================
# 2. MODELAGEM UNIFICADA DE CONTEÚDO (Notícias/Editais)
# ==========================================

class NoticiaPageTag(TaggedItemBase):
    content_object = ParentalKey('NoticiaPage', on_delete=models.CASCADE, related_name='tagged_items')

class NoticiaPage(Page):
    """
    Modelo único para Matérias convencionais e Editais/Concursos (Seção 6 e 11).
    A presença dos dados de edital define o comportamento dinâmico do template.
    """
    subpage_types = []  # Não possui páginas filhas
    
    # Campos Fundamentais da Notícia
    intro = models.TextField(help_text="Linha fina / Resumo que aparece abaixo do título principal.")
    imagem_capa = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    
    corpo = StreamField([
        ("paragrafo", blocks.RichTextBlock(features=['h2', 'h3', 'bold', 'italic', 'link', 'ol', 'ul'])),
        ("imagem", ImageChooserBlock()),
        ("citacao", blocks.BlockQuoteBlock()),
    ], use_json_field=True)

    # Campos Opcionais de Edital (Se preenchidos, ativam o bloco "Resumo das Vagas")
    orgao_responsavel = models.CharField(max_length=255, blank=True, null=True, verbose_name="Órgão Responsável (Edital)")
    numero_edital = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número do Edital")
    prazo_inscricao = models.DateField(blank=True, null=True, verbose_name="Inscrições Até")
    taxa_inscricao = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Taxa R$")
    salario_ate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Salários Até R$")
    link_pdf_oficial = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link Oficial do Edital/Inscrição")
    
    status_edital = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[("aberto", "Aberto"), ("encerrado", "Encerrado"), ("prorrogado", "Prorrogado")],
        verbose_name="Status do Edital"
    )

    @property
    def status_inscricao(self):
        prazo = self.prazo_inscricao
        if prazo:
            hoje = timezone.localdate()
            diff = (prazo - hoje).days
            if diff < 0:
                return ("Encerrado", "encerrado")
            elif diff <= 5:
                return ("Últimos Dias", "ultimos_dias")
            return ("Aberto", "aberto")
        val = self.status_edital or "aberto"
        labels = {"aberto": "Aberto", "encerrado": "Encerrado", "prorrogado": "Prorrogado"}
        return (labels.get(val, "Aberto"), val)

    # Controle de Revisão (Editais aguardam revisão manual antes de aparecer na Home)
    revisado = models.BooleanField(default=False, verbose_name="Revisado e Aprovado",
        help_text="Editais importados automaticamente só aparecem no mural da Home após revisão manual.")

    # Controle de Inteligência Artificial e Moderação
    gerado_por_ia = models.BooleanField(default=False, verbose_name="Gerado por IA")
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    
    # Classificação e Metadados de Origem
    fonte_original_url = models.URLField(max_length=500, blank=True, verbose_name="URL da Fonte Original")
    fonte = models.ForeignKey("FonteSnippet", on_delete=models.PROTECT, verbose_name="Fonte")
    categoria = models.ForeignKey("CategoriaSnippet", null=True, blank=True, on_delete=models.SET_NULL)
    tags = ClusterTaggableManager(through=NoticiaPageTag, blank=True)

    # Controle Curatorial para a Capa (Home)
    destaque = models.BooleanField(default=False, help_text="Se marcado, fica elegível para o topo da Home")
    destaque_ordem = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Ordem numérica no bloco Hero")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('imagem_capa'),
        FieldPanel('corpo'),
        
        # Bloco de Edital agrupado e opcional no Admin
        MultiFieldPanel([
            FieldPanel('orgao_responsavel'),
            FieldPanel('numero_edital'),
            FieldPanel('status_edital'),
            FieldPanel('prazo_inscricao'),
            FieldPanel('taxa_inscricao'),
            FieldPanel('salario_ate'),
            FieldPanel('link_pdf_oficial'),
        ], heading="Se for Edital/Concurso (Campos Opcionais)", classname="collapsible collapsed"),
        
        MultiFieldPanel([
            FieldPanel('categoria'),
            FieldPanel('tags'),
            FieldPanel('fonte'),
            FieldPanel('fonte_original_url'),
        ], heading="Classificação e Origem"),
        
        MultiFieldPanel([
            FieldPanel('revisado'),
            FieldPanel('gerado_por_ia'),
            FieldPanel('revisado_por'),
        ], heading="Revisão e Auditoria"),
        
        MultiFieldPanel([
            FieldPanel('destaque'),
            FieldPanel('destaque_ordem'),
        ], heading="Curadoria de Capa (Home)"),
    ]


# ==========================================
# 3. PÁGINAS DE ÍNDICE E LISTAGENS (Feeds)
# ==========================================

class NoticiaIndexPage(Page):
    """
    Representa a estrutura do feed de listagem completa 'Últimas Notícias' (image_a8eecb.png)
    """
    subpage_types = ['NoticiaPage']
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        
        todas_noticias = NoticiaPage.objects.child_of(self).live().order_by('-first_published_at')
        
        # Filtros ativos da Sidebar
        busca_termo = request.GET.get('busca', None)
        if busca_termo:
            todas_noticias = todas_noticias.filter(title__icontains=busca_termo)
            
        tag_filtro = request.GET.get('tag', None)
        if tag_filtro:
            todas_noticias = todas_noticias.filter(tags__slug=tag_filtro)

        categoria_filtro = request.GET.get('categoria', None)
        if categoria_filtro:
            todas_noticias = todas_noticias.filter(categoria__slug=categoria_filtro)

        # Paginação Estruturada
        paginator = Paginator(todas_noticias, 10)
        page = request.GET.get('page')
        try:
            noticias_paginadas = paginator.page(page)
        except PageNotAnInteger:
            noticias_paginadas = paginator.page(1)
        except EmptyPage:
            noticias_paginadas = paginator.page(paginator.num_pages)

        context['noticias'] = noticias_paginadas
        context['categorias_disponiveis'] = CategoriaSnippet.objects.all()
        
        context['anuncio_sidebar'] = AnuncioSnippet.objects.filter(
            posicao="lateral_feed", ativo=True
        ).first()

        context['categoria_filtro'] = categoria_filtro
        if categoria_filtro:
            cat_obj = CategoriaSnippet.objects.filter(slug=categoria_filtro).first()
            context['categoria_nome'] = cat_obj.nome if cat_obj else categoria_filtro.title()
        else:
            context['categoria_nome'] = None

        return context



class VestibularHubPage(Page):
    """
    Central Fixa Evergreen dedicada ao Vestibular e SISU UFAC (Seção 7).
    """
    subpage_types = []
    descricao = models.TextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('descricao'),
    ]