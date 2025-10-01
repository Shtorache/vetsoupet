from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Agendamento, Cliente, Paciente
from .forms import AgendamentoForm, ClienteForm, PacienteForm, AtendimentoDetalhadoForm
from django.contrib.auth.decorators import login_required
import json
import datetime # <-- Adicionado para a separação de datas


# Substitua sua função index por esta:

@login_required
def index(request):
    today = datetime.date.today()
    
    # 1. Define as buscas base
    agendamentos_ativos = Agendamento.objects.filter(data__gte=today)
    agendamentos_anteriores = Agendamento.objects.filter(data__lt=today)

    # 2. Pega os valores do formulário de filtro da URL (GET)
    profissional = request.GET.get('profissional', '')
    cliente = request.GET.get('cliente', '')
    animal = request.GET.get('animal', '')
    especie = request.GET.get('especie_filtro', '')
    data = request.GET.get('data', '')
    status = request.GET.get('status', '')

    # 3. Aplica os filtros nas DUAS buscas, se eles existirem
    if profissional:
        agendamentos_ativos = agendamentos_ativos.filter(profissional__icontains=profissional)
        agendamentos_anteriores = agendamentos_anteriores.filter(profissional__icontains=profissional)
    if cliente:
        agendamentos_ativos = agendamentos_ativos.filter(cliente__icontains=cliente)
        agendamentos_anteriores = agendamentos_anteriores.filter(cliente__icontains=cliente)
    if animal:
        agendamentos_ativos = agendamentos_ativos.filter(animal__icontains=animal)
        agendamentos_anteriores = agendamentos_anteriores.filter(animal__icontains=animal)
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
        'cliente': cliente,
        'animal': animal,
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
    cliente = request.GET.get('cliente', '')
    animal = request.GET.get('animal', '')
    especie = request.GET.get('especie_filtro', '')
    data = request.GET.get('data', '')

    # 3. Aplica os filtros na busca, um por um, se eles existirem
    if profissional:
        # __icontains faz uma busca case-insensitive que "contém" o texto
        agendamentos = agendamentos.filter(profissional__icontains=profissional)
    if cliente:
        agendamentos = agendamentos.filter(cliente__icontains=cliente)
    if animal:
        agendamentos = agendamentos.filter(animal__icontains=animal)
    if especie:
        agendamentos = agendamentos.filter(especie=especie)
    if data:
        agendamentos = agendamentos.filter(data=data)

    # 4. Cria um dicionário com os filtros aplicados para devolver ao template
    filtros = {
        'profissional': profissional,
        'cliente': cliente,
        'animal': animal,
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
        "cliente": agendamento.cliente,
        "animal": agendamento.animal,
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
    clientes = Cliente.objects.all()
    return render(request, "clientes/lista.html", {"clientes": clientes})


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
        form = PacienteForm(request.POST, request.FILES)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.cliente = cliente
            paciente.save()
            return redirect("detalhe_cliente", pk=cliente.pk)
    else:
        form = PacienteForm()
    return render(request, "pacientes/adicionar.html", {"form": form, "cliente": cliente})