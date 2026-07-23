from decimal import Decimal

from django import forms

from .models import (
    ConfiguracaoPrecificacao,
    PrecificacaoProduto,
)


class ConfiguracaoPrecificacaoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoPrecificacao

        fields = [
            "nome",
            "salario_mensal",
            "horas_trabalhadas_dia",
            "dias_trabalhados_semana",
            "custos_fixos_mensais",
            "producao_mensal_estimada",
            "percentual_comissao",
            "percentual_impostos",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "salario_mensal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                }
            ),
            "horas_trabalhadas_dia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "8,00",
                }
            ),
            "dias_trabalhados_semana": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "5,00",
                }
            ),
            "custos_fixos_mensais": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                }
            ),
            "producao_mensal_estimada": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "percentual_comissao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                }
            ),
            "percentual_impostos": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "inputmode": "decimal",
                    "placeholder": "0,00",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class PrecificacaoProdutoForm(forms.Form):
    configuracao = forms.ModelChoiceField(
        queryset=ConfiguracaoPrecificacao.objects.none(),
        label="Configuração de precificação",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    tempo_producao_minutos = forms.DecimalField(
        min_value=Decimal("0.00"),
        max_digits=8,
        decimal_places=2,
        localize=True,
        label="Tempo de produção em minutos",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",
                "placeholder": "0,00",
            }
        ),
    )

    outros_custos = forms.DecimalField(
        min_value=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        localize=True,
        initial=Decimal("0.00"),
        label="Outros custos",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",
                "placeholder": "0,00",
            }
        ),
    )

    tipo_margem = forms.ChoiceField(
        choices=PrecificacaoProduto.TipoMargem.choices,
        label="Tipo de margem",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    valor_margem = forms.DecimalField(
        min_value=Decimal("0.00"),
        max_digits=12,
        decimal_places=2,
        localize=True,
        label="Margem desejada",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",
                "placeholder": "0,00",
            }
        ),
    )

    observacao = forms.CharField(
        required=False,
        label="Observação",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["configuracao"].queryset = (
            ConfiguracaoPrecificacao.objects
            .filter(ativo=True)
            .order_by("nome")
        )