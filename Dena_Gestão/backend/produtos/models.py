from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


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

    preco_padrao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Preço padrão",
    )

    custo_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
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
        ordering = ["produto__nome", "cor", "tamanho"]

        constraints = [
            models.UniqueConstraint(
                fields=["produto", "tamanho", "cor", "modelo"],
                name="variacao_unica_por_produto",
            )
        ]

    def __str__(self):
        modelo = f" - {self.modelo}" if self.modelo else ""

        return (
            f"{self.produto.nome} - "
            f"{self.cor} - {self.tamanho}{modelo}"
        )

    @property
    def estoque_baixo(self):
        return self.quantidade_estoque <= self.estoque_minimo