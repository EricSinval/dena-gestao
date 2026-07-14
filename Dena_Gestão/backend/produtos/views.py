from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProdutoForm
from .models import Categoria, Produto


def lista_produtos(request):
    produtos = Produto.objects.select_related("categoria").all()

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
        produtos = produtos.filter(categoria_id=categoria_id)

    if status == "ativo":
        produtos = produtos.filter(ativo=True)
    elif status == "inativo":
        produtos = produtos.filter(ativo=False)

    categorias = Categoria.objects.filter(ativo=True).order_by("nome")

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
                f'O produto "{produto.nome}" foi cadastrado com sucesso.',
            )

            return redirect("produtos:lista_produtos")

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
        Produto.objects.select_related("categoria").prefetch_related(
            "variacoes"
        ),
        id=produto_id,
    )

    contexto = {
        "produto": produto,
        "variacoes": produto.variacoes.all(),
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
                f'O produto "{produto.nome}" foi atualizado com sucesso.',
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
        mensagem = f'O produto "{produto.nome}" foi reativado.'
    else:
        mensagem = f'O produto "{produto.nome}" foi inativado.'

    messages.success(
        request,
        mensagem,
    )

    return redirect(
        "produtos:detalhe_produto",
        produto_id=produto.id,
    )