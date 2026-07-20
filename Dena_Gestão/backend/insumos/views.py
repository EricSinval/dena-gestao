from decimal import Decimal

from django.contrib import messages
from django.db import models, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CategoriaMateriaPrimaForm,
    MateriaPrimaForm,
    MovimentacaoMateriaPrimaForm,
)
from .models import (
    CategoriaMateriaPrima,
    MateriaPrima,
    MovimentacaoMateriaPrima,
)


def lista_materias_primas(request):
    materias_primas = (
        MateriaPrima.objects
        .select_related("categoria")
        .all()
    )

    busca = request.GET.get("busca", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()
    status = request.GET.get("status", "").strip()
    estoque = request.GET.get("estoque", "").strip()

    if busca:
        materias_primas = materias_primas.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(categoria__nome__icontains=busca)
        )

    if categoria_id:
        materias_primas = materias_primas.filter(
            categoria_id=categoria_id
        )

    if status == "ativo":
        materias_primas = materias_primas.filter(ativo=True)

    elif status == "inativo":
        materias_primas = materias_primas.filter(ativo=False)

    if estoque == "baixo":
        materias_primas = materias_primas.filter(
            quantidade_estoque__lte=models.F("estoque_minimo")
        )

    categorias = CategoriaMateriaPrima.objects.filter(
        ativo=True
    ).order_by("nome")

    contexto = {
        "materias_primas": materias_primas,
        "categorias": categorias,
        "busca": busca,
        "categoria_selecionada": categoria_id,
        "status_selecionado": status,
        "estoque_selecionado": estoque,
    }

    return render(
        request,
        "insumos/lista_materias_primas.html",
        contexto,
    )


def cadastrar_materia_prima(request):
    if request.method == "POST":
        formulario = MateriaPrimaForm(request.POST)

        if formulario.is_valid():
            materia_prima = formulario.save()

            messages.success(
                request,
                (
                    f'A matéria-prima "{materia_prima.nome}" '
                    "foi cadastrada com sucesso."
                ),
            )

            return redirect(
                "insumos:detalhe_materia_prima",
                materia_prima_id=materia_prima.id,
            )

    else:
        formulario = MateriaPrimaForm()

    contexto = {
        "formulario": formulario,
        "titulo": "Cadastrar matéria-prima",
        "texto_botao": "Salvar matéria-prima",
    }

    return render(
        request,
        "insumos/formulario_materia_prima.html",
        contexto,
    )


def detalhe_materia_prima(request, materia_prima_id):
    materia_prima = get_object_or_404(
        MateriaPrima.objects.select_related("categoria"),
        id=materia_prima_id,
    )

    movimentacoes = (
        materia_prima.movimentacoes
        .select_related("usuario")
        .order_by("-data_movimentacao")[:30]
    )

    contexto = {
        "materia_prima": materia_prima,
        "movimentacoes": movimentacoes,
    }

    return render(
        request,
        "insumos/detalhe_materia_prima.html",
        contexto,
    )


def editar_materia_prima(request, materia_prima_id):
    materia_prima = get_object_or_404(
        MateriaPrima,
        id=materia_prima_id,
    )

    if request.method == "POST":
        formulario = MateriaPrimaForm(
            request.POST,
            instance=materia_prima,
        )

        if formulario.is_valid():
            materia_prima = formulario.save()

            messages.success(
                request,
                (
                    f'A matéria-prima "{materia_prima.nome}" '
                    "foi atualizada com sucesso."
                ),
            )

            return redirect(
                "insumos:detalhe_materia_prima",
                materia_prima_id=materia_prima.id,
            )

    else:
        formulario = MateriaPrimaForm(
            instance=materia_prima,
        )

    contexto = {
        "formulario": formulario,
        "materia_prima": materia_prima,
        "titulo": "Editar matéria-prima",
        "texto_botao": "Salvar alterações",
    }

    return render(
        request,
        "insumos/formulario_materia_prima.html",
        contexto,
    )


@require_POST
def alterar_status_materia_prima(request, materia_prima_id):
    materia_prima = get_object_or_404(
        MateriaPrima,
        id=materia_prima_id,
    )

    materia_prima.ativo = not materia_prima.ativo

    materia_prima.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    acao = "reativada" if materia_prima.ativo else "inativada"

    messages.success(
        request,
        (
            f'A matéria-prima "{materia_prima.nome}" '
            f"foi {acao}."
        ),
    )

    return redirect(
        "insumos:detalhe_materia_prima",
        materia_prima_id=materia_prima.id,
    )


