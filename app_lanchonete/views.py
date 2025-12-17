from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.shortcuts import render
from app_lanchonete import models
from django.contrib import messages


SESSION_KEY = "itens_pedido"

def home(request):
       return render(request, 'home.html')
############################################################################################
def menu_clientes(request):
    return render(request, 'cliente/menu_cliente.html')

def menu_funcionarios(request):
    return render(request, 'funcionario/menu_funcionario.html')

def menu_lanches(request):
    return render(request, 'lanche/menu_lanche.html')

def menu_pedidos(request):
    return render(request, 'pedido/menu_pedido.html')
############################################################################################
def cadastrar_cliente(request):
    return render(request, 'cliente/cadastrar_cliente.html')

def cadastrar_funcionario(request):
    return render(request, 'funcionario/cadastrar_funcionario.html')

def cadastrar_lanche(request):
    return render(request, 'lanche/cadastrar_lanche.html')

def cadastrar_pedido(request):
    return render(request, 'pedido/cadastrar_pedido.html')
############################################################################################
def clientes_cadastrados(request):
    if request.method == 'POST':
        novo_cliente = models.Cliente()
        novo_cliente.nome = request.POST.get('nome_cliente')
        novo_cliente.telefone = request.POST.get('telefone_cliente')
        if novo_cliente.nome and novo_cliente.telefone:
            if not models.Cliente.objects.filter(nome=novo_cliente.nome, telefone=novo_cliente.telefone).exists():
                novo_cliente.save()
    clientes = {
        'clientes': models.Cliente.objects.all()
    }
    return render(request, 'cliente/ver_clientes.html', clientes)

def funcionarios_cadastrados(request):
    if request.method == 'POST':
        novo_funcionario = models.Funcionario()
        novo_funcionario.nome = request.POST.get('nome_funcionario')
        novo_funcionario.especialidade = request.POST.get('especialidade_funcionario')
        if novo_funcionario.nome and novo_funcionario.especialidade:
            if not models.Funcionario.objects.filter(nome=novo_funcionario.nome, especialidade=novo_funcionario.especialidade).exists():
                novo_funcionario.save()
    funcionarios = {
        'funcionarios': models.Funcionario.objects.all()
    }
    return render(request, 'funcionario/ver_funcionarios.html', funcionarios)

def lanches_cadastrados(request):
    if request.method == 'POST':
        novo_lanche = models.Lanche()
        novo_lanche.nome = request.POST.get('nome_lanche')
        novo_lanche.valor = request.POST.get('valor_lanche')
        if novo_lanche.nome and novo_lanche.valor:
            if not models.Lanche.objects.filter(nome=novo_lanche.nome, valor=novo_lanche.valor).exists():
                novo_lanche.save()
    lanches = {
        'lanches': models.Lanche.objects.all()
    }
    return render(request, 'lanche/ver_lanches.html', lanches)








