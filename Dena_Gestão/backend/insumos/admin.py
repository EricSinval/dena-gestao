from django.contrib import admin

from .models import (
    CategoriaMateriaPrima,
    MateriaPrima,
    MovimentacaoMateriaPrima,
)


@admin.register(CategoriaMateriaPrima)
class CategoriaMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativo",
        "data_criacao",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
        "descricao",
    )


@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "unidade_medida",
        "quantidade_estoque",
        "estoque_minimo",
        "custo_unitario",
        "exibir_valor_estoque",
        "exibir_estoque_baixo",
        "ativo",
    )

    list_filter = (
        "categoria",
        "unidade_medida",
        "ativo",
    )

    search_fields = (
        "nome",
        "descricao",
    )

    readonly_fields = (
        "quantidade_estoque",
        "data_criacao",
        "data_atualizacao",
    )

    @admin.display(
        boolean=True,
        description="Estoque baixo",
    )
    def exibir_estoque_baixo(self, materia_prima):
        return materia_prima.estoque_baixo

    @admin.display(
        description="Valor em estoque",
    )
    def exibir_valor_estoque(self, materia_prima):
        return f"R$ {materia_prima.valor_em_estoque:.2f}"


@admin.register(MovimentacaoMateriaPrima)
class MovimentacaoMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = (
        "data_movimentacao",
        "materia_prima",
        "tipo",
        "quantidade",
        "saldo_anterior",
        "saldo_resultante",
        "custo_unitario_movimentacao",
        "usuario",
    )

    list_filter = (
        "tipo",
        "data_movimentacao",
    )

    search_fields = (
        "materia_prima__nome",
        "motivo",
    )

    readonly_fields = (
        "materia_prima",
        "tipo",
        "quantidade",
        "saldo_anterior",
        "saldo_resultante",
        "custo_unitario_movimentacao",
        "motivo",
        "usuario",
        "data_movimentacao",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False