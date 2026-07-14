from django import forms

from .models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto

        fields = [
            "categoria",
            "nome",
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