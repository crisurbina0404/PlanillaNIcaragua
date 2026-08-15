/* ===============================================================
   Pagina de detalle del empleado: graficos con Chart.js.
   =============================================================== */

(function () {
  if (typeof Chart === "undefined" || !window.__DATA__) return;

  const data = window.__DATA__;
  const COLORS = {
    blue:    "#0078d4",
    purple:  "#5c2e91",
    teal:    "#008272",
    green:   "#107c10",
    orange:  "#ca5010",
    red:     "#d13438",
  };

  const fmt = (n) => `C$${Number(n).toLocaleString("es-NI", {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  })}`;

  // ----- Torta: distribucion INSS / IR / Neto / Otros -----
  const distCanvas = document.getElementById("distChart");
  if (distCanvas) {
    new Chart(distCanvas, {
      type: "doughnut",
      data: {
        labels: ["INSS", "IR mensual", "Salario neto"],
        datasets: [{
          data: [data.inss, data.ir, data.neto],
          backgroundColor: [COLORS.orange, COLORS.purple, COLORS.green],
          borderColor: "#fff",
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${fmt(ctx.parsed)}`
            }
          }
        },
        animation: { animateRotate: true, duration: 800 },
      },
    });
  }

  // ----- Barras: bruto, descuentos, neto, renta anual, IR anual -----
  const compCanvas = document.getElementById("compChart");
  if (compCanvas) {
    new Chart(compCanvas, {
      type: "bar",
      data: {
        labels: ["Salario bruto", "INSS", "IR mensual", "Total descuentos", "Salario neto"],
        datasets: [{
          label: "Monto mensual (C$)",
          data: [data.bruto, data.inss, data.ir, data.inss + data.ir, data.neto],
          backgroundColor: [COLORS.blue, COLORS.orange, COLORS.purple, COLORS.red, COLORS.green],
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
        animation: { duration: 800 },
      },
    });
  }

  // ----- Tarifa IR badge -----
  console.log(`Tarifa IR anual aplicada: ${data.irPct}%`);
})();
