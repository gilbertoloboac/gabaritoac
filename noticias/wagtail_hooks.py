from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from noticias.views import RevisaoEditaisView


@hooks.register("register_admin_urls")
def register_revisao_url():
    return [
        path("revisao/", RevisaoEditaisView.as_view(), name="revisao_editais"),
    ]


@hooks.register("register_admin_menu_item")
def register_revisao_menu():
    return MenuItem(
        "Revisão de Editais",
        reverse("revisao_editais"),
        icon_name="tick-inverse",
        order=210,
    )
