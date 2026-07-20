from django import forms

from .models import MovimentacaoEstoque, Produto, VariacaoProduto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto

        fields = [
            "categoria",
            "nome",
            "tipo_origem",
            "descricao",
            "preco_padrao",
            "custo_estimado",
            "personalizado",
            "possui_bordado",
            "imagem",
            "ativo",
        ]

        widgets = {
            "categoria": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Digite o nome do produto",
                }
            ),
            "tipo_origem": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descreva o produto",
                    "rows": 4,
                }
            ),
            "preco_padrao": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0,00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "custo_estimado": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0,00",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "personalizado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "possui_bordado": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
            "imagem": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class VariacaoProdutoForm(forms.ModelForm):
    class Meta:
        model = VariacaoProduto

        fields = [
            "tamanho",
            "cor",
            "modelo",
            "codigo_sku",
            "estoque_minimo",
            "ativo",
        ]

        widgets = {
            "tamanho": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: P, M, G, GG ou 38",
                }
            ),
            "cor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Azul-marinho",
                }
            ),
            "modelo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Colégio Dena",
                }
            ),
            "codigo_sku": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: CAM-ESC-AZM-M",
                }
            ),
            "estoque_minimo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_codigo_sku(self):
        codigo_sku = self.cleaned_data["codigo_sku"]

        return codigo_sku.strip().upper()


class MovimentacaoEstoqueForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=MovimentacaoEstoque.TipoMovimentacao.choices,
        label="Tipo de movimentação",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    quantidade = forms.IntegerField(
        min_value=1,
        label="Quantidade",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Digite a quantidade",
            }
        ),
    )

    motivo = forms.CharField(
        required=False,
        label="Motivo ou observação",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": (
                    "Ex.: venda realizada, material perdido, "
                    "correção de inventário..."
                ),
            }
        ),
    )