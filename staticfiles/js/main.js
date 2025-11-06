document.addEventListener("DOMContentLoaded", function () {

  // =========== MODAL NOVO AGENDAMENTO ===========
  const modal = document.getElementById("appointmentModal");
  const form = document.getElementById("appointment-form");
  const newAppointmentBtn = document.getElementById("new-appointment");
  const cancelBtn = document.getElementById("cancel-modal");
  const closeBtn = document.getElementById("close-modal");

  // Função para abrir o modal de novo agendamento
  if (modal && newAppointmentBtn) {
    newAppointmentBtn.addEventListener("click", function () {
      form.reset();
      modal.classList.remove("hidden");
    });
  }
  // Funções para fechar modal novo agendamento
  if (modal && cancelBtn) cancelBtn.onclick = () => modal.classList.add("hidden");
  if (modal && closeBtn) closeBtn.onclick = () => modal.classList.add("hidden");

  // Intercepta submit do formulário de novo agendamento via AJAX
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" }
        });
        const result = await response.json();
        if (result.success) {
          modal.classList.add("hidden");
          window.location.href = "/";
        } else {
          alert("Erro ao salvar o agendamento.");
        }
      } catch {
        alert("Erro de comunicação.");
      }
    });
  }

  // =========== LÓGICA DE PREENCHIMENTO DINÂMICO (CLIENTE -> ANIMAL -> ESPÉCIE/RAÇA) ===========
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

  // =========== MODAL DE EDIÇÃO ===========

  const editModal = document.getElementById("editAppointmentModal");
  const editForm = document.getElementById("edit-appointment-form");
  const closeEditModalBtn = document.getElementById("close-edit-modal");
  const cancelEditModalBtn = document.getElementById("cancel-edit-modal");

  if (closeEditModalBtn) closeEditModalBtn.onclick = () => editModal.classList.add('hidden');
  if (cancelEditModalBtn) cancelEditModalBtn.onclick = () => editModal.classList.add('hidden');

  // Clique no botão Editar para abrir modal e preencher dados
  document.body.addEventListener("click", function (event) {
    const editButton = event.target.closest('.btn-edit');
    if (!editButton) return;
    const agendamentoId = editButton.dataset.id;
    fetch(`/editar_agendamento/${agendamentoId}/`)
      .then(response => response.json())
      .then(data => {
        document.getElementById('info-cliente').textContent = data.cliente_nome || data.cliente || 'N/A';
        document.getElementById('info-animal').textContent = data.animal_nome || data.animal || 'N/A';
        document.getElementById('info-data').textContent = data.data_formatada || data.data || 'N/A';
        document.getElementById('info-hora').textContent = data.hora_formatada || data.hora || 'N/A';
        editForm.querySelector('[name="status"]').value = data.status;
        editForm.querySelector('[name="observacoes"]').value = data.observacoes;
        editForm.setAttribute("data-id", agendamentoId);
        editModal.classList.remove("hidden");
      })
      .catch(() => alert("Não foi possível carregar os dados para edição."));
  });

  // Submit AJAX - Edição
  if (editForm) {
    editForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const agId = editForm.getAttribute("data-id");
      const status = editForm.querySelector("select[name='status']").value;
      const observacoes = editForm.querySelector("textarea[name='observacoes']").value;
      const csrf = editForm.querySelector("[name=csrfmiddlewaretoken]").value;
      fetch(`/editar_agendamento/${agId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrf,
          "X-Requested-With": "XMLHttpRequest"
        },
        body: `status=${encodeURIComponent(status)}&observacoes=${encodeURIComponent(observacoes)}`
      })
        .then(r => r.json())
        .then(result => {
          if (result.success) {
            editModal.classList.add("hidden");
            window.location.href = "/";
          } else {
            alert("Erro ao salvar edição.");
          }
        })
        .catch(() => alert("Erro de comunicação ao salvar edição."));
    });
  }

  // =========== ATUALIZAÇÃO DE STATUS DIRETO NA LISTA ===========

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
        if (!result.success) {
          alert('Falha ao atualizar o status.');
          selectElement.value = result.old_status;
        }
      } catch (error) {
        alert('Ocorreu um erro de comunicação.');
      }
    }
  });

  // =========== FILTROS E AGENDAMENTOS ANTERIORES ===========

  const filtroBtn = document.getElementById("toggle-filtro");
  const filtroPanel = document.getElementById("filtro-panel");
  if (filtroBtn && filtroPanel) {
    filtroBtn.addEventListener("click", () => {
      filtroPanel.classList.toggle("hidden");
      filtroBtn.textContent = filtroPanel.classList.contains("hidden") ? "Mostrar Filtros" : "Ocultar Filtros";
    });
  }
  const toggleAnterioresBtn = document.getElementById("toggle-anteriores");
  const agendaAnteriores = document.getElementById("agenda-anteriores");
  const iconeAnteriores = document.getElementById("icone-anteriores");
  if (toggleAnterioresBtn && agendaAnteriores) {
    toggleAnterioresBtn.addEventListener("click", () => {
      agendaAnteriores.classList.toggle("hidden");
      iconeAnteriores.textContent = agendaAnteriores.classList.contains("hidden") ? "▶" : "▼";
    });
  }

  // =========== STATUS SPAN COLOR UPDATE ===========

  document.querySelectorAll(".status-select").forEach(select => {
    const card = select.closest('.appt-card');
    if (!card) return;
    const span = card.querySelector(".status");
    if (!span) return;
    const updateStatusSpan = () => {
      span.className = "status " + select.value;
      span.textContent = select.options[select.selectedIndex].text;
    };
    updateStatusSpan();
    select.addEventListener("change", updateStatusSpan);
  });

});


