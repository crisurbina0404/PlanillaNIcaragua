/* Helpers comunes de autenticacion: mostrar/ocultar contrasena. */

document.querySelectorAll(".show-pass").forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = document.getElementById(btn.dataset.target);
    if (!target) return;
    if (target.type === "password") {
      target.type = "text";
      btn.textContent = "\u2764"; // simple visual hint
    } else {
      target.type = "password";
      btn.textContent = "\uD83D\uDC41"; // ojo
    }
  });
});
