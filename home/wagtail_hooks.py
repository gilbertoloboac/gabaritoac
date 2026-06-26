from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse


@hooks.register("register_admin_menu_item")
def register_noticias_menu():
    return MenuItem(
        "Notícias",
        "/admin/pages/4/",
        icon_name="list-ul",
        order=200,
    )
