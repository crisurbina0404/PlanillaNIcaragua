/* ===============================================================
   Funciones de validacion en cliente. Mismas reglas que app/validation.py.
   =============================================================== */

const Validators = {
  usernameRe: /^[a-zA-Z0-9_]{3,20}$/,
  emailRe:    /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,

  username(value) {
    const v = (value || "").trim();
    if (!v) return "El nombre de usuario es obligatorio.";
    if (v.length < 3) return "Debe tener al menos 3 caracteres.";
    if (v.length > 20) return "No puede tener mas de 20 caracteres.";
    if (!this.usernameRe.test(v)) return "Solo letras, numeros y guion bajo (_).";
    return "";
  },

  email(value) {
    const v = (value || "").trim();
    if (!v) return "El correo es obligatorio.";
    if (!this.emailRe.test(v)) return "Correo electronico invalido.";
    return "";
  },

  password(value) {
    const v = value || "";
    if (!v) return "La contrasena es obligatoria.";
    if (v.length < 8) return "Debe tener al menos 8 caracteres.";
    if (v.length > 64) return "No puede tener mas de 64 caracteres.";
    if (!/[A-Z]/.test(v)) return "Debe incluir al menos una mayuscula.";
    if (!/[a-z]/.test(v)) return "Debe incluir al menos una minuscula.";
    if (!/\d/.test(v))   return "Debe incluir al menos un numero.";
    return "";
  },

  fullName(value) {
    const v = (value || "").trim();
    if (!v) return "El nombre completo es obligatorio.";
    if (v.length < 3) return "El nombre completo es muy corto.";
    return "";
  },

  employeeNames(value) {
    const v = (value || "").trim();
    if (!v) return "Los nombres del empleado son obligatorios.";
    if (v.length < 3) return "El nombre del empleado es muy corto.";
    return "";
  },

  salary(value) {
    const v = (value === undefined ? "" : value).toString().trim();
    if (!v) return "El salario es obligatorio.";
    const num = Number(v);
    if (Number.isNaN(num)) return "El salario debe ser un numero.";
    if (num <= 0) return "El salario debe ser mayor a cero.";
    if (num > 100_000_000) return "El salario es demasiado grande.";
    return "";
  },

  /** Score 0..100 para feedback de fuerza de contrasena. */
  passwordStrength(value) {
    const v = value || "";
    let score = 0;
    if (v.length >= 8)  score += 25;
    if (v.length >= 12) score += 15;
    if (/[A-Z]/.test(v)) score += 15;
    if (/[a-z]/.test(v)) score += 15;
    if (/\d/.test(v))    score += 15;
    if (/[^A-Za-z0-9]/.test(v)) score += 15;
    return Math.min(100, score);
  }
};

/* Set error message under a field; toggle invalid/valid classes.
   Retorna true si el campo es valido. */
function setFieldError(input, message) {
  const errEl = document.querySelector(`[data-error-for="${input.name}"]`);
  if (errEl) errEl.textContent = message || "";
  if (message) {
    input.classList.add("invalid");
    input.classList.remove("valid");
  } else {
    input.classList.remove("invalid");
    if (input.value.trim()) input.classList.add("valid");
    else input.classList.remove("valid");
  }
  return !message;
}

/* Debounce utilitario para no saturar el servidor con AJAX. */
function debounce(fn, wait = 350) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}

/* Toast helpers para mostrar mensajes no funcionales. */
function toast(message, type = "info", ms = 4000) {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transform = "translateX(40px)";
    el.style.transition = "all .25s ease";
    setTimeout(() => el.remove(), 250);
  }, ms);
}

/* Ripple effect en botones primary. */
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".btn-primary");
  if (!btn) return;
  const circle = document.createElement("span");
  circle.className = "btn-ripple";
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  circle.style.width = circle.style.height = `${size}px`;
  circle.style.left = `${e.clientX - rect.left - size / 2}px`;
  circle.style.top  = `${e.clientY - rect.top - size / 2}px`;
  btn.appendChild(circle);
  setTimeout(() => circle.remove(), 600);
});
