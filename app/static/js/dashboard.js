/* ===============================================================
   Menu principal: menú responsive + buscador de la tabla + graficos.
   =============================================================== */

(function () {
  // ----- Sidebar responsive -----
  const toggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.addEventListener("click", (e) => {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    });
  }

  // ----- Buscador en tabla -----
  const search = document.getElementById("empSearch");
  if (search) {
    search.addEventListener("input", () => {
      const q = search.value.trim().toLowerCase();
      document.querySelectorAll("#empTable tbody tr").forEach((tr) => {
        tr.style.display = tr.dataset.name.includes(q) ? "" : "none";
      });
    });
  }

  // ----- Charts (resumen global) -----
  if (typeof Chart === "undefined") return;

  // Colores Office 365
  const COLORS = {
    blue:    "#0078d4",
    purple:  "#5c2e91",
    teal:    "#008272",
    green:   "#107c10",
    orange:  "#ca5010",
    red:     "#d13438",
    yellow:  "#ffb900",
  };

  // Chart de distribucion (donut): bruto vs descuentos vs neto
  const netoCanvas = document.getElementById("netoChart");
  if (netoCanvas) {
    // tomamos valores del resumen via data attributes;
    // aqui generamos uno sintetico: el FIRST empleado se muestra como representativo.
    const rows = Array.from(document.querySelectorAll("#empTable tbody tr"));
    const labels = rows.map((r) => r.children[1].textContent.split(" ")[0]);
    const netos  = rows.map((r) => parseFloat(r.children[6].textContent.replace(/[^\d.]/g, "")));
    new Chart(netoCanvas, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          data: netos,
          backgroundColor: [COLORS.blue, COLORS.purple, COLORS.teal, COLORS.green, COLORS.orange, COLORS.yellow],
          borderWidth: 2,
          borderColor: "#fff",
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
        animation: { animateRotate: true, duration: 800 },
      },
    });
  }

  // Chart de barras: total bruto vs descuentos vs neto
  const compCanvas = document.getElementById("brutoNetoChart");
  if (compCanvas) {
    const statNums = document.querySelectorAll(".stat-num");
    const totalEmployees = Number(statNums[0].textContent);
    let totalBruto = 0, totalDesc = 0, totalNeto = 0;
    const rows = document.querySelectorAll("#empTable tbody tr");
    rows.forEach((r) => {
      totalBruto += parseFloat(r.children[2].textContent.replace(/[^\d.]/g, ""));
      totalDesc  += parseFloat(r.children[5].textContent.replace(/[^\d.]/g, ""));
      totalNeto  += parseFloat(r.children[6].textContent.replace(/[^\d.]/g, ""));
    });
    void totalEmployees;
    new Chart(compCanvas, {
      type: "bar",
      data: {
        labels: ["Bruto", "Descuentos", "Neto"],
        datasets: [{
          label: "Total (C$)",
          data: [totalBruto, totalDesc, totalNeto],
          backgroundColor: [COLORS.blue, COLORS.red, COLORS.green],
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
        animation: { duration: 700 },
      },
    });
  }
})();
