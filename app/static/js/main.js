// main.js (Completo)
document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("appointmentModal");
  const openBtn = document.getElementById("new-appointment");
  const closeBtn = document.getElementById("close-modal");
  const cancelBtn = document.getElementById("cancel-modal");
  const form = document.getElementById("appointment-form");

  let editingId = null; // 🔹 para saber se está criando ou editando

  if (openBtn && modal) {
    openBtn.onclick = () => {
      editingId = null;
      form.reset();
      // Remove o ID do formulário se houver
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

  // 🔹 Ações de editar
  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      editingId = btn.dataset.id;
      // Define a URL para edição
      form.action = `/editar/${editingId}/`; 
      
      const response = await fetch(`/editar/${editingId}/`);
      const data = await response.json();

      if (data.error) {
        alert(data.error);
        return;
      }

      // Preenche os campos
      document.getElementById("id_cliente").value = data.cliente;
      document.getElementById("id_animal").value = data.animal;
      document.getElementById("id_especie").value = data.especie || "";
      document.getElementById("id_raca").value = data.raca || "";
      
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

  // 🔹 Mostrar/esconder painel de filtros (LÓGICA CORRETA)
  const filtroBtn = document.getElementById("toggle-filtro");
  const filtroPanel = document.getElementById("filtro-panel");

  if (filtroBtn && filtroPanel) {
    filtroBtn.addEventListener("click", () => {
      filtroPanel.classList.toggle("hidden");
      filtroBtn.textContent = filtroPanel.classList.contains("hidden")
        ? "Mostrar Filtros"
        : "Ocultar Filtros";
    });
  }
  
  // 🔹 Lógica para mostrar/esconder agendamentos anteriores
  const toggleAnterioresBtn = document.getElementById("toggle-anteriores");
  const agendaAnteriores = document.getElementById("agenda-anteriores");
  const iconeAnteriores = document.getElementById("icone-anteriores");
  
  if (toggleAnterioresBtn && agendaAnteriores) {
      toggleAnterioresBtn.addEventListener("click", () => {
          agendaAnteriores.classList.toggle("hidden");
          if (agendaAnteriores.classList.contains("hidden")) {
              iconeAnteriores.textContent = "▶";
          } else {
              iconeAnteriores.textContent = "▼";
          }
      });
  }


  // 🔹 Submit do form (criação ou edição)
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