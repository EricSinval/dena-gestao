from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Cliente(models.Model):
    nome = models.CharField(
        max_length=150,
        verbose_name="Nome",
    )

    telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone",
    )

    email = models.EmailField(
        blank=True,
        verbose_name="E-mail",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação",
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última atualização",
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class TipoDocumento(models.TextChoices):
        ORCAMENTO = "ORCAMENTO", "Orçamento"
        PEDIDO = "PEDIDO", "Pedido"

    class StatusPedido(models.TextChoices):
        ORCAMENTO = "ORCAMENTO", "Orçamento"
        AGUARDANDO_APROVACAO = (
            "AGUARDANDO_APROVACAO",
            "Aguardando aprovação",
        )
        APROVADO = "APROVADO", "Aprovado"
        EM_PRODUCAO = "EM_PRODUCAO", "Em produção"
        AGUARDANDO_ENTREGA = (
            "AGUARDANDO_ENTREGA",
            "Aguardando retirada ou entrega",
        )
        CONCLUIDO = "CONCLUIDO", "Concluído"
        CANCELADO = "CANCELADO", "Cancelado"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
        verbose_name="Cliente",
    )

    tipo_documento = models.CharField(
        max_length=20,
        choices=TipoDocumento.choices,
        default=TipoDocumento.ORCAMENTO,
        verbose_name="Tipo",
    )

    status = models.CharField(
        max_length=30,
        choices=StatusPedido.choices,
        default=StatusPedido.ORCAMENTO,
        verbose_name="Status",
    )

    data_pedido = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação",
    )

    data_prevista_entrega = models.DateField(
        blank=True,
        null=True,
        verbose_name="Previsão de entrega",
    )

    valor_bruto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor bruto",
    )

    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Desconto",
    )

    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor total",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última atualização",
    )

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-data_pedido"]

    def __str__(self):
        return f"{self.get_tipo_documento_display()} #{self.id}"

    @property
    def numero_formatado(self):
        if not self.id:
            return "Novo"

        prefixo = (
            "ORC"
            if self.tipo_documento == self.TipoDocumento.ORCAMENTO
            else "PED"
        )

        return f"{prefixo}-{self.id:05d}"