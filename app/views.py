# app/views.py

# Imports do Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os
import json
import datetime
from .forms import AtendimentoDetalhesForm

from django.db.models import ProtectedError
from django.contrib import messages
from weasyprint import HTML, CSS
from django.templatetags.static import static
from django.conf import settings



# Imports dos seus Models
from .models import (
    Agendamento,
    Cliente,
    Animal,
    PlanoSaude,
    Medicamento,
    ProcedimentoRealizado
)

# Imports dos seus Forms
# ✅ O NOME DO FORMULÁRIO FOI CORRIGIDO AQUI
from .forms import (
    AgendamentoForm,
    EditarAgendamentoForm,
    ClienteForm,
    AnimalForm,
    AtendimentoDetalhesForm, # <- Nome corrigido
    PlanoSaudeForm,
    MedicamentoForm,
    ProcedimentoFormSet,
    MedicamentoUsadoFormSet,
)

@login_required
def gerar_relatorio_medicamentos(request):
    """Gera o relatório de medicamentos com WeasyPrint"""
    medicamentos = Medicamento.objects.all().order_by('nome')

    css_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'css', 'pdf.css')

    html_string = render_to_string('medicamentos/medicamentos_relatorio.html', {
        'medicamentos': medicamentos,
    })

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[CSS(css_path)]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_medicamentos.pdf"'
    return response


@login_required
def gerar_relatorio_clinico_pdf(request, agendamento_id):
    """Gera o relatório clínico completo em PDF"""
    agendamento = get_object_or_404(Agendamento, pk=agendamento_id)
    css_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'css', 'pdf.css')

    html_string = render_to_string('relatorio_atendimentos.html', {
        'ag': agendamento,
    })

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[CSS(css_path)]
    )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_{agendamento.id}.pdf"'
    return response


@login_required
def buscar_pacientes_por_cliente(request, cliente_id):
    """Retorna uma lista de pacientes (id, nome, especie, raca) para o cliente selecionado em formato JSON."""
    
    if not str(cliente_id).isdigit():
        return JsonResponse({"pacientes": []}, status=400)

    try:
        pacientes = Animal.objects.filter(cliente_id=cliente_id).order_by('nome')
    except Exception:
        return JsonResponse({"pacientes": []}, status=500)
    
   
    pacientes_data = [
        {"id": paciente.id, 
         "nome": f"{paciente.nome} ({paciente.especie})",
         "especie": paciente.especie,  
         "raca": paciente.raca or ""   
        }
        for paciente in pacientes
    ]
    
    return JsonResponse({"pacientes": pacientes_data})

@login_required
def index(request):
    today = datetime.date.today()
    
    
    agendamentos_ativos = Agendamento.objects.filter(data__gte=today)
    agendamentos_anteriores = Agendamento.objects.filter(data__lt=today)

    
    profissional = request.GET.get('profissional', '')
    cliente_nome = request.GET.get('cliente', '')
    animal_nome = request.GET.get('animal', '')
    especie = request.GET.get('especie_filtro', '')
    data = request.GET.get('data', '')
    status = request.GET.get('status', '')

    
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
    edit_form = EditarAgendamentoForm()
    racas_choices = json.dumps(Agendamento.RACAS_CHOICES)

    return render(request, "index.html", {
        "agendamentos_ativos": agendamentos_ativos, 
        "agendamentos_anteriores": agendamentos_anteriores,
        "form": form,
        "edit_form": edit_form,
        "racas_choices": racas_choices,
        "filtros": filtros, 
    })
@login_required
def atendimentos_realizados(request):
   
    agendamentos = Agendamento.objects.filter(status="realizado")

   
    profissional = request.GET.get('profissional', '')
    cliente_nome = request.GET.get('cliente', '')
    animal_nome = request.GET.get('animal', '')
    especie = request.GET.get('especie_filtro', '')
    data = request.GET.get('data', '')

   
    if profissional:
        
        agendamentos = agendamentos.filter(profissional__icontains=profissional)
    if cliente_nome:
        agendamentos = agendamentos.filter(cliente__icontains=cliente_nome)
    if animal_nome:
        agendamentos = agendamentos.filter(animal__icontains=animal_nome)
    if especie:
        agendamentos = agendamentos.filter(especie=especie)
    if data:
        agendamentos = agendamentos.filter(data=data)

    
    filtros = {
        'profissional': profissional,
        'cliente': cliente_nome,
        'animal': animal_nome,
        'especie_filtro': especie,
        'data': data
    }
    
   
    agendamentos = agendamentos.order_by("-data", "-hora")
    form = AgendamentoForm()

    return render(request, "atendimentos_realizados.html", {
        "agendamentos": agendamentos,
        "form": form,
        "filtros": filtros,
    })

@login_required
def detalhar_atendimento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)

    if request.method == 'POST':
        form = AtendimentoDetalhesForm(request.POST, instance=agendamento)
        formset = ProcedimentoFormSet(request.POST, instance=agendamento)
        med_formset = MedicamentoUsadoFormSet(request.POST, instance=agendamento)

        if form.is_valid() and formset.is_valid() and med_formset.is_valid():
            form.save()
            formset.save()
            med_formset.save()

            # 🔹 Atualiza o estoque dos medicamentos usados
            for uso in agendamento.medicamentos_usados.all():
                med = uso.medicamento
                if med.quantidade >= uso.quantidade_usada:
                    med.quantidade -= uso.quantidade_usada
                    med.save()

            return redirect('atendimentos_realizados')

    else:
        form = AtendimentoDetalhesForm(instance=agendamento)
        formset = ProcedimentoFormSet(instance=agendamento)
        med_formset = MedicamentoUsadoFormSet(instance=agendamento)

    context = {
        'agendamento': agendamento,
        'form': form,
        'formset': formset,
        'med_formset': med_formset,
    }

    return render(request, 'detalhar_atendimento.html', context)




@login_required
def editar_agendamento(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)

    
    if request.method == "POST":
        
        if agendamento.usuario != request.user:
            return JsonResponse({"success": False, "error": "Permissão negada"}, status=403)
        
        form = EditarAgendamentoForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})

    
    else:
        data = {
            "cliente_nome": agendamento.cliente.nome,
            "animal_nome": agendamento.animal.nome,
            "data_formatada": agendamento.data.strftime("%d/%m/%Y"),
            "hora_formatada": agendamento.hora.strftime("%H:%M"),
            "status": agendamento.status,
            "observacoes": agendamento.observacoes or "", 
        }
        return JsonResponse(data)




@login_required
@require_POST
def atualizar_status(request):
    try:
        data = json.loads(request.body)
        agendamento_id = data.get('id')
        novo_status = data.get('status')

        agendamento = Agendamento.objects.get(pk=agendamento_id)
        
       

        agendamento.status = novo_status
        agendamento.save(update_fields=['status'])

        return JsonResponse({'success': True})

    except Agendamento.DoesNotExist:
       
        return JsonResponse({'success': False, 'error': 'Agendamento não encontrado'}, status=404)
    except Exception as e:

        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

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
    # 1. Busca o cliente (isso já estava correto)
    cliente = get_object_or_404(Cliente, pk=pk)

    # 2. Busca todos os pacientes daquele cliente (isso também já estava correto)
    pacientes = cliente.pacientes.all()
    
    # 3. --- A LÓGICA ADICIONADA ESTÁ AQUI ---
    # Para cada paciente na lista, vamos encontrar o seu plano ativo.
    for paciente in pacientes:
        # Busca na tabela de planos, filtra por este paciente e pelo status 'ativo'.
        # .first() pega o primeiro que encontrar ou retorna None se não achar nenhum.
        plano_ativo = paciente.plano_saude.filter(ativo=True).first()
        
        # Criamos um novo atributo "plano_ativo" no objeto do paciente.
        # O template vai usar isso para exibir os dados.
        paciente.plano_ativo = plano_ativo

    # 4. Envia os dados para o template. Note que a lista 'pacientes' agora
    #    contém a informação extra do plano.
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
    detalhe_form = AtendimentoDetalhesForm()


    return render(request, "clientes/historico_animal.html", {
        "animal": animal,
        "cliente": animal.cliente, 
        "historico": historico, 
        "consultas_realizadas": consultas_realizadas,
        "detalhe_form": detalhe_form,
    })