def cadastrar_pedido(request):
    """
    GET: mostra o formulário e os itens temporários da sessão.
    POST com action=add -> adiciona item à sessão.
    POST com action=remove -> remove item pelo índice.
    POST com action=finalize -> cria Pedido, ItemPedido(s) e Pagamento.
    """
    # inicializa a lista na sessão se necessário
    if SESSION_KEY not in request.session:
        request.session[SESSION_KEY] = []

    itens_sessao = request.session.get(SESSION_KEY, [])

    if request.method == "POST":
        action = request.POST.get("action")

        # --- ADICIONAR ITEM à sessão ---
        if action == "add":
            lanche_id = request.POST.get("lanche")
            quantidade_raw = request.POST.get("quantidade", "1")

            if not lanche_id:
                messages.error(request, "Selecione um lanche.")
                return redirect("cadastrar_pedido")

            try:
                quantidade = int(quantidade_raw)
                if quantidade <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Quantidade inválida.")
                return redirect("cadastrar_pedido")

            lanche = get_object_or_404(models.Lanche, id=lanche_id)
            # adiciona o item na sessão (merge se já existir mesmo lanche)
            found = False
            for itm in itens_sessao:
                if itm["lanche_id"] == lanche.id:
                    itm["quantidade"] += quantidade
                    found = True
                    break
            if not found:
                itens_sessao.append({
                    "lanche_id": lanche.id,
                    "nome": lanche.nome,
                    # armazena valor como string pra evitar problemas de serialização
                    "valor": str(lanche.valor),
                    "quantidade": quantidade
                })

            request.session[SESSION_KEY] = itens_sessao
            request.session.modified = True
            messages.success(request, f"{quantidade}x {lanche.nome} adicionados ao pedido.")
            return redirect("cadastrar_pedido")

        # --- REMOVER ITEM da sessão (pelo índice) ---
        elif action == "remove":
            index_raw = request.POST.get("index")
            try:
                index = int(index_raw)
                if 0 <= index < len(itens_sessao):
                    removed = itens_sessao.pop(index)
                    request.session[SESSION_KEY] = itens_sessao
                    request.session.modified = True
                    messages.success(request, f"Removido {removed['nome']} do pedido.")
                else:
                    messages.error(request, "Índice inválido.")
            except (ValueError, TypeError):
                messages.error(request, "Erro ao remover item.")
            return redirect("cadastrar_pedido")

        # --- FINALIZAR: criar pedido + itens + pagamento ---
        elif action == "finalize":
            cliente_id = request.POST.get("cliente")
            funcionario_id = request.POST.get("funcionario")
            data_raw = request.POST.get("data")  # espera YYYY-MM-DD

            if not cliente_id or not funcionario_id:
                messages.error(request, "Cliente e funcionário são obrigatórios.")
                return redirect("cadastrar_pedido")

            if len(itens_sessao) == 0:
                messages.error(request, "Adicione pelo menos um item ao pedido.")
                return redirect("cadastrar_pedido")

            cliente = get_object_or_404(models.Cliente, id=cliente_id)
            funcionario = get_object_or_404(models.Funcionario, id=funcionario_id)

            # data: se vazio, usa hoje
            if not data_raw:
                data = timezone.now().date()
            else:
                try:
                    data = timezone.datetime.strptime(data_raw, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Data inválida.")
                    return redirect("cadastrar_pedido")

            # cria o pedido
            pedido = models.Pedido.objects.create(
                cliente=cliente,
                funcionario=funcionario,
                data=data
            )

            # cria itens e soma total
            total = Decimal("0.00")
            for itm in itens_sessao:
                lanche = get_object_or_404(models.Lanche, id=itm["lanche_id"])
                quantidade = int(itm["quantidade"])
                subtotal = lanche.valor * quantidade
                total += subtotal

                models.ItemPedido.objects.create(
                    pedido=pedido,
                    lanche=lanche,
                    quantidade=quantidade
                )

            # cria pagamento com o total
            models.Pagamento.objects.create(
                pedido=pedido,
                valor=total
            )

            # limpa sessão
            request.session[SESSION_KEY] = []
            request.session.modified = True

            messages.success(request, f"Pedido #{pedido.id} criado com sucesso! Total: R$ {total}")
            return redirect("pedidos_cadastrados")

    # GET ou caso POST tratado já redirecionou
    contexto = {
        "clientes": models.Cliente.objects.all(),
        "funcionarios": models.Funcionario.objects.all(),
        "lanches": models.Lanche.objects.all(),
        "itens_sessao": itens_sessao,
    }
    return render(request, "pedido/cadastrar_pedido.html", contexto)


def pedidos_cadastrados(request):
    pedidos = models.Pedido.objects.all().order_by("-id")
    # Para cada pedido, queremos também os itens e se tem pagamento
    contexto = {
        "pedidos": pedidos,
    }
    return render(request, "pedido/ver_pedidos.html", contexto)


def marcar_pago(request, pedido_id):
    pagamento = get_object_or_404(models.Pagamento, pedido_id=pedido_id)
    pagamento.pago = True
    pagamento.save()
    messages.success(request, "Pagamento confirmado!")
    return redirect("pedidos_cadastrados")