def movimentar_materia_prima(request, materia_prima_id):
    materia_prima_visualizada = get_object_or_404(
        MateriaPrima.objects.select_related("categoria"),
        id=materia_prima_id,
    )

    if request.method == "POST":
        formulario = MovimentacaoMateriaPrimaForm(
            request.POST
        )

        if formulario.is_valid():
            tipo = formulario.cleaned_data["tipo"]
            quantidade = formulario.cleaned_data["quantidade"]
            custo_compra = formulario.cleaned_data["custo_unitario"]
            motivo = formulario.cleaned_data["motivo"]

            tipos_entrada = {
                MovimentacaoMateriaPrima.TipoMovimentacao.COMPRA,
                MovimentacaoMateriaPrima.TipoMovimentacao.ENTRADA,
                MovimentacaoMateriaPrima.TipoMovimentacao.DEVOLUCAO,
                MovimentacaoMateriaPrima.TipoMovimentacao.AJUSTE_ENTRADA,
            }

            with transaction.atomic():
                materia_prima = (
                    MateriaPrima.objects
                    .select_for_update()
                    .get(id=materia_prima_id)
                )

                saldo_anterior = materia_prima.quantidade_estoque

                if tipo in tipos_entrada:
                    saldo_resultante = saldo_anterior + quantidade

                else:
                    saldo_resultante = saldo_anterior - quantidade

                    if saldo_resultante < Decimal("0.000"):
                        formulario.add_error(
                            "quantidade",
                            (
                                "A quantidade informada é maior "
                                "que o estoque disponível."
                            ),
                        )

                if not formulario.errors:
                    custo_movimentacao = None

                    if (
                        tipo
                        == MovimentacaoMateriaPrima
                        .TipoMovimentacao.COMPRA
                    ):
                        custo_movimentacao = custo_compra

                        valor_estoque_anterior = (
                            saldo_anterior
                            * materia_prima.custo_unitario
                        )

                        valor_nova_compra = (
                            quantidade
                            * custo_compra
                        )

                        if saldo_resultante > 0:
                            novo_custo_medio = (
                                valor_estoque_anterior
                                + valor_nova_compra
                            ) / saldo_resultante
                        else:
                            novo_custo_medio = custo_compra

                        materia_prima.custo_unitario = (
                            novo_custo_medio.quantize(
                                Decimal("0.0001")
                            )
                        )

                    usuario = None

                    if request.user.is_authenticated:
                        usuario = request.user

                    MovimentacaoMateriaPrima.objects.create(
                        materia_prima=materia_prima,
                        tipo=tipo,
                        quantidade=quantidade,
                        saldo_anterior=saldo_anterior,
                        saldo_resultante=saldo_resultante,
                        custo_unitario_movimentacao=(
                            custo_movimentacao
                        ),
                        motivo=motivo,
                        usuario=usuario,
                    )

                    materia_prima.quantidade_estoque = (
                        saldo_resultante
                    )

                    materia_prima.save(
                        update_fields=[
                            "quantidade_estoque",
                            "custo_unitario",
                            "data_atualizacao",
                        ]
                    )

                    messages.success(
                        request,
                        (
                            "Movimentação registrada com sucesso. "
                            f"Novo saldo: {saldo_resultante} "
                            f"{materia_prima.get_unidade_medida_display()}."
                        ),
                    )

                    return redirect(
                        "insumos:detalhe_materia_prima",
                        materia_prima_id=materia_prima.id,
                    )

    else:
        formulario = MovimentacaoMateriaPrimaForm()

    contexto = {
        "formulario": formulario,
        "materia_prima": materia_prima_visualizada,
    }

    return render(
        request,
        "insumos/movimentar_materia_prima.html",
        contexto,
    )


def cadastrar_categoria(request):
    if request.method == "POST":
        formulario = CategoriaMateriaPrimaForm(request.POST)

        if formulario.is_valid():
            categoria = formulario.save()

            messages.success(
                request,
                (
                    f'A categoria "{categoria.nome}" '
                    "foi cadastrada com sucesso."
                ),
            )

            return redirect(
                "insumos:cadastrar_materia_prima"
            )

    else:
        formulario = CategoriaMateriaPrimaForm()

    contexto = {
        "formulario": formulario,
    }

    return render(
        request,
        "insumos/formulario_categoria.html",
        contexto,
    )