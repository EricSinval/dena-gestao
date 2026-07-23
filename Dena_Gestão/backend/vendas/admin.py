from django.contrib import admin

from .models import Cliente, Pedido


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "telefone",
        "email",
        "ativo",
        "data_criacao",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
        "telefone",
        "email",
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_formatado",
        "cliente",
        "tipo_documento",
        "status",
        "valor_total",
        "data_pedido",
        "data_prevista_entrega",
    )

    list_filter = (
        "tipo_documento",
        "status",
        "data_pedido",
    )

    search_fields = (
        "cliente__nome",
        "observacoes",
    )