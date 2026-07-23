from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from precificacao.models import PrecificacaoProduto

from .forms import (
    ComposicaoProdutoForm,
    MovimentacaoEstoqueForm,
    ProdutoForm,
    VariacaoProdutoForm,
)
from .models import (
    Categoria,
    ComposicaoProduto,
    MovimentacaoEstoque,
    Produto,
    VariacaoProduto,
)


def lista_produtos(request):
    produtos = Produto.objects.select_related(
        "categoria",
    ).all()

    busca = request.GET.get("busca", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()
    status = request.GET.get("status", "").strip()

    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(categoria__nome__icontains=busca)
        )

    if categoria_id:
        produtos = produtos.filter(
            categoria_id=categoria_id,
        )

    if status == "ativo":
        produtos = produtos.filter(
            ativo=True,
        )

    elif status == "inativo":
        produtos = produtos.filter(
            ativo=False,
        )

    categorias = Categoria.objects.filter(
        ativo=True,
    ).order_by(
        "nome",
    )

    contexto = {
        "produtos": produtos,
        "categorias": categorias,
        "busca": busca,
        "categoria_selecionada": categoria_id,
        "status_selecionado": status,
    }

    return render(
        request,
        "produtos/lista_produtos.html",
        contexto,
    )


def cadastrar_produto(request):
    if request.method == "POST":
        formulario = ProdutoForm(
            request.POST,
            request.FILES,
        )

        if formulario.is_valid():
            produto = formulario.save()

            messages.success(
                request,
                (
                    f'O produto "{produto.nome}" '
                    "foi cadastrado com sucesso."
                ),
            )

            return redirect(
                "produtos:lista_produtos",
            )

    else:
        formulario = ProdutoForm()

    contexto = {
        "formulario": formulario,
        "titulo": "Cadastrar produto",
        "texto_botao": "Salvar produto",
    }

    return render(
        request,
        "produtos/formulario_produto.html",
        contexto,
    )


def detalhe_produto(request, produto_id):
    produto = get_object_or_404(
        Produto.objects.select_related(
            "categoria",
        ).prefetch_related(
            "variacoes",
            "variacoes__movimentacoes",
            "composicoes",
            "composicoes__materia_prima",
            "composicoes__materia_prima__categoria",
        ),
        id=produto_id,
    )

    variacoes = produto.variacoes.order_by(
        "cor",
        "tamanho",
        "modelo",
    )

    movimentacoes = (
        MovimentacaoEstoque.objects
        .filter(
            variacao__produto=produto,
        )
        .select_related(
            "variacao",
            "usuario",
        )
        .order_by(
            "-data_movimentacao",
        )[:20]
    )

    composicoes = (
        produto.composicoes
        .select_related(
            "materia_prima",
            "materia_prima__categoria",
        )
        .order_by(
            "materia_prima__nome",
        )
    )

    precificacoes = (
        PrecificacaoProduto.objects
        .filter(
            produto=produto,
        )
        .select_related(
            "configuracao",
        )
        .order_by(
            "-data_calculo",
        )[:20]
    )

    contexto = {
        "produto": produto,
        "variacoes": variacoes,
        "movimentacoes": movimentacoes,
        "composicoes": composicoes,
        "precificacoes": precificacoes,
    }

    return render(
        request,
        "produtos/detalhe_produto.html",
        contexto,
    )


def editar_produto(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id,
    )

    if request.method == "POST":
        formulario = ProdutoForm(
            request.POST,
            request.FILES,
            instance=produto,
        )

        if formulario.is_valid():
            produto = formulario.save()

            messages.success(
                request,
                (
                    f'O produto "{produto.nome}" '
                    "foi atualizado com sucesso."
                ),
            )

            return redirect(
                "produtos:detalhe_produto",
                produto_id=produto.id,
            )

    else:
        formulario = ProdutoForm(
            instance=produto,
        )

    contexto = {
        "formulario": formulario,
        "titulo": "Editar produto",
        "produto": produto,
        "texto_botao": "Salvar alterações",
    }

    return render(
        request,
        "produtos/formulario_produto.html",
        contexto,
    )


