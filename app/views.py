from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Agendamento, Cliente, Animal
from .forms import AgendamentoForm, ClienteForm, AnimalForm, AtendimentoDetalhadoForm
from django.contrib.auth.decorators import login_required
import json
import datetime # <-- Adicionado para a separação de datas


# Substitua sua função index por esta:
# views.py (Função buscar_pacientes_por_cliente CORRIGIDA)

@login_required
def buscar_pacientes_por_cliente(request, cliente_id):
    """Retorna uma lista de pacientes (id, nome, especie, raca) para o cliente selecionado em formato JSON."""
    
    if not str(cliente_id).isdigit():
        return JsonResponse({"pacientes": []}, status=400)

    try:
        pacientes = Animal.objects.filter(cliente_id=cliente_id).order_by('nome')
    except Exception:
        return JsonResponse({"pacientes": []}, status=500)
    
    # 🎯 MUDANÇA AQUI: Incluindo especie e raca no JSON
    pacientes_data = [
        {"id": paciente.id, 
         "nome": f"{paciente.nome} ({paciente.especie})",
         "especie": paciente.especie,  # <-- NOVO DADO
         "raca": paciente.raca or ""   # <-- NOVO DADO (ou string vazia se for null)
        }
        for paciente in pacientes
    ]
    
    return JsonResponse({"pacientes": pacientes_data})

@login_required
def index(request):
    today = datetime.date.today()
    
    # 1. Define as buscas base
    agendamentos_ativos = Agendamento.objects.filter(data__gte=today)
    agendamentos_anteriores = Agendamento.objects.filter(data__lt=today)

    # 2. Pega os valores do formulário de filtro da URL (GET)
    profissional = request.GET.get('profissional', '')
    cliente_nome = request.GET.get('cliente', '')
    animal_nome = request.GET.get('animal', '')
    especie = request.GET.get('especie_filtro', '')
    data = request.GET.get('data', '')
    status = request.GET.get('status', '')

    # 3. Aplica os filtros nas DUAS buscas, se eles existirem
    if profissional:
        agendamentos_ativos = agendamentos_ativos.filter(profissional__icontains=profissional)
        agendamentos_anteriores = agendamentos_anteriores.filter(profissional__icontains=profissional)
    if cliente_nome:
        agendamentos_ativos = agendamentos_ativos.filter(cliente__icontains=cliente_nome)
        agendamentos_anteriores = agendamentos_anteriores.filter(cliente__icontains=cliente_nome)
    if animal_nome:
        agendamentos_ativos = agendamentos_ativos.filter(animal__icontains=animal_nome)
        agendamentos_anteriores = agendamentos_anteriores.filter(animal__icontains=animal_nome)
    if especie:
        agendamentos_ativos = agendamentos_ativos.filter(especie=especie)
        agendamentos_anteriores = agendamentos_anteriores.filter(especie=especie)
    if data:
        agendamentos_ativos = agendamentos_ativos.filter(data=data)
        agendamentos_anteriores = agendamentos_anteriores.filter(data=data)
    if status:
        agendamentos_ativos = agendamentos_ativos.filter(status=status)
        agendamentos_anteriores = agendamentos_anteriores.filter(status=status)

    # 4. Cria um dicionário com os filtros aplicados para devolver ao template
    filtros = {
        'profissional': profissional,
        'cliente': cliente_nome,
        'animal': animal_nome,
        'especie_filtro': especie,
        'data': data,
        'status': status,
    }

    # Ordena os resultados finais
    agendamentos_ativos = agendamentos_ativos.order_by("data", "hora")
    agendamentos_anteriores = agendamentos_anteriores.order_by("-data", "-hora")

    form = AgendamentoForm()
    racas_choices = json.dumps(Agendamento.RACAS_CHOICES)

    return render(request, "index.html", {
        "agendamentos_ativos": agendamentos_ativos, 
        "agendamentos_anteriores": agendamentos_anteriores,
        "form": form,
        "racas_choices": racas_choices,
        "filtros": filtros, # <-- DEVOLVE OS FILTROS PARA O TEMPLATE
    })
