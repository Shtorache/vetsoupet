document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("appointmentModal");
  const btn = document.getElementById("new-appointment");
  const span = document.querySelector(".close");
  const form = document.getElementById("appointmentForm");

  btn.onclick = () => modal.classList.remove("hidden");
  span.onclick = () => modal.classList.add("hidden");
  window.onclick = (e) => { if (e.target === modal) modal.classList.add("hidden"); };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    const res = await fetch("/criar/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (data.success) {
      location.reload();
    } else {
      alert("Erro: " + JSON.stringify(data.errors));
    }
  });
});