@require_POST
def alterar_status_produto(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id,
    )

    produto.ativo = not produto.ativo

    produto.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    if produto.ativo:
        mensagem = (
            f'O produto "{produto.nome}" '
            "foi reativado."
        )

    else:
        mensagem = (
            f'O produto "{produto.nome}" '
            "foi inativado."
        )

    messages.success(
        request,
        mensagem,
    )

    return redirect(
        "produtos:detalhe_produto",
        produto_id=produto.id,
    )


def cadastrar_variacao(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id,
    )

    if request.method == "POST":
        formulario = VariacaoProdutoForm(
            request.POST,
        )

        if formulario.is_valid():
            dados = formulario.cleaned_data

            variacao_existente = VariacaoProduto.objects.filter(
                produto=produto,
                tamanho__iexact=dados["tamanho"],
                cor__iexact=dados["cor"],
                modelo__iexact=dados["modelo"],
            ).exists()

            if variacao_existente:
                formulario.add_error(
                    None,
                    (
                        "Já existe uma variação deste produto "
                        "com o mesmo tamanho, cor e modelo."
                    ),
                )

            else:
                variacao = formulario.save(
                    commit=False,
                )

                variacao.produto = produto
                variacao.save()

                messages.success(
                    request,
                    (
                        f'A variação "{variacao}" '
                        "foi cadastrada com sucesso."
                    ),
                )

                return redirect(
                    "produtos:detalhe_produto",
                    produto_id=produto.id,
                )

    else:
        formulario = VariacaoProdutoForm()

    contexto = {
        "formulario": formulario,
        "produto": produto,
        "titulo": "Cadastrar variação",
        "texto_botao": "Salvar variação",
    }

    return render(
        request,
        "produtos/formulario_variacao.html",
        contexto,
    )


def editar_variacao(request, variacao_id):
    variacao = get_object_or_404(
        VariacaoProduto.objects.select_related(
            "produto",
        ),
        id=variacao_id,
    )

    if request.method == "POST":
        formulario = VariacaoProdutoForm(
            request.POST,
            instance=variacao,
        )

        if formulario.is_valid():
            variacao = formulario.save()

            messages.success(
                request,
                (
                    f'A variação "{variacao}" '
                    "foi atualizada com sucesso."
                ),
            )

            return redirect(
                "produtos:detalhe_produto",
                produto_id=variacao.produto.id,
            )

    else:
        formulario = VariacaoProdutoForm(
            instance=variacao,
        )

    contexto = {
        "formulario": formulario,
        "produto": variacao.produto,
        "variacao": variacao,
        "titulo": "Editar variação",
        "texto_botao": "Salvar alterações",
    }

    return render(
        request,
        "produtos/formulario_variacao.html",
        contexto,
    )


@require_POST
def alterar_status_variacao(request, variacao_id):
    variacao = get_object_or_404(
        VariacaoProduto.objects.select_related(
            "produto",
        ),
        id=variacao_id,
    )

    variacao.ativo = not variacao.ativo

    variacao.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    if variacao.ativo:
        mensagem = (
            f'A variação "{variacao}" '
            "foi reativada."
        )

    else:
        mensagem = (
            f'A variação "{variacao}" '
            "foi inativada."
        )

    messages.success(
        request,
        mensagem,
    )

    return redirect(
        "produtos:detalhe_produto",
        produto_id=variacao.produto.id,
    )


