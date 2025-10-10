from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("criar/", views.criar_agendamento, name="criar_agendamento"),
    path("clientes/", views.lista_clientes, name="lista_clientes"),
    path("clientes/novo/", views.cadastrar_cliente, name="cadastrar_cliente"),
    path("clientes/<int:pk>/", views.detalhe_cliente, name="detalhe_cliente"),
    path("clientes/<int:cliente_id>/adicionar-paciente/", views.adicionar_paciente, name="adicionar_paciente"),
    path("editar/<int:pk>/", views.editar_agendamento, name="editar_agendamento"),
    path("atendimentos/", views.atendimentos_realizados, name="atendimentos_realizados"),
    path("atendimento/<int:pk>/", views.detalhar_atendimento, name="detalhar_atendimento"),
    path("clientes/<int:cliente_id>/pacientes/", views.buscar_pacientes_por_cliente, name="buscar_pacientes"),
    path("animal/<int:animal_pk>/historico/", views.historico_animal, name="historico_animal"),
    path('agendamentos/atualizar-status/', views.atualizar_status, name='atualizar_status'),
    path('editar_agendamento/<int:pk>/', views.editar_agendamento, name='editar_agendamento'),
    path("planos/", views.lista_planos, name="lista_planos"),
    path("planos/novo/", views.cadastrar_plano, name="cadastrar_plano"),
    path("buscar_pacientes_por_cliente/<int:cliente_id>/", views.buscar_pacientes_por_cliente, name="buscar_pacientes_por_cliente"),
    path("planos/<int:pk>/editar/", views.editar_plano, name="editar_plano"),
    path("planos/<int:pk>/deletar/", views.deletar_plano, name="deletar_plano"),
    path("medicamentos/", views.lista_medicamentos, name="lista_medicamentos"),
    path("medicamentos/novo/", views.cadastrar_medicamento, name="cadastrar_medicamento"),
    path("medicamentos/<int:pk>/editar/", views.editar_medicamento, name="editar_medicamento"),
    path("medicamentos/<int:pk>/excluir/", views.excluir_medicamento, name="excluir_medicamento"),
    path('relatorio-medicamentos/', views.gerar_relatorio_medicamentos, name='gerar_relatorio_medicamentos'),

    ]
