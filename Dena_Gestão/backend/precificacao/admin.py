from django.contrib import admin

from .models import (
    ConfiguracaoPrecificacao,
    PrecificacaoProduto,
)


@admin.register(ConfiguracaoPrecificacao)
class ConfiguracaoPrecificacaoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "salario_mensal",
        "horas_trabalhadas_dia",
        "dias_trabalhados_semana",
        "custos_fixos_mensais",
        "producao_mensal_estimada",
        "percentual_comissao",
        "percentual_impostos",
        "ativo",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
    )


@admin.register(PrecificacaoProduto)
class PrecificacaoProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "configuracao",
        "data_calculo",
        "custo_materiais",
        "custo_mao_obra",
        "custo_base",
        "lucro_estimado",
        "preco_sugerido",
    )

    list_filter = (
        "configuracao",
        "tipo_margem",
        "data_calculo",
    )

    search_fields = (
        "produto__nome",
        "configuracao__nome",
        "observacao",
    )

    readonly_fields = (
        "produto",
        "configuracao",
        "tempo_producao_minutos",
        "outros_custos",
        "tipo_margem",
        "valor_margem",
        "custo_materiais",
        "custo_mao_obra",
        "custo_fixo_rateado",
        "custo_base",
        "lucro_estimado",
        "valor_comissao",
        "valor_impostos",
        "preco_sugerido",
        "observacao",
        "data_calculo",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False