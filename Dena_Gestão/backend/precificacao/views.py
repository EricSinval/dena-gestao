from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from produtos.models import Produto

from .forms import (
    ConfiguracaoPrecificacaoForm,
    PrecificacaoProdutoForm,
)
from .models import (
    ConfiguracaoPrecificacao,
    PrecificacaoProduto,
)
from .services import calcular_precificacao
from django.views.decorators.http import require_POST

def cadastrar_configuracao(request):
    if request.method == "POST":
        formulario = ConfiguracaoPrecificacaoForm(
            request.POST
        )

        if formulario.is_valid():
            configuracao = formulario.save()

            messages.success(
                request,
                (
                    f'A configuração "{configuracao.nome}" '
                    "foi cadastrada com sucesso."
                ),
            )

            return redirect(
                "precificacao:lista_configuracoes"
            )

    else:
        formulario = ConfiguracaoPrecificacaoForm()

    contexto = {
        "formulario": formulario,
        "titulo": "Nova configuração de precificação",
        "texto_botao": "Salvar configuração",
    }

    return render(
        request,
        "precificacao/formulario_configuracao.html",
        contexto,
    )


def lista_configuracoes(request):
    configuracoes = (
        ConfiguracaoPrecificacao.objects.all()
    )

    return render(
        request,
        "precificacao/lista_configuracoes.html",
        {
            "configuracoes": configuracoes,
        },
    )


def calcular_preco_produto(request, produto_id):
    produto = get_object_or_404(
        Produto,
        id=produto_id,
    )

    if request.method == "POST":
        formulario = PrecificacaoProdutoForm(
            request.POST
        )

        if formulario.is_valid():
            dados = formulario.cleaned_data

            resultado = calcular_precificacao(
                produto=produto,
                configuracao=dados["configuracao"],
                tempo_producao_minutos=(
                    dados["tempo_producao_minutos"]
                ),
                outros_custos=dados["outros_custos"],
                tipo_margem=dados["tipo_margem"],
                valor_margem=dados["valor_margem"],
            )

            precificacao = (
                PrecificacaoProduto.objects.create(
                    produto=produto,
                    configuracao=dados["configuracao"],
                    tempo_producao_minutos=(
                        dados["tempo_producao_minutos"]
                    ),
                    outros_custos=dados["outros_custos"],
                    tipo_margem=dados["tipo_margem"],
                    valor_margem=dados["valor_margem"],
                    observacao=dados["observacao"],
                    **resultado,
                )
            )

            messages.success(
                request,
                "Precificação calculada com sucesso.",
            )

            return redirect(
                "precificacao:detalhe_precificacao",
                precificacao_id=precificacao.id,
            )

    else:
        formulario = PrecificacaoProdutoForm()

    return render(
        request,
        "precificacao/calcular_precificacao.html",
        {
            "produto": produto,
            "formulario": formulario,
        },
    )


def detalhe_precificacao(request, precificacao_id):
    precificacao = get_object_or_404(
        PrecificacaoProduto.objects.select_related(
            "produto",
            "configuracao",
        ),
        id=precificacao_id,
    )

    return render(
        request,
        "precificacao/detalhe_precificacao.html",
        {
            "precificacao": precificacao,
        },
    )

@require_POST
def aplicar_preco_sugerido(request, precificacao_id):
    precificacao = get_object_or_404(
        PrecificacaoProduto.objects.select_related(
            "produto",
        ),
        id=precificacao_id,
    )

    produto = precificacao.produto

    produto.preco_padrao = precificacao.preco_sugerido

    produto.save(
        update_fields=[
            "preco_padrao",
            "data_atualizacao",
        ]
    )

    messages.success(
        request,
        (
            f'O preço padrão do produto "{produto.nome}" '
            f"foi atualizado para "
            f"R$ {precificacao.preco_sugerido:.2f}.'"
        ),
    )

    return redirect(
        "produtos:detalhe_produto",
        produto_id=produto.id,
    )