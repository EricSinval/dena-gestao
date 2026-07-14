from django.urls import path

from . import views


app_name = "produtos"

urlpatterns = [
    path(
        "",
        views.lista_produtos,
        name="lista_produtos",
    ),
    path(
        "cadastrar/",
        views.cadastrar_produto,
        name="cadastrar_produto",
    ),
    path(
        "<int:produto_id>/",
        views.detalhe_produto,
        name="detalhe_produto",
    ),
    path(
        "<int:produto_id>/editar/",
        views.editar_produto,
        name="editar_produto",
    ),
    path(
        "<int:produto_id>/alterar-status/",
        views.alterar_status_produto,
        name="alterar_status_produto",
    ),
    path(
        "<int:produto_id>/variacoes/cadastrar/",
        views.cadastrar_variacao,
        name="cadastrar_variacao",
    ),
    path(
        "variacoes/<int:variacao_id>/editar/",
        views.editar_variacao,
        name="editar_variacao",
    ),
    path(
        "variacoes/<int:variacao_id>/alterar-status/",
        views.alterar_status_variacao,
        name="alterar_status_variacao",
    ),
]