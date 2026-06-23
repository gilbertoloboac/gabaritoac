from django.contrib import admin
from home.models import NewsletterSignup


@admin.register(NewsletterSignup)
class NewsletterSignupAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'criado_em')
    list_filter = ('criado_em',)
    search_fields = ('nome', 'email')
    date_hierarchy = 'criado_em'
    readonly_fields = ('criado_em',)
