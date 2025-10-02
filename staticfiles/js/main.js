// main.js (Com lógica dinâmica para Cliente/Animal e Espécie/Raça)
document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("appointmentModal");
    const openBtn = document.getElementById("new-appointment");
    const closeBtn = document.getElementById("close-modal");
    const cancelBtn = document.getElementById("cancel-modal");
    const form = document.getElementById("appointment-form");

    let editingId = null; 

    // 🔹 Campos dinâmicos
    const clienteSelect = document.getElementById("id_cliente");
    const animalSelect = document.getElementById("id_animal");
    const especieSelect = document.getElementById("id_especie");
    const racaSelect = document.getElementById("id_raca");
    
    // Pega o JSON das raças que deve ser injetado no index.html
    const racasChoicesElement = document.getElementById("racas-choices");
    // Garante que o JSON exista para evitar erros
    const racasChoices = racasChoicesElement ? JSON.parse(racasChoicesElement.textContent) : {};


    // --------------------------------------------------------------------------------
    // FUNÇÕES DE LÓGICA DINÂMICA
    // --------------------------------------------------------------------------------

    /** Carrega os animais de um cliente via API e preenche o select. */
    const loadAnimals = async (clienteId, selectedAnimalId = null) => {
        // Estado inicial de carregamento
        animalSelect.innerHTML = '<option value="">Carregando...</option>';

        if (!clienteId || clienteId === "") {
            animalSelect.innerHTML = '<option value="">Selecione um cliente primeiro</option>';
            return;
        }

        try {
            const url = `/api/pacientes/${clienteId}/`;
            const response = await fetch(url);
            const data = await response.json();

            animalSelect.innerHTML = '';
            
            if (data.pacientes && data.pacientes.length > 0) {
                // Adiciona a opção padrão se não estiver em edição
                if (!selectedAnimalId) {
                     animalSelect.add(new Option('---------', ''));
                }
               
                data.pacientes.forEach(animal => {
                    const option = new Option(animal.nome, animal.id);
                    // Seleciona o animal correto na edição
                    if (selectedAnimalId && String(animal.id) === String(selectedAnimalId)) {
                        option.selected = true;
                    }
                    animalSelect.add(option);
                });
            } else {
                animalSelect.add(new Option('Nenhum animal cadastrado para este cliente', ''));
            }

        } catch (error) {
            console.error("Erro ao carregar pacientes:", error);
            animalSelect.innerHTML = '<option value="">Erro ao carregar animais</option>';
        }
    };

    /** Atualiza as opções de raça com base na espécie selecionada. */
    const updateRacaChoices = (especie, selectedRaca = null) => {
        racaSelect.innerHTML = ''; 

        const choices = racasChoices[especie] || [["", "Selecione uma espécie primeiro"]];
        
        choices.forEach(([value, label]) => {
            const option = new Option(label, value);
            // Seleciona a raça correta na edição
            if (selectedRaca && value === selectedRaca) {
                option.selected = true;
            }
            racaSelect.add(option);
        });
    };

    // --------------------------------------------------------------------------------
    // EVENTOS DE CAMPO
    // --------------------------------------------------------------------------------

    // Evento de mudança de Cliente (carrega os Animais)
    if (clienteSelect) {
        clienteSelect.addEventListener("change", (e) => {
            loadAnimals(e.target.value);
            // Resetar a espécie e raça ao trocar de cliente, pois o animal muda
            especieSelect.value = "";
            updateRacaChoices("");
        });
    }

    // Evento de mudança de Espécie (carrega as Raças)
    if (especieSelect) {
        especieSelect.addEventListener("change", (e) => {
            updateRacaChoices(e.target.value);
        });
    }

    // --------------------------------------------------------------------------------
    // AÇÕES DO MODAL (NOVO/EDITAR)
    // --------------------------------------------------------------------------------

    if (openBtn && modal) {
        openBtn.onclick = () => {
            editingId = null;
            form.reset();
            
            // 🔹 Resetar campos dinâmicos ao criar novo agendamento
            updateRacaChoices("");
            animalSelect.innerHTML = '<option value="">Selecione um cliente primeiro</option>';
            
            form.action = '/criar/'; 
            modal.classList.remove("hidden");
        };
    }
    if (closeBtn && modal) {
        closeBtn.onclick = () => modal.classList.add("hidden");
    }
    if (cancelBtn && modal) {
        cancelBtn.onclick = () => modal.classList.add("hidden");
    }

    // Ações de editar - ATUALIZADAS
    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            editingId = btn.dataset.id;
            form.action = `/editar/${editingId}/`; 
            
            const response = await fetch(`/editar/${editingId}/`);
            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            // 1. Preenche o cliente
            document.getElementById("id_cliente").value = data.cliente;
            
            // 2. Carrega e seleciona o animal (dinâmico)
            // Usa await para garantir que os animais estejam carregados antes de tentar selecionar
            await loadAnimals(data.cliente, data.animal); 

            // 3. Preenche a espécie e a raça (dinâmico)
            document.getElementById("id_especie").value = data.especie || "";
            updateRacaChoices(data.especie || "", data.raca);

            // 4. Preenche o restante dos campos
            document.getElementById("id_tipo_atendimento").value = data.tipo_atendimento;
            document.getElementById("id_profissional").value = data.profissional;
            document.getElementById("id_data").value = data.data;
            document.getElementById("id_hora").value = data.hora;
            document.getElementById("id_duracao").value = data.duracao;
            document.getElementById("id_observacoes").value = data.observacoes;
            document.getElementById("id_status").value = data.status;

            modal.classList.remove("hidden");
        });
    });

    // ... (Seu código existente para filtros e agendamentos anteriores)
    
    // Submit do form (criação ou edição)
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const url = editingId ? `/editar/${editingId}/` : "/criar/";

            const response = await fetch(url, {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });

            const data = await response.json();
            if (data.success) {
                window.location.reload();
            } else {
                console.error(data.errors || data.error);
                alert("Erro ao salvar o agendamento. Verifique os campos.");
            }
        });
    }
});