@login_required
def atendimentos_realizados(request):
    # 1. Começa com a busca base por atendimentos realizados
    agendamentos = Agendamento.objects.filter(status="realizado")

    # 2. Pega os valores do formulário de filtro da URL (GET)
    profissional = request.GET.get('profissional', '')
    cliente_nome = request.GET.get('cliente', '')
    animal_nome = request.GET.get('animal', '')
    especie = request.GET.get('especie_filtro', '')
    data = request.GET.get('data', '')

    # 3. Aplica os filtros na busca, um por um, se eles existirem
    if profissional:
        # __icontains faz uma busca case-insensitive que "contém" o texto
        agendamentos = agendamentos.filter(profissional__icontains=profissional)
    if cliente_nome:
        agendamentos = agendamentos.filter(cliente__icontains=cliente_nome)
    if animal_nome:
        agendamentos = agendamentos.filter(animal__icontains=animal_nome)
    if especie:
        agendamentos = agendamentos.filter(especie=especie)
    if data:
        agendamentos = agendamentos.filter(data=data)

    # 4. Cria um dicionário com os filtros aplicados para devolver ao template
    filtros = {
        'profissional': profissional,
        'cliente': cliente_nome,
        'animal': animal_nome,
        'especie_filtro': especie,
        'data': data
    }
    
    # Ordena o resultado final
    agendamentos = agendamentos.order_by("-data", "-hora")
    form = AgendamentoForm()

    return render(request, "atendimentos_realizados.html", {
        "agendamentos": agendamentos,
        "form": form,
        "filtros": filtros, # <-- DEVOLVE OS FILTROS PARA O TEMPLATE
    })

@login_required
def detalhar_atendimento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk, status="realizado")

    if request.method == "POST":
        form = AtendimentoDetalhadoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            return redirect("atendimentos_realizados")
    else:
        form = AtendimentoDetalhadoForm(instance=agendamento)

    return render(request, "detalhar_atendimento.html", {
        "agendamento": agendamento,
        "form": form,
    })


@login_required
def editar_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)

    if agendamento.usuario != request.user:
        return JsonResponse({"success": False, "error": "Você não tem permissão para editar este agendamento."}, status=403)

    if request.method == "POST":
        form = AgendamentoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})

    return JsonResponse({
        "cliente": agendamento.cliente.id,
        "animal": agendamento.animal.id,
        "tipo_atendimento": agendamento.tipo_atendimento,
        "profissional": agendamento.profissional,
        "especie": getattr(agendamento, "especie", ""),
        "raca": getattr(agendamento, "raca", ""),
        "data": agendamento.data.strftime("%Y-%m-%d"),
        "hora": agendamento.hora.strftime("%H:%M"),
        "duracao": agendamento.duracao,
        "observacoes": agendamento.observacoes,
        "status": agendamento.status,
    })


@login_required
def criar_agendamento(request):
    if request.method == "POST":
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.usuario = request.user
            agendamento.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Método inválido"})


@login_required
def lista_clientes(request):
    """Lista todos os clientes e prepara o formulário para adicionar um novo."""
    clientes = Cliente.objects.all().order_by('nome')
    form = ClienteForm() # Se você quiser usar o modal de cadastro rápido, é bom ter o form
    
    return render(request, "clientes/lista_clientes.html", {
        "clientes": clientes,
        "form": form # Passa o formulário, mesmo que não seja usado diretamente na listagem
    })


@login_required
def cadastrar_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save()
            return redirect("detalhe_cliente", pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, "clientes/cadastrar.html", {"form": form})


@login_required
def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    pacientes = cliente.pacientes.all()
    return render(request, "clientes/detalhe.html", {"cliente": cliente, "pacientes": pacientes})


@login_required
def adicionar_paciente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == "POST":
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            paciente = form.save(commit=False)
            # garante associação correta (o campo estará no form, mas reforçamos aqui)
            paciente.cliente = cliente
            paciente.save()
            return redirect("detalhe_cliente", pk=cliente.pk)
        else:
            # DEBUG: imprime erros no console do servidor (remova em produção)
            print("Erros no AnimalForm:", form.errors)
    else:
        # importante: passar o cliente como valor inicial para o campo hidden
        form = AnimalForm(initial={"cliente": cliente.pk})

    racas_choices_json = json.dumps(Agendamento.RACAS_CHOICES)

    return render(request, "clientes/adicionar.html", {
        "form": form,
        "cliente": cliente,
        "racas_choices": racas_choices_json,
    })

@login_required
def historico_animal(request, animal_pk):
    animal = get_object_or_404(Animal, pk=animal_pk)
    historico = Agendamento.objects.filter(animal=animal).order_by("-data", "-hora")
    consultas_realizadas = historico.filter(status="realizado")
    detalhe_form = AtendimentoDetalhadoForm()

    return render(request, "clientes/historico_animal.html", {
        "animal": animal,
        "cliente": animal.cliente, 
        "historico": historico, 
        "consultas_realizadas": consultas_realizadas,
        "detalhe_form": detalhe_form,
    })