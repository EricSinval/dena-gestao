from django.urls import path

from . import views


app_name = "precificacao"

urlpatterns = [
    path(
        "configuracoes/",
        views.lista_configuracoes,
        name="lista_configuracoes",
    ),
    path(
        "configuracoes/nova/",
        views.cadastrar_configuracao,
        name="cadastrar_configuracao",
    ),
    path(
        "produto/<int:produto_id>/calcular/",
        views.calcular_preco_produto,
        name="calcular_preco_produto",
    ),
    path(
        "resultado/<int:precificacao_id>/",
        views.detalhe_precificacao,
        name="detalhe_precificacao",
    ),

    path(
        "<int:precificacao_id>/aplicar-preco/",
        views.aplicar_preco_sugerido,
        name="aplicar_preco_sugerido",
    ),
]