def movimentar_estoque(request, variacao_id):
    variacao_visualizada = get_object_or_404(
        VariacaoProduto.objects.select_related(
            "produto",
            "produto__categoria",
        ),
        id=variacao_id,
    )

    if request.method == "POST":
        formulario = MovimentacaoEstoqueForm(
            request.POST,
        )

        if formulario.is_valid():
            tipo = formulario.cleaned_data["tipo"]
            quantidade = formulario.cleaned_data["quantidade"]
            motivo = formulario.cleaned_data["motivo"]

            tipos_entrada = {
                MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
                MovimentacaoEstoque.TipoMovimentacao.DEVOLUCAO,
                MovimentacaoEstoque.TipoMovimentacao.PRODUCAO,
                MovimentacaoEstoque.TipoMovimentacao.AJUSTE_ENTRADA,
            }

            with transaction.atomic():
                variacao = (
                    VariacaoProduto.objects
                    .select_for_update()
                    .select_related(
                        "produto",
                    )
                    .get(
                        id=variacao_id,
                    )
                )

                saldo_anterior = variacao.quantidade_estoque

                if tipo in tipos_entrada:
                    saldo_resultante = (
                        saldo_anterior
                        + quantidade
                    )

                else:
                    saldo_resultante = (
                        saldo_anterior
                        - quantidade
                    )

                    if saldo_resultante < 0:
                        formulario.add_error(
                            "quantidade",
                            (
                                "A quantidade informada é maior "
                                "que o estoque disponível."
                            ),
                        )

                if not formulario.errors:
                    usuario = None

                    if request.user.is_authenticated:
                        usuario = request.user

                    MovimentacaoEstoque.objects.create(
                        variacao=variacao,
                        tipo=tipo,
                        quantidade=quantidade,
                        saldo_anterior=saldo_anterior,
                        saldo_resultante=saldo_resultante,
                        motivo=motivo,
                        usuario=usuario,
                    )

                    variacao.quantidade_estoque = saldo_resultante

                    variacao.save(
                        update_fields=[
                            "quantidade_estoque",
                            "data_atualizacao",
                        ]
                    )

                    messages.success(
                        request,
                        (
                            "Movimentação registrada com sucesso. "
                            f"Novo estoque: {saldo_resultante}."
                        ),
                    )

                    return redirect(
                        "produtos:detalhe_produto",
                        produto_id=variacao.produto.id,
                    )

    else:
        formulario = MovimentacaoEstoqueForm()

    contexto = {
        "formulario": formulario,
        "variacao": variacao_visualizada,
        "produto": variacao_visualizada.produto,
    }

    return render(
        request,
        "produtos/movimentar_estoque.html",
        contexto,
    )


def cadastrar_composicao(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id,
    )

    if request.method == "POST":
        formulario = ComposicaoProdutoForm(
            request.POST,
            produto=produto,
        )

        if formulario.is_valid():
            composicao = formulario.save(
                commit=False,
            )

            composicao.produto = produto
            composicao.save()

            messages.success(
                request,
                (
                    'A matéria-prima '
                    f'"{composicao.materia_prima.nome}" '
                    "foi adicionada à composição."
                ),
            )

            return redirect(
                "produtos:detalhe_produto",
                produto_id=produto.id,
            )

    else:
        formulario = ComposicaoProdutoForm(
            produto=produto,
        )

    contexto = {
        "formulario": formulario,
        "produto": produto,
        "titulo": "Adicionar matéria-prima",
        "texto_botao": "Adicionar à composição",
    }

    return render(
        request,
        "produtos/formulario_composicao.html",
        contexto,
    )


def editar_composicao(request, composicao_id):
    composicao = get_object_or_404(
        ComposicaoProduto.objects.select_related(
            "produto",
            "materia_prima",
        ),
        id=composicao_id,
    )

    if request.method == "POST":
        formulario = ComposicaoProdutoForm(
            request.POST,
            instance=composicao,
            produto=composicao.produto,
        )

        if formulario.is_valid():
            composicao = formulario.save()

            messages.success(
                request,
                "Item da composição atualizado.",
            )

            return redirect(
                "produtos:detalhe_produto",
                produto_id=composicao.produto.id,
            )

    else:
        formulario = ComposicaoProdutoForm(
            instance=composicao,
            produto=composicao.produto,
        )

    contexto = {
        "formulario": formulario,
        "produto": composicao.produto,
        "composicao": composicao,
        "titulo": "Editar matéria-prima",
        "texto_botao": "Salvar alterações",
    }

    return render(
        request,
        "produtos/formulario_composicao.html",
        contexto,
    )


@require_POST
def alterar_status_composicao(
    request,
    composicao_id,
):
    composicao = get_object_or_404(
        ComposicaoProduto.objects.select_related(
            "produto",
            "materia_prima",
        ),
        id=composicao_id,
    )

    composicao.ativo = not composicao.ativo

    composicao.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    if composicao.ativo:
        acao = "reativado"

    else:
        acao = "inativado"

    messages.success(
        request,
        (
            'O material '
            f'"{composicao.materia_prima.nome}" '
            f"foi {acao} na composição."
        ),
    )

    return redirect(
        "produtos:detalhe_produto",
        produto_id=composicao.produto.id,
    )