from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Agendamento, Cliente, Paciente
from .forms import AgendamentoForm, ClienteForm, PacienteForm, AtendimentoDetalhadoForm
from django.contrib.auth.decorators import login_required
import json
import datetime # <-- Adicionado para a separação de datas


@login_required
def index(request):
    today = datetime.date.today()
    
    # 1. Agendamentos Passados (anteriores a hoje) - Ordem decrescente
    agendamentos_anteriores = Agendamento.objects.filter(
        data__lt=today 
    ).order_by("-data", "-hora")

    # 2. Agendamentos Ativos (hoje ou futuro) - Ordem crescente (próximo primeiro)
    agendamentos_ativos = Agendamento.objects.filter(
        data__gte=today 
    ).order_by("data", "hora")

    form = AgendamentoForm()
    racas_choices = json.dumps(Agendamento.RACAS_CHOICES)

    return render(request, "index.html", {
        "agendamentos_ativos": agendamentos_ativos, 
        "agendamentos_anteriores": agendamentos_anteriores,
        "form": form,
        "racas_choices": racas_choices,
    })

@login_required
def atendimentos_realizados(request):
    # ✅ Garantindo a ordem cronológica
    agendamentos = Agendamento.objects.filter(status="realizado").order_by("data", "hora")
    form = AgendamentoForm()

    return render(request, "atendimentos_realizados.html", {
        "agendamentos": agendamentos,
        "form": form,
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