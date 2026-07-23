from decimal import Decimal, ROUND_HALF_UP

from .models import PrecificacaoProduto


CENTAVOS = Decimal("0.01")


def arredondar(valor):
    return Decimal(valor).quantize(
        CENTAVOS,
        rounding=ROUND_HALF_UP,
    )


def calcular_precificacao(
    *,
    produto,
    configuracao,
    tempo_producao_minutos,
    outros_custos,
    tipo_margem,
    valor_margem,
):
    custo_materiais = arredondar(
        produto.custo_materiais
    )

    horas_producao = (
        tempo_producao_minutos
        / Decimal("60")
    )

    custo_mao_obra = arredondar(
        horas_producao
        * configuracao.valor_hora
    )

    custo_fixo_rateado = arredondar(
        configuracao.custo_fixo_por_peca
    )

    custo_base = arredondar(
        custo_materiais
        + custo_mao_obra
        + outros_custos
        + custo_fixo_rateado
    )

    if (
        tipo_margem
        == PrecificacaoProduto.TipoMargem.PERCENTUAL
    ):
        lucro_estimado = arredondar(
            custo_base
            * (valor_margem / Decimal("100"))
        )
    else:
        lucro_estimado = arredondar(
            valor_margem
        )

    subtotal = arredondar(
        custo_base + lucro_estimado
    )

    valor_comissao = arredondar(
        subtotal
        * (
            configuracao.percentual_comissao
            / Decimal("100")
        )
    )

    valor_impostos = arredondar(
        subtotal
        * (
            configuracao.percentual_impostos
            / Decimal("100")
        )
    )

    preco_sugerido = arredondar(
        subtotal
        + valor_comissao
        + valor_impostos
    )

    return {
        "custo_materiais": custo_materiais,
        "custo_mao_obra": custo_mao_obra,
        "custo_fixo_rateado": custo_fixo_rateado,
        "custo_base": custo_base,
        "lucro_estimado": lucro_estimado,
        "valor_comissao": valor_comissao,
        "valor_impostos": valor_impostos,
        "preco_sugerido": preco_sugerido,
    }