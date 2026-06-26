from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from wagtail.models import Page
from noticias.models import NoticiaPage


class RevisaoEditaisView(View):
    template_name = "noticias/admin_revisao.html"
    page_title = "Revisão de Editais"

    def _get_editais(self, filtro):
        qs = NoticiaPage.objects.all().select_related("fonte", "categoria").order_by("-first_published_at")
        if filtro == "pendentes":
            qs = qs.filter(revisado=False)
        elif filtro == "aprovados":
            qs = qs.filter(revisado=True)
        return qs

    def get(self, request):
        filtro = request.GET.get("filtro", "todos")
        editais = self._get_editais(filtro)
        return render(request, self.template_name, {
            "page_title": self.page_title,
            "editais": editais,
            "filtro_atual": filtro,
        })

    def post(self, request):
        action = request.POST.get("action")
        page_ids = request.POST.getlist("page_ids")

        if not page_ids:
            messages.warning(request, "Nenhum edital selecionado.")
            return redirect(request.path)

        pages = NoticiaPage.objects.filter(id__in=page_ids)

        if action == "aprovar":
            with transaction.atomic():
                for page in pages:
                    page.revisado = True
                    page.revisado_por = request.user
                    revision = page.save_revision(user=request.user)
                    revision.publish()
            messages.success(request, f"{len(page_ids)} editais aprovados e republicados.")

        elif action == "rejeitar":
            for page in pages:
                page.unpublish()
            messages.success(request, f"{len(page_ids)} editais removidos do ar.")

        return redirect(f"{request.path}?filtro={request.POST.get('filtro', 'pendentes')}")
