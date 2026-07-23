from decimal import Decimal, ROUND_HALF_UP

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from produtos.models import Produto


class ConfiguracaoPrecificacao(models.Model):
    nome = models.CharField(
        max_length=100,
        default="Configuração principal",
        verbose_name="Nome",
    )

    salario_mensal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Salário mensal considerado",
    )

    horas_trabalhadas_dia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("8.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Horas trabalhadas por dia",
    )

    dias_trabalhados_semana = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("5.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Dias trabalhados por semana",
    )

    custos_fixos_mensais = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Custos fixos mensais",
    )

    producao_mensal_estimada = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Produção mensal estimada em peças",
    )

    percentual_comissao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Comissão (%)",
    )

    percentual_impostos = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Impostos (%)",
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
        verbose_name = "Configuração de precificação"
        verbose_name_plural = "Configurações de precificação"
        ordering = ["-ativo", "nome"]

    def __str__(self):
        return self.nome

    @property
    def valor_hora(self):
        semanas_mes = Decimal("4.28")

        horas_mensais = (
            self.horas_trabalhadas_dia
            * self.dias_trabalhados_semana
            * semanas_mes
        )

        if horas_mensais <= 0:
            return Decimal("0.00")

        return (
            self.salario_mensal / horas_mensais
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @property
    def custo_fixo_por_peca(self):
        if self.producao_mensal_estimada <= 0:
            return Decimal("0.00")

        return (
            self.custos_fixos_mensais
            / Decimal(self.producao_mensal_estimada)
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )


class PrecificacaoProduto(models.Model):
    class TipoMargem(models.TextChoices):
        PERCENTUAL = "PERCENTUAL", "Percentual sobre o custo"
        VALOR_FIXO = "VALOR_FIXO", "Valor fixo"

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="precificacoes",
        verbose_name="Produto",
    )

    configuracao = models.ForeignKey(
        ConfiguracaoPrecificacao,
        on_delete=models.PROTECT,
        related_name="precificacoes",
        verbose_name="Configuração utilizada",
    )

    tempo_producao_minutos = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Tempo de produção em minutos",
    )

    outros_custos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Outros custos",
    )

    tipo_margem = models.CharField(
        max_length=20,
        choices=TipoMargem.choices,
        default=TipoMargem.PERCENTUAL,
        verbose_name="Tipo de margem",
    )

    valor_margem = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Margem desejada",
    )

    custo_materiais = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Custo dos materiais",
    )

    custo_mao_obra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Custo da mão de obra",
    )

    custo_fixo_rateado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Custo fixo rateado",
    )

    custo_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Custo base",
    )

    lucro_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Lucro estimado",
    )

    valor_comissao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Comissão",
    )

    valor_impostos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Impostos",
    )

    preco_sugerido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Preço sugerido",
    )

    observacao = models.TextField(
        blank=True,
        verbose_name="Observação",
    )

    data_calculo = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do cálculo",
    )

    class Meta:
        verbose_name = "Precificação de produto"
        verbose_name_plural = "Precificações de produtos"
        ordering = ["-data_calculo"]

    def __str__(self):
        return (
            f"{self.produto.nome} - "
            f"R$ {self.preco_sugerido}"
        )