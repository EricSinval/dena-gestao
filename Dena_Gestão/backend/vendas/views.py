from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ClienteForm, PedidoForm
from .models import Cliente, Pedido


def lista_clientes(request):
    clientes = Cliente.objects.all()

    busca = request.GET.get("busca", "").strip()
    status = request.GET.get("status", "").strip()

    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(email__icontains=busca)
        )

    if status == "ativo":
        clientes = clientes.filter(ativo=True)

    elif status == "inativo":
        clientes = clientes.filter(ativo=False)

    contexto = {
        "clientes": clientes,
        "busca": busca,
        "status_selecionado": status,
    }

    return render(
        request,
        "vendas/lista_clientes.html",
        contexto,
    )


def cadastrar_cliente(request):
    if request.method == "POST":
        formulario = ClienteForm(request.POST)

        if formulario.is_valid():
            cliente = formulario.save()

            messages.success(
                request,
                f'O cliente "{cliente.nome}" foi cadastrado.',
            )

            return redirect(
                "vendas:detalhe_cliente",
                cliente_id=cliente.id,
            )

    else:
        formulario = ClienteForm()

    contexto = {
        "formulario": formulario,
        "titulo": "Cadastrar cliente",
        "texto_botao": "Salvar cliente",
    }

    return render(
        request,
        "vendas/formulario_cliente.html",
        contexto,
    )


def detalhe_cliente(request, cliente_id):
    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
    )

    pedidos = cliente.pedidos.all()[:20]

    contexto = {
        "cliente": cliente,
        "pedidos": pedidos,
    }

    return render(
        request,
        "vendas/detalhe_cliente.html",
        contexto,
    )


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
    )

    if request.method == "POST":
        formulario = ClienteForm(
            request.POST,
            instance=cliente,
        )

        if formulario.is_valid():
            cliente = formulario.save()

            messages.success(
                request,
                f'O cliente "{cliente.nome}" foi atualizado.',
            )

            return redirect(
                "vendas:detalhe_cliente",
                cliente_id=cliente.id,
            )

    else:
        formulario = ClienteForm(
            instance=cliente,
        )

    contexto = {
        "formulario": formulario,
        "cliente": cliente,
        "titulo": "Editar cliente",
        "texto_botao": "Salvar alterações",
    }

    return render(
        request,
        "vendas/formulario_cliente.html",
        contexto,
    )


@require_POST
def alterar_status_cliente(request, cliente_id):
    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
    )

    cliente.ativo = not cliente.ativo

    cliente.save(
        update_fields=[
            "ativo",
            "data_atualizacao",
        ]
    )

    acao = "reativado" if cliente.ativo else "inativado"

    messages.success(
        request,
        f'O cliente "{cliente.nome}" foi {acao}.',
    )

    return redirect(
        "vendas:detalhe_cliente",
        cliente_id=cliente.id,
    )


def lista_pedidos(request):
    pedidos = (
        Pedido.objects
        .select_related("cliente")
        .all()
    )

    busca = request.GET.get("busca", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    status = request.GET.get("status", "").strip()

    if busca:
        pedidos = pedidos.filter(
            Q(cliente__nome__icontains=busca)
            | Q(observacoes__icontains=busca)
        )

    if tipo:
        pedidos = pedidos.filter(tipo_documento=tipo)

    if status:
        pedidos = pedidos.filter(status=status)

    contexto = {
        "pedidos": pedidos,
        "busca": busca,
        "tipo_selecionado": tipo,
        "status_selecionado": status,
        "tipos": Pedido.TipoDocumento.choices,
        "status_disponiveis": Pedido.StatusPedido.choices,
    }

    return render(
        request,
        "vendas/lista_pedidos.html",
        contexto,
    )


def cadastrar_pedido(request):
    if request.method == "POST":
        formulario = PedidoForm(request.POST)

        if formulario.is_valid():
            pedido = formulario.save()

            messages.success(
                request,
                (
                    f'{pedido.get_tipo_documento_display()} '
                    f'"{pedido.numero_formatado}" criado.'
                ),
            )

            return redirect(
                "vendas:detalhe_pedido",
                pedido_id=pedido.id,
            )

    else:
        formulario = PedidoForm(
            initial={
                "tipo_documento": Pedido.TipoDocumento.ORCAMENTO,
                "status": Pedido.StatusPedido.ORCAMENTO,
            }
        )

    contexto = {
        "formulario": formulario,
        "titulo": "Novo orçamento ou pedido",
        "texto_botao": "Salvar",
    }

    return render(
        request,
        "vendas/formulario_pedido.html",
        contexto,
    )


def detalhe_pedido(request, pedido_id):
    pedido = get_object_or_404(
        Pedido.objects.select_related("cliente"),
        id=pedido_id,
    )

    return render(
        request,
        "vendas/detalhe_pedido.html",
        {
            "pedido": pedido,
        },
    )