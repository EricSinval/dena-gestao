from django.contrib import admin

from .models import (
    Categoria,
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


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "preco_padrao",
        "custo_estimado",
        "possui_bordado",
        "personalizado",
        "ativo",
    )

    list_filter = (
        "categoria",
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
    ]


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