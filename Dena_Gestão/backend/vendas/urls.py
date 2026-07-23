from django.urls import path

from . import views


app_name = "vendas"

urlpatterns = [
    path(
        "clientes/",
        views.lista_clientes,
        name="lista_clientes",
    ),
    path(
        "clientes/cadastrar/",
        views.cadastrar_cliente,
        name="cadastrar_cliente",
    ),
    path(
        "clientes/<int:cliente_id>/",
        views.detalhe_cliente,
        name="detalhe_cliente",
    ),
    path(
        "clientes/<int:cliente_id>/editar/",
        views.editar_cliente,
        name="editar_cliente",
    ),
    path(
        "clientes/<int:cliente_id>/alterar-status/",
        views.alterar_status_cliente,
        name="alterar_status_cliente",
    ),
    path(
        "pedidos/",
        views.lista_pedidos,
        name="lista_pedidos",
    ),
    path(
        "pedidos/cadastrar/",
        views.cadastrar_pedido,
        name="cadastrar_pedido",
    ),
    path(
        "pedidos/<int:pedido_id>/",
        views.detalhe_pedido,
        name="detalhe_pedido",
    ),
]