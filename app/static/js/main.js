// main.js (Versão Final e Robusta - Absolutamente Completa)
document.addEventListener("DOMContentLoaded", () => {
    
    // --- SELETOR GLOBAL PARA O MODAL ---
    const modal = document.getElementById("appointmentModal");

    // ====================================================================
    // INÍCIO DO BLOCO DE PROTEÇÃO: CÓDIGO QUE SÓ EXECUTA SE O MODAL EXISTIR
    // ====================================================================
    if (modal) {
        const modalTitle = modal.querySelector("h2");
        const form = document.getElementById("appointment-form");
        const allFormGroups = form.querySelectorAll(".form-group");
        let currentEditingId = null;

        // --- FUNÇÕES AUXILIARES PARA O MODAL ---
        function resetModalToNew() {
            currentEditingId = null;
            form.reset();
            modalTitle.textContent = "Novo Agendamento";
            form.action = form.dataset.createUrl || "/criar/"; 

            allFormGroups.forEach(group => {
                group.style.display = 'flex';
                group.classList.remove('is-readonly');
                const input = group.querySelector('input, select, textarea');
                if (input) input.disabled = false;
            });
        }

        function openModal() {
            modal.classList.remove("hidden");
        }

        function closeModal() {
            modal.classList.add("hidden");
        }

        // --- LÓGICA DE EVENTOS DO MODAL ---

        // 1. ABRIR MODAL PARA NOVO AGENDAMENTO
        const newAppointmentBtn = document.getElementById("new-appointment");
        if (newAppointmentBtn) {
            newAppointmentBtn.addEventListener("click", () => {
                resetModalToNew();
                openModal();
            });
        }

      // main.js - SUBSTITUA A LÓGICA DE EDIÇÃO POR ESTA

// --- Elementos do Modal de Edição ---
const editModal = document.getElementById('editAppointmentModal');
const editForm = document.getElementById('edit-appointment-form');
const closeEditModalBtn = document.getElementById('close-edit-modal');
const cancelEditModalBtn = document.getElementById('cancel-edit-modal');

// --- Função para abrir o modal de edição ---
function openEditModal() {
  if (editModal) editModal.classList.remove('hidden');
}

// --- Função para fechar o modal de edição ---
function closeEditModal() {
  if (editModal) editModal.classList.add('hidden');
}

// Event Listeners para fechar o modal
if (closeEditModalBtn) closeEditModalBtn.addEventListener('click', closeEditModal);
if (cancelEditModalBtn) cancelEditModalBtn.addEventListener('click', closeEditModal);


// --- Lógica Principal para o Botão "Editar" ---
document.body.addEventListener("click", (event) => {
    const editButton = event.target.closest('.btn-edit');
    if (!editButton) return;

    const agendamentoId = editButton.dataset.id;
    const fetchURL = `/editar_agendamento/${agendamentoId}/`;

    // 1. Busca os dados atuais do agendamento
    fetch(fetchURL)
        .then(response => {
            if (!response.ok) throw new Error('Falha ao buscar dados');
            return response.json();
        })
        .then(data => {
            // 2. Preenche as informações de visualização (não-editáveis)
            document.getElementById('info-cliente').textContent = data.cliente_nome || 'N/A';
            document.getElementById('info-animal').textContent = data.animal_nome || 'N/A';
            document.getElementById('info-data').textContent = data.data_formatada || 'N/A';
            document.getElementById('info-hora').textContent = data.hora_formatada || 'N/A';

            
            editForm.querySelector('[name="status"]').value = data.status;
            editForm.querySelector('[name="observacoes"]').value = data.observacoes;
            
           
            editForm.action = fetchURL;
            
            
            openEditModal();
        })
        .catch(err => {
            console.error("Erro:", err);
            alert("Não foi possível carregar os dados para edição.");
        });
});

// --- Lógica de submissão do formulário de EDIÇÃO ---
if (editForm) {
  editForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(editForm);
    const url = editForm.action;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
          'X-Requested-With': 'XMLHttpRequest'
        },
      });
      const result = await response.json();

      if (result.success) {
        window.location.reload();
      } else {
        console.error("Erro do servidor:", result.errors);
        alert("Erro ao salvar. Verifique os campos.");
      }
    } catch (error) {
      console.error("Erro de rede:", error);
      alert("Ocorreu um erro de comunicação.");
    }
  });
}
        // --- LÓGICAS DE PREENCHIMENTO DINÂMICO (DEPENDEM DO MODAL) ---
        const clienteSelect = document.getElementById("id_cliente");
        const animalSelect = document.getElementById("id_animal");
        const especieSelect = document.getElementById("id_especie");
        const racaSelect = document.getElementById("id_raca");
        let loadedPacientesData = [];

        // CARREGAR ANIMAIS QUANDO O CLIENTE MUDA
        if (clienteSelect && animalSelect) {
            clienteSelect.addEventListener("change", function() {
                const clienteId = this.value;
                animalSelect.innerHTML = '<option value="">Carregando...</option>';
                loadedPacientesData = [];
                especieSelect.value = '';
                racaSelect.innerHTML = '<option value="">Selecione uma espécie primeiro</option>';

                if (clienteId) {
                    fetch(`/clientes/${clienteId}/pacientes/`)
                        .then(response => response.json())
                        .then(data => {
                            animalSelect.innerHTML = '<option value="">Selecione o animal</option>';
                            loadedPacientesData = data.pacientes || [];
                            if (loadedPacientesData.length > 0) {
                                loadedPacientesData.forEach(paciente => {
                                    const option = new Option(paciente.nome, paciente.id);
                                    animalSelect.appendChild(option);
                                });
                            } else {
                                animalSelect.innerHTML = '<option value="">Nenhum paciente encontrado</option>';
                            }
                        })
                        .catch(err => {
                            console.error("Erro ao buscar pacientes:", err);
                            animalSelect.innerHTML = '<option value="">Erro ao carregar</option>';
                        });
                } else {
                    animalSelect.innerHTML = '<option value="">Selecione um cliente primeiro</option>';
                }
            });
        }

        // PREENCHER ESPÉCIE/RAÇA QUANDO O ANIMAL MUDA
        if (animalSelect && especieSelect && racaSelect) {
            animalSelect.addEventListener("change", function() {
                const animalId = parseInt(this.value);
                const paciente = loadedPacientesData.find(p => p.id === animalId);
                
                if (paciente) {
                    especieSelect.value = paciente.especie;
                    const changeEvent = new Event('change');
                    especieSelect.dispatchEvent(changeEvent);
                    if (paciente.raca) {
                        setTimeout(() => { racaSelect.value = paciente.raca; }, 50);
                    }
                } else {
                    especieSelect.value = '';
                    racaSelect.innerHTML = '<option value="">Selecione uma espécie primeiro</option>';
                }
            });
        }

        // CARREGAR RAÇAS QUANDO A ESPÉCIE MUDA
        if (especieSelect && racaSelect) {
            if (especieSelect.value) {
                especieSelect.dispatchEvent(new Event('change'));
            }
            especieSelect.addEventListener("change", function() {
                const especie = this.value;
                const racaOriginal = racaSelect.value;
                racaSelect.innerHTML = ""; 
                if (window.racasPorEspecie && window.racasPorEspecie[especie]) {
                    racaSelect.add(new Option('---------', ''));
                    window.racasPorEspecie[especie].forEach(([value, text]) => {
                        racaSelect.add(new Option(text, value));
                    });
                    racaSelect.value = racaOriginal;
                } else {
                    racaSelect.add(new Option('Selecione uma espécie primeiro', ''));
                }
            });
        }
    }
    // ====================================================================
    // FIM DO BLOCO DE PROTEÇÃO
    // ====================================================================
    
    document.addEventListener("DOMContentLoaded", function() {
  // Botão editar: abre a modal e busca os dados do agendamento
  document.querySelectorAll(".btn-edit").forEach(btn => {
    btn.addEventListener("click", function() {
      const agId = this.getAttribute("data-id");
      fetch(`/editar_agendamento/${agId}/`)
        .then(response => response.json())
        .then(data => {
          // Preencher os campos da modal
          document.querySelector("#editAppointmentModal input[name='cliente']").value = data.cliente;
          document.querySelector("#editAppointmentModal input[name='animal']").value = data.animal;
          document.querySelector("#editAppointmentModal input[name='especie']").value = data.especie;
          document.querySelector("#editAppointmentModal input[name='raca']").value = data.raca;
          document.querySelector("#editAppointmentModal input[name='tipo_atendimento']").value = data.tipo_atendimento;
          document.querySelector("#editAppointmentModal input[name='profissional']").value = data.profissional;
          document.querySelector("#editAppointmentModal input[name='data']").value = data.data;
          document.querySelector("#editAppointmentModal input[name='hora']").value = data.hora;
          document.querySelector("#editAppointmentModal input[name='duracao']").value = data.duracao;
          // Apenas estes dois são editáveis:
          document.querySelector("#editAppointmentModal select[name='status']").value = data.status;
          document.querySelector("#editAppointmentModal textarea[name='observacoes']").value = data.observacoes;

          // Salvar id para o envio posterior
          document.querySelector("#edit-appointment-form").setAttribute("data-id", agId);
          document.getElementById("editAppointmentModal").classList.remove("hidden");
        });
    });
  });

  // Fechar modal
  document.getElementById("close-edit-modal").addEventListener("click", function() {
    document.getElementById("editAppointmentModal").classList.add("hidden");
  });
  document.getElementById("cancel-edit-modal").addEventListener("click", function() {
    document.getElementById("editAppointmentModal").classList.add("hidden");
  });

  // Envia alteração via AJAX (apenas status e observacoes)
  document.getElementById("edit-appointment-form").addEventListener("submit", function(e){
    e.preventDefault();
    const agId = this.getAttribute("data-id");
    const status = this.querySelector("select[name='status']").value;
    const observacoes = this.querySelector("textarea[name='observacoes']").value;
    fetch(`/editar_agendamento/${agId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": document.querySelector('#edit-appointment-form [name=csrfmiddlewaretoken]').value
      },
      body: `status=${encodeURIComponent(status)}&observacoes=${encodeURIComponent(observacoes)}`
    })
    .then(response => response.json())
    .then(data => {
      if(data.success){
        location.reload(); // recarrega a página para atualizar agendamentos
      } else {
        alert("Erro: " + (data.error || "Falha ao salvar!"));
      }
    });
  });
});


    // --- LÓGICAS INDEPENDENTES (FUNCIONAM EM QUALQUER PÁGINA) ---

    // ATUALIZAR STATUS DIRETAMENTE NA LISTA
    document.body.addEventListener('change', async (event) => {
        if (event.target.classList.contains('status-select')) {
            const selectElement = event.target;
            const appointmentId = selectElement.dataset.id;
            const newStatus = selectElement.value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch('/agendamentos/atualizar-status/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ id: appointmentId, status: newStatus })
                });
                const result = await response.json();
                if (result.success) {
                    selectElement.className = 'status-select';
                    selectElement.classList.add(`status-${newStatus}`);
                } else {
                    alert('Falha ao atualizar o status.');
                    selectElement.value = result.old_status; 
                }
            } catch (error) {
                console.error('Erro de rede ao atualizar status:', error);
                alert('Ocorreu um erro de comunicação.');
            }
        }
    });
    
    // MOSTRAR/ESCONDER FILTROS
    const filtroBtn = document.getElementById("toggle-filtro");
    const filtroPanel = document.getElementById("filtro-panel");
    if (filtroBtn && filtroPanel) {
        filtroBtn.addEventListener("click", () => {
            filtroPanel.classList.toggle("hidden");
            filtroBtn.textContent = filtroPanel.classList.contains("hidden") ? "Mostrar Filtros" : "Ocultar Filtros";
        });
    }
    
    // MOSTRAR/ESCONDER AGENDAMENTOS ANTERIORES
    const toggleAnterioresBtn = document.getElementById("toggle-anteriores");
    const agendaAnteriores = document.getElementById("agenda-anteriores");
    const iconeAnteriores = document.getElementById("icone-anteriores");
    if (toggleAnterioresBtn && agendaAnteriores) {
        toggleAnterioresBtn.addEventListener("click", () => {
            agendaAnteriores.classList.toggle("hidden");
            iconeAnteriores.textContent = agendaAnteriores.classList.contains("hidden") ? "▶" : "▼";
        });
    }
});