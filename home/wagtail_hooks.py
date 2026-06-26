from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse


@hooks.register("register_admin_menu_item")
def register_noticias_menu():
    from noticias.models import NoticiaIndexPage

    nip = NoticiaIndexPage.objects.first()
    if nip:
        url = reverse("wagtailadmin_explore", args=[nip.pk])
    else:
        url = reverse("wagtailadmin_explore_root")
    return MenuItem(
        "Notícias",
        url,
        icon_name="list-ul",
        order=200,
    )