@login_required
def lista_planos(request):
    planos = PlanoSaude.objects.select_related("cliente", "animal").all().order_by("-validade")
    return render(request, "planos/lista_planos.html", {"planos": planos})


@login_required
def cadastrar_plano(request):
    if request.method == "POST":
        form = PlanoSaudeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_planos")
    else:
        form = PlanoSaudeForm()
    return render(request, "planos/cadastrar_plano.html", {"form": form})

@login_required
def editar_plano(request, pk):
    plano = get_object_or_404(PlanoSaude, pk=pk)
    if request.method == "POST":
        form = PlanoSaudeForm(request.POST, instance=plano)
        if form.is_valid():
            form.save()
            return redirect("lista_planos")
    else:
        form = PlanoSaudeForm(instance=plano)
    return render(request, "planos/editar_plano.html", {"form": form, "plano": plano})


@login_required
def deletar_plano(request, pk):
    plano = get_object_or_404(PlanoSaude, pk=pk)
    if request.method == "POST":
        plano.delete()
        return redirect("lista_planos")
    return render(request, "planos/deletar_plano.html", {"plano": plano})

# -----------------------------
# CRUD de Medicamentos
# -----------------------------
@login_required
def lista_medicamentos(request):
    busca = request.GET.get("busca", "")
    medicamentos = Medicamento.objects.all().order_by("nome")

    if busca:
        medicamentos = medicamentos.filter(nome__icontains=busca)

    return render(request, "medicamentos/lista.html", {
        "medicamentos": medicamentos,
        "busca": busca,
    })


@login_required
def cadastrar_medicamento(request):
    if request.method == "POST":
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_medicamentos")
    else:
        form = MedicamentoForm()
    return render(request, "medicamentos/cadastrar.html", {"form": form})


@login_required
def editar_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    if request.method == "POST":
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            return redirect("lista_medicamentos")
    else:
        form = MedicamentoForm(instance=medicamento)
    return render(request, "medicamentos/editar.html", {"form": form, "medicamento": medicamento})


@login_required
def excluir_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    try:
        medicamento.delete()
        messages.success(request, "✅ Medicamento excluído com sucesso!")
    except ProtectedError:
        messages.error(request, "❌ Este medicamento está vinculado a atendimentos e não pode ser excluído.")
    return redirect("lista_medicamentos")


# -----------------------------
# RELATÓRIO DE MEDICAMENTOS
# -----------------------------
@login_required
def gerar_relatorio_medicamentos(request):
    """Gera o relatório de medicamentos (PDF com WeasyPrint)."""
    medicamentos = Medicamento.objects.all().order_by("nome")

    # Caminho do CSS físico
    css_path = os.path.join(settings.BASE_DIR, "app", "static", "css", "pdf.css")

    # Datas de referência para destacar validade
    hoje = timezone.now().date()
    validade_alerta = hoje + datetime.timedelta(days=30)

    # Renderiza o HTML do relatório
    html_string = render_to_string("medicamentos/medicamentos_relatorio.html", {
        "medicamentos": medicamentos,
        "hoje": hoje,
        "validade_alerta": validade_alerta,
        "agora": timezone.now(),
    })

    # Gera o PDF com o CSS físico
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[CSS(css_path)]
    )

    # Retorna resposta HTTP com PDF
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="relatorio_medicamentos.pdf"'
    return response


# -----------------------------
# RELATÓRIO CLÍNICO (ATENDIMENTO)
# -----------------------------
@login_required
def gerar_relatorio_clinico_pdf(request, agendamento_id):
    """Gera o relatório clínico completo (PDF)"""
    agendamento = get_object_or_404(Agendamento, pk=agendamento_id)
    css_path = os.path.join(settings.BASE_DIR, "app", "static", "css", "pdf.css")

    html_string = render_to_string("relatorio_atendimentos.html", {
        "ag": agendamento,
    })

    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
        stylesheets=[CSS(css_path)]
    )

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="relatorio_{agendamento.id}.pdf"'
    return response