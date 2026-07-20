from decimal import Decimal

from django import forms

from .models import (
    CategoriaMateriaPrima,
    MateriaPrima,
    MovimentacaoMateriaPrima,
)


class CategoriaMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = CategoriaMateriaPrima

        fields = [
            "nome",
            "descricao",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: Tecidos",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição da categoria",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima

        fields = [
            "categoria",
            "nome",
            "descricao",
            "unidade_medida",
            "estoque_minimo",
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
                    "placeholder": "Ex.: Malha PV azul-marinho",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Informações adicionais",
                }
            ),
            "unidade_medida": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "estoque_minimo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.001",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class MovimentacaoMateriaPrimaForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=MovimentacaoMateriaPrima.TipoMovimentacao.choices,
        label="Tipo de movimentação",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "id_tipo_movimentacao",
            }
        ),
    )

    quantidade = forms.DecimalField(
        min_value=Decimal("0.001"),
        max_digits=12,
        decimal_places=3,
        label="Quantidade",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0.001",
                "step": "0.001",
                "placeholder": "0,000",
            }
        ),
    )

    custo_unitario = forms.DecimalField(
        required=False,
        min_value=Decimal("0.0000"),
        max_digits=12,
        decimal_places=4,
        label="Custo unitário da compra",
        help_text=(
            "Obrigatório apenas quando o tipo for Compra."
        ),
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.0001",
                "placeholder": "0,0000",
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
                    "Ex.: Compra realizada no fornecedor X, "
                    "consumo na produção de camisetas..."
                ),
            }
        ),
    )

    def clean(self):
        dados = super().clean()

        tipo = dados.get("tipo")
        custo_unitario = dados.get("custo_unitario")

        if (
            tipo
            == MovimentacaoMateriaPrima.TipoMovimentacao.COMPRA
            and custo_unitario is None
        ):
            self.add_error(
                "custo_unitario",
                "Informe o custo unitário da compra.",
            )

        return dados