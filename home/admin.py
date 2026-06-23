from django.contrib import admin
from home.models import NewsletterSignup


@admin.register(NewsletterSignup)
class NewsletterSignupAdmin(admin.ModelAdmin):
    list_display = ('nome', 'whatsapp', 'criado_em', 'consentimento', 'consentimento_em')
    list_filter = ('criado_em', 'consentimento')
    search_fields = ('nome', 'whatsapp')
    date_hierarchy = 'criado_em'
    readonly_fields = ('criado_em', 'consentimento_em')
