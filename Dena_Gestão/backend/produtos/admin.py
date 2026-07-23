from django.contrib import admin

from .models import (
    Categoria,
    ComposicaoProduto,
    MovimentacaoEstoque,
    Produto,
    VariacaoProduto,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
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
    )


class VariacaoProdutoInline(admin.TabularInline):
    model = VariacaoProduto
    extra = 1


class ComposicaoProdutoInline(admin.TabularInline):
    model = ComposicaoProduto
    extra = 1


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "tipo_origem",
        "preco_padrao",
        "exibir_custo_total_estimado",
        "possui_bordado",
        "personalizado",
        "ativo",
    )

    list_filter = (
        "categoria",
        "tipo_origem",
        "possui_bordado",
        "personalizado",
        "ativo",
    )

    search_fields = (
        "nome",
        "descricao",
    )

    inlines = [
        VariacaoProdutoInline,
        ComposicaoProdutoInline,
    ]

    @admin.display(
        description="Custo total estimado",
    )
    def exibir_custo_total_estimado(self, produto):
        return f"R$ {produto.custo_total_estimado:.2f}"


@admin.register(VariacaoProduto)
class VariacaoProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_sku",
        "produto",
        "tamanho",
        "cor",
        "modelo",
        "quantidade_estoque",
        "estoque_minimo",
        "exibir_estoque_baixo",
        "ativo",
    )

    list_filter = (
        "ativo",
        "cor",
        "tamanho",
    )

    search_fields = (
        "codigo_sku",
        "produto__nome",
        "cor",
        "modelo",
    )

    @admin.display(
        boolean=True,
        description="Estoque baixo",
    )
    def exibir_estoque_baixo(self, variacao):
        return variacao.estoque_baixo


@admin.register(ComposicaoProduto)
class ComposicaoProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "produto",
        "materia_prima",
        "quantidade_utilizada",
        "percentual_perda",
        "exibir_quantidade_com_perda",
        "exibir_custo_calculado",
        "ativo",
    )

    list_filter = (
        "ativo",
        "materia_prima__categoria",
    )

    search_fields = (
        "produto__nome",
        "materia_prima__nome",
        "observacao",
    )

    @admin.display(
        description="Quantidade com perda",
    )
    def exibir_quantidade_com_perda(self, composicao):
        return f"{composicao.quantidade_com_perda:.3f}"

    @admin.display(
        description="Custo calculado",
    )
    def exibir_custo_calculado(self, composicao):
        return f"R$ {composicao.custo_calculado:.2f}"


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "data_movimentacao",
        "variacao",
        "tipo",
        "quantidade",
        "saldo_anterior",
        "saldo_resultante",
        "usuario",
    )

    list_filter = (
        "tipo",
        "data_movimentacao",
    )

    search_fields = (
        "variacao__codigo_sku",
        "variacao__produto__nome",
        "motivo",
    )

    readonly_fields = (
        "variacao",
        "tipo",
        "quantidade",
        "saldo_anterior",
        "saldo_resultante",
        "motivo",
        "usuario",
        "data_movimentacao",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False