/* ===============================================================
   Formulario de registrar empleado: calculo en tiempo real.
   =============================================================== */

(function () {
  const form = document.getElementById("empForm");
  if (!form) return;

  const inputNombre  = form.querySelector("#nombres");
  const inputSalario = form.querySelector("#salario_bruto");
  const resultBox    = document.getElementById("calcResult");

  const fmt = (n) => `C$${Number(n).toLocaleString("es-NI", {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  })}`;

  function renderCalculo(c) {
    if (!c) {
      resultBox.classList.add("empty");
      resultBox.innerHTML = `<div class="calc-placeholder">
        <div class="empty-ico">&#129518;</div>
        <p class="muted">Escribe un salario valido para ver el desglose.</p>
      </div>`;
      return;
    }
    resultBox.classList.remove("empty");
    resultBox.innerHTML = `
      <div class="calc-line"><span class="lbl">Salario bruto</span><span class="val">${fmt(c.salario_bruto)}</span></div>
      <div class="calc-line"><span class="lbl">INSS (7%)</span><span class="val neg">-${fmt(c.inss)}</span></div>
      <div class="calc-line"><span class="lbl">Renta neta mensual</span><span class="val">${fmt(c.renta_neta_mensual)}</span></div>
      <div class="calc-line"><span class="lbl">Renta neta anual</span><span class="val">${fmt(c.renta_anual)}</span></div>
      <div class="calc-line"><span class="lbl">IR anual</span><span class="val">${fmt(c.ir_anual)}</span></div>
      <div class="calc-line"><span class="lbl">IR mensual</span><span class="val neg">-${fmt(c.ir_mensual)}</span></div>
      <div class="calc-line"><span class="lbl">Total descuentos</span><span class="val neg">-${fmt(c.total_descuentos)}</span></div>
      <div class="calc-line"><span class="lbl"><strong>Salario neto</strong></span><span class="val pos"><strong>${fmt(c.salario_neto)}</strong></span></div>
      <div class="calc-tarifa">
        Tarifa IR anual aplicada: <strong>${c.ir_pct}%</strong>.
      </div>
    `;
  }

  function validate() {
    const errs = {};
    errs.nombres = Validators.employeeNames(inputNombre.value);
    errs.salario_bruto = Validators.salary(inputSalario.value);
    setFieldError(inputNombre, errs.nombres);
    setFieldError(inputSalario, errs.salario_bruto);
    return errs;
  }

  async function calcular() {
    validate();
    if (Validators.salary(inputSalario.value)) {
      renderCalculo(null);
      return;
    }
    try {
      const url = `/api/calc?nombres=${encodeURIComponent(inputNombre.value)}&salario_bruto=${encodeURIComponent(inputSalario.value)}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.valid) renderCalculo(data.calculo);
      else renderCalculo(null);
    } catch (_) { /* sin red no bloqueamos */ }
  }

  inputNombre.addEventListener("input", debounce(calcular, 200));
  inputSalario.addEventListener("input", debounce(calcular, 200));

  // Si venimos de un POST fallido, calcular al cargar.
  if (window.__PREV_CALC) calcular();
  else validarInicial();

  function validarInicial() { validate(); }

  form.addEventListener("submit", (e) => {
    const errs = validate();
    if (errs.nombres || errs.salario_bruto) {
      e.preventDefault();
      toast("Corrige los errores antes de guardar.", "warning");
    }
  });
})();
