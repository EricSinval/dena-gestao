from django import forms

from .models import Cliente, Pedido


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

        fields = [
            "nome",
            "telefone",
            "email",
            "observacoes",
            "ativo",
        ]

        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome completo",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(11) 99999-9999",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "cliente@email.com",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Informações adicionais",
                }
            ),
            "ativo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido

        fields = [
            "cliente",
            "tipo_documento",
            "status",
            "data_prevista_entrega",
            "observacoes",
        ]

        widgets = {
            "cliente": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "tipo_documento": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "data_prevista_entrega": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Referências, prazo combinado, "
                        "informações recebidas pelo WhatsApp..."
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cliente"].queryset = (
            Cliente.objects
            .filter(ativo=True)
            .order_by("nome")
        )