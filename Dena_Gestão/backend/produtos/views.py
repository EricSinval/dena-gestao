from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render

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
    }

    return render(
        request,
        "produtos/formulario_produto.html",
        contexto,
    )