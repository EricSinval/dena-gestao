from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from insumos.models import MateriaPrima


class Categoria(models.Model):
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
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    class TipoOrigem(models.TextChoices):
        FABRICACAO_PROPRIA = (
            "FABRICACAO_PROPRIA",
            "Fabricação própria",
        )

        REVENDA = (
            "REVENDA",
            "Revenda",
        )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
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

    tipo_origem = models.CharField(
        max_length=30,
        choices=TipoOrigem.choices,
        default=TipoOrigem.FABRICACAO_PROPRIA,
        verbose_name="Tipo de origem",
    )

    preco_padrao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
        verbose_name="Preço padrão",
    )

    custo_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
        default=Decimal("0.00"),
        verbose_name="Custo estimado",
    )

    personalizado = models.BooleanField(
        default=False,
        verbose_name="Produto personalizado",
    )

    possui_bordado = models.BooleanField(
        default=False,
        verbose_name="Possui bordado",
    )

    imagem = models.ImageField(
        upload_to="produtos/",
        blank=True,
        null=True,
        verbose_name="Imagem de referência",
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
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    @property
    def custo_materiais(self):
        total = Decimal("0.00")

        composicoes = self.composicoes.filter(
            ativo=True,
        ).select_related(
            "materia_prima",
        )

        for composicao in composicoes:
            total += composicao.custo_calculado

        return total

    @property
    def custo_total_estimado(self):
        if (
            self.tipo_origem
            == self.TipoOrigem.FABRICACAO_PROPRIA
        ):
            return self.custo_materiais

        return self.custo_estimado

    @property
    def lucro_estimado(self):
        return (
            self.preco_padrao
            - self.custo_total_estimado
    )

    def __str__(self):
        return self.nome


class VariacaoProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="variacoes",
        verbose_name="Produto",
    )

    tamanho = models.CharField(
        max_length=20,
        verbose_name="Tamanho",
    )

    cor = models.CharField(
        max_length=50,
        verbose_name="Cor",
    )

    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modelo",
    )

    codigo_sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código SKU",
    )

    quantidade_estoque = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade em estoque",
    )

    estoque_minimo = models.PositiveIntegerField(
        default=0,
        verbose_name="Estoque mínimo",
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
        verbose_name = "Variação de produto"
        verbose_name_plural = "Variações de produtos"
        ordering = [
            "produto__nome",
            "cor",
            "tamanho",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "produto",
                    "tamanho",
                    "cor",
                    "modelo",
                ],
                name="variacao_unica_por_produto",
            ),
        ]

    @property
    def estoque_baixo(self):
        return self.quantidade_estoque <= self.estoque_minimo

    def __str__(self):
        modelo = f" - {self.modelo}" if self.modelo else ""

        return (
            f"{self.produto.nome} - "
            f"{self.cor} - "
            f"{self.tamanho}"
            f"{modelo}"
        )


class MovimentacaoEstoque(models.Model):
    class TipoMovimentacao(models.TextChoices):
        ENTRADA = (
            "ENTRADA",
            "Entrada",
        )

        SAIDA_VENDA = (
            "SAIDA_VENDA",
            "Saída por venda",
        )

        PERDA = (
            "PERDA",
            "Perda",
        )

        DEVOLUCAO = (
            "DEVOLUCAO",
            "Devolução",
        )

        PRODUCAO = (
            "PRODUCAO",
            "Produção concluída",
        )

        AJUSTE_ENTRADA = (
            "AJUSTE_ENTRADA",
            "Ajuste de entrada",
        )

        AJUSTE_SAIDA = (
            "AJUSTE_SAIDA",
            "Ajuste de saída",
        )

    variacao = models.ForeignKey(
        VariacaoProduto,
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Variação",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TipoMovimentacao.choices,
        verbose_name="Tipo de movimentação",
    )

    quantidade = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="Quantidade",
    )

    saldo_anterior = models.PositiveIntegerField(
        verbose_name="Saldo anterior",
    )

    saldo_resultante = models.PositiveIntegerField(
        verbose_name="Saldo resultante",
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
        related_name="movimentacoes_estoque",
        verbose_name="Usuário",
    )

    data_movimentacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da movimentação",
    )

    class Meta:
        verbose_name = "Movimentação de estoque"
        verbose_name_plural = "Movimentações de estoque"
        ordering = [
            "-data_movimentacao",
        ]

    @property
    def movimentacao_entrada(self):
        return self.tipo in {
            self.TipoMovimentacao.ENTRADA,
            self.TipoMovimentacao.DEVOLUCAO,
            self.TipoMovimentacao.PRODUCAO,
            self.TipoMovimentacao.AJUSTE_ENTRADA,
        }

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.variacao.codigo_sku} - "
            f"{self.quantidade}"
        )


class ComposicaoProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="composicoes",
        verbose_name="Produto",
    )

    materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.PROTECT,
        related_name="composicoes_produtos",
        verbose_name="Matéria-prima",
    )

    quantidade_utilizada = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[
            MinValueValidator(
                Decimal("0.001"),
            ),
        ],
        verbose_name="Quantidade utilizada",
    )

    percentual_perda = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
        verbose_name="Perda prevista (%)",
    )

    observacao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Observação",
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
        verbose_name = "Composição do produto"
        verbose_name_plural = "Composições dos produtos"
        ordering = [
            "materia_prima__nome",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "produto",
                    "materia_prima",
                ],
                name="materia_prima_unica_por_produto",
            ),
        ]

    @property
    def quantidade_com_perda(self):
        percentual = (
            self.percentual_perda
            / Decimal("100")
        )

        return (
            self.quantidade_utilizada
            * (Decimal("1") + percentual)
        )

    @property
    def custo_calculado(self):
        return (
            self.quantidade_com_perda
            * self.materia_prima.custo_unitario
        )

    def __str__(self):
        return (
            f"{self.produto.nome} - "
            f"{self.materia_prima.nome}"
        )