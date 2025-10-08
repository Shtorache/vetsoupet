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

        // 2. ABRIR MODAL PARA EDITAR AGENDAMENTO
        document.body.addEventListener("click", (event) => {
            const editButton = event.target.closest('.edit-btn');
            if (editButton) {
                const card = editButton.closest('.appt-card');
                currentEditingId = card.dataset.id;
                const fetchURL = `/editar/${currentEditingId}/`;

                fetch(fetchURL)
                    .then(response => {
                        if (!response.ok) { throw new Error('Falha ao buscar dados'); }
                        return response.json();
                    })
                    .then(data => {
                        resetModalToNew(); 
                        modalTitle.textContent = "Editar Agendamento";
                        form.action = fetchURL;

                        for (const key in data) {
                            const input = form.querySelector(`#id_${key}`);
                            if (input) input.value = data[key];
                        }
                        
                        const readonlyFields = ['cliente', 'animal', 'especie', 'raca', 'tipo_atendimento', 'profissional', 'duracao', 'observacoes'];
                        
                        allFormGroups.forEach(group => {
                            const input = group.querySelector('input, select, textarea');
                            if (!input) return;
                            const fieldName = input.id.replace('id_', '');
                            if (readonlyFields.includes(fieldName)) {
                                input.disabled = true;
                                group.classList.add('is-readonly');
                            }
                        });
                        
                        openModal();
                    })
                    .catch(err => {
                        console.error("Erro ao buscar dados do agendamento:", err);
                        alert("Não foi possível carregar os dados para edição.");
                    });
            }
        });
        
        // 3. FECHAR O MODAL
        const closeBtn = document.getElementById("close-modal");
        const cancelBtn = document.getElementById("cancel-modal");
        if (closeBtn) closeBtn.addEventListener("click", closeModal);
        if (cancelBtn) cancelBtn.addEventListener("click", closeModal);
        
        // 4. SUBMISSÃO DO FORMULÁRIO (AJAX)
        if (form) {
            if (!form.dataset.createUrl) {
                form.dataset.createUrl = "/criar/";
            }
            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const url = form.action;
                try {
                    const response = await fetch(url, {
                        method: "POST",
                        body: formData,
                        headers: { "X-Requested-With": "XMLHttpRequest" },
                    });
                    const result = await response.json();
                    if (result.success) {
                        window.location.reload();
                    } else {
                        console.error("Erro do servidor:", result.errors || result.error);
                        alert("Erro ao salvar o agendamento. Verifique os campos.");
                    }
                } catch (error) {
                    console.error("Erro de rede:", error);
                    alert("Ocorreu um erro de comunicação com o servidor.");
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