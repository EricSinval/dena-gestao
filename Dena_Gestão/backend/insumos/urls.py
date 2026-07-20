from django.urls import path

from . import views


app_name = "insumos"

urlpatterns = [
    path(
        "",
        views.lista_materias_primas,
        name="lista_materias_primas",
    ),
    path(
        "cadastrar/",
        views.cadastrar_materia_prima,
        name="cadastrar_materia_prima",
    ),
    path(
        "categorias/cadastrar/",
        views.cadastrar_categoria,
        name="cadastrar_categoria",
    ),
    path(
        "<int:materia_prima_id>/",
        views.detalhe_materia_prima,
        name="detalhe_materia_prima",
    ),
    path(
        "<int:materia_prima_id>/editar/",
        views.editar_materia_prima,
        name="editar_materia_prima",
    ),
    path(
        "<int:materia_prima_id>/alterar-status/",
        views.alterar_status_materia_prima,
        name="alterar_status_materia_prima",
    ),
    path(
        "<int:materia_prima_id>/movimentar/",
        views.movimentar_materia_prima,
        name="movimentar_materia_prima",
    ),
]