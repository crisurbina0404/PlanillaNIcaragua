/* ===============================================================
   Registro de usuario con validacion en tiempo real.
   - Validacion local inmediata en cada input.
   - Verificacion AJAX de unicidad (username / email) con debounce.
   - Barra de fuerza de contrasena en vivo.
   - Boton submit bloqueado mientras el form sea invalido.
   =============================================================== */

(function () {
  const form = document.getElementById("registerForm");
  if (!form) return;

  const fields = {
    full_name: form.querySelector("#full_name"),
    username:  form.querySelector("#username"),
    email:     form.querySelector("#email"),
    password:  form.querySelector("#password"),
  };
  const submitBtn = form.querySelector("#submitBtn");
  const strengthBar = document.getElementById("strengthBar");

  let remoteErrors = { username: "", email: "" };

  // ---------- Validacion local ----------
  function validateField(name) {
    const input = fields[name];
    let msg = "";
    switch (name) {
      case "full_name":  msg = Validators.fullName(input.value); break;
      case "username":   msg = Validators.username(input.value); break;
      case "email":       msg = Validators.email(input.value); break;
      case "password":   msg = Validators.password(input.value); updateStrength(input.value); break;
    }
    if (name === "username" && !msg && remoteErrors.username) msg = remoteErrors.username;
    if (name === "email"    && !msg && remoteErrors.email)    msg = remoteErrors.email;
    input.dataset.valid = setFieldError(input, msg) ? "1" : "0";
    refreshSubmit();
  }

  Object.keys(fields).forEach((name) => {
    fields[name].addEventListener("input", () => validateField(name));
    fields[name].addEventListener("blur",  () => validateField(name));
  });

  // ---------- Verificacion remota de unicidad ----------
  async function checkRemote(url, value, key) {
    if (!value) return;
    const localMsg = Validators[key](value);
    if (localMsg) {
      remoteErrors[key] = "";
      return;
    }
    try {
      const res = await fetch(`${url}?${key}=${encodeURIComponent(value)}`);
      const data = await res.json();
      if (!data.valid) {
        remoteErrors[key] = data.errors[0];
        if (fields[key] === document.activeElement) {
          setFieldError(fields[key], data.errors[0]);
        }
        refreshSubmit();
      } else {
        remoteErrors[key] = "";
        // si el campo tiene foco, recalcular (limpiar error remoto)
        if (fields[key] === document.activeElement) validateField(key);
      }
    } catch (_) { /* sin red no bloqueamos */ }
  }

  fields.username.addEventListener("input", debounce((e) =>
    checkRemote("/api/check/username", e.target.value, "username")));
  fields.email.addEventListener("input", debounce((e) =>
    checkRemote("/api/check/email", e.target.value, "email")));

  // ---------- Barra de fuerza ----------
  function updateStrength(value) {
    if (!strengthBar) return;
    const score = Validators.passwordStrength(value);
    const s = strengthBar.style;
    s.width = `${score}%`;
    if (score >= 75)      s.background = "var(--ms-green)";
    else if (score >= 50) s.background = "var(--ms-yellow)";
    else if (score >= 25) s.background = "var(--ms-orange)";
    else                  s.background = "var(--ms-red)";
  }

  // ---------- Control del submit ----------
  function refreshSubmit() {
    let allValid = true;
    Object.keys(fields).forEach((name) => {
      const input = fields[name];
      const localMsg = ({
        full_name: Validators.fullName(input.value),
        username:  Validators.username(input.value),
        email:     Validators.email(input.value),
        password:  Validators.password(input.value),
      })[name];
      if (localMsg || (input.value && input.dataset.valid === "0")) allValid = false;
    });
    if (remoteErrors.username || remoteErrors.email) allValid = false;
    submitBtn.disabled = !allValid;
    submitBtn.style.opacity = allValid ? "1" : ".6";
    submitBtn.style.cursor  = allValid ? "pointer" : "not-allowed";
  }

  // Validacion inicial por si el server re-renderizo con errores.
  Object.keys(fields).forEach((name) => validateField(name));
  refreshSubmit();

  form.addEventListener("submit", (e) => {
    Object.keys(fields).forEach((name) => validateField(name));
    refreshSubmit();
    if (submitBtn.disabled) e.preventDefault();
  });
})();
