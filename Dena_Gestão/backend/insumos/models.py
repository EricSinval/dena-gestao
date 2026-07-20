from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class CategoriaMateriaPrima(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome",
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
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
        verbose_name = "Categoria de matéria-prima"
        verbose_name_plural = "Categorias de matérias-primas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class MateriaPrima(models.Model):
    class UnidadeMedida(models.TextChoices):
        UNIDADE = "UN", "Unidade"
        METRO = "M", "Metro"
        METRO_QUADRADO = "M2", "Metro quadrado"
        QUILOGRAMA = "KG", "Quilograma"
        GRAMA = "G", "Grama"
        LITRO = "L", "Litro"
        MILILITRO = "ML", "Mililitro"
        ROLO = "ROLO", "Rolo"
        PACOTE = "PACOTE", "Pacote"
        CAIXA = "CAIXA", "Caixa"

    categoria = models.ForeignKey(
        CategoriaMateriaPrima,
        on_delete=models.PROTECT,
        related_name="materias_primas",
        verbose_name="Categoria",
    )

    nome = models.CharField(
        max_length=150,
        verbose_name="Nome",
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição",
    )

    unidade_medida = models.CharField(
        max_length=10,
        choices=UnidadeMedida.choices,
        verbose_name="Unidade de medida",
    )

    quantidade_estoque = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000"),
        validators=[
            MinValueValidator(Decimal("0.000")),
        ],
        verbose_name="Quantidade em estoque",
    )

    estoque_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000"),
        validators=[
            MinValueValidator(Decimal("0.000")),
        ],
        verbose_name="Estoque mínimo",
    )

    custo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        validators=[
            MinValueValidator(Decimal("0.0000")),
        ],
        verbose_name="Custo unitário",
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
        verbose_name = "Matéria-prima"
        verbose_name_plural = "Matérias-primas"
        ordering = ["nome"]

        constraints = [
            models.UniqueConstraint(
                fields=["nome", "unidade_medida"],
                name="materia_prima_unica_por_unidade",
            )
        ]

    def __str__(self):
        return (
            f"{self.nome} "
            f"({self.get_unidade_medida_display()})"
        )

    @property
    def estoque_baixo(self):
        return self.quantidade_estoque <= self.estoque_minimo

    @property
    def valor_em_estoque(self):
        return self.quantidade_estoque * self.custo_unitario


class MovimentacaoMateriaPrima(models.Model):
    class TipoMovimentacao(models.TextChoices):
        COMPRA = "COMPRA", "Compra"
        ENTRADA = "ENTRADA", "Entrada manual"
        CONSUMO = "CONSUMO", "Consumo na produção"
        PERDA = "PERDA", "Perda"
        DEVOLUCAO = "DEVOLUCAO", "Devolução"
        AJUSTE_ENTRADA = "AJUSTE_ENTRADA", "Ajuste de entrada"
        AJUSTE_SAIDA = "AJUSTE_SAIDA", "Ajuste de saída"

    materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Matéria-prima",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoMovimentacao.choices,
        verbose_name="Tipo de movimentação",
    )

    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0.001")),
        ],
        verbose_name="Quantidade",
    )

    saldo_anterior = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Saldo anterior",
    )

    saldo_resultante = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Saldo resultante",
    )

    custo_unitario_movimentacao = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.0000")),
        ],
        verbose_name="Custo unitário da movimentação",
    )

    motivo = models.TextField(
        blank=True,
        verbose_name="Motivo ou observação",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movimentacoes_materia_prima",
        verbose_name="Usuário",
    )

    data_movimentacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da movimentação",
    )

    class Meta:
        verbose_name = "Movimentação de matéria-prima"
        verbose_name_plural = "Movimentações de matérias-primas"
        ordering = ["-data_movimentacao"]

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.materia_prima.nome} - "
            f"{self.quantidade}"
        )

    @property
    def movimentacao_entrada(self):
        return self.tipo in {
            self.TipoMovimentacao.COMPRA,
            self.TipoMovimentacao.ENTRADA,
            self.TipoMovimentacao.DEVOLUCAO,
            self.TipoMovimentacao.AJUSTE_ENTRADA,
        }

    @property
    def valor_total(self):
        if self.custo_unitario_movimentacao is None:
            return None

        return (
            self.quantidade
            * self.custo_unitario_movimentacao
        )