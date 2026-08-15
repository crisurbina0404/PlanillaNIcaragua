"""Validaciones de formularios compartidas.

Las mismas reglas se replican en el cliente (JS) para validacion en tiempo real
y aqui (Python) como barrera de seguridad.
"""

import re

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

PASSWORD_MIN = 8
PASSWORD_MAX = 64


def validate_username(username: str) -> list[str]:
    errors = []
    if not username:
        errors.append("El nombre de usuario es obligatorio.")
    elif not USERNAME_RE.match(username):
        if len(username) < 3:
            errors.append("Debe tener al menos 3 caracteres.")
        elif len(username) > 20:
            errors.append("No puede tener mas de 20 caracteres.")
        else:
            errors.append("Solo letras, numeros y guion bajo (_).")
    return errors


def validate_email(email: str) -> list[str]:
    errors = []
    if not email:
        errors.append("El correo es obligatorio.")
    elif not EMAIL_RE.match(email):
        errors.append("Correo electronico invalido.")
    return errors


def validate_password(password: str) -> list[str]:
    errors = []
    if not password:
        errors.append("La contrasena es obligatoria.")
        return errors
    if len(password) < PASSWORD_MIN:
        errors.append(f"Debe tener al menos {PASSWORD_MIN} caracteres.")
    if len(password) > PASSWORD_MAX:
        errors.append(f"No puede tener mas de {PASSWORD_MAX} caracteres.")
    if not re.search(r"[A-Z]", password):
        errors.append("Debe incluir al menos una mayuscula.")
    if not re.search(r"[a-z]", password):
        errors.append("Debe incluir al menos una minuscula.")
    if not re.search(r"\d", password):
        errors.append("Debe incluir al menos un numero.")
    return errors


def validate_full_name(name: str) -> list[str]:
    errors = []
    if not name or not name.strip():
        errors.append("El nombre completo es obligatorio.")
    elif len(name.strip()) < 3:
        errors.append("El nombre completo es muy corto.")
    return errors


def validate_employee_names(nombres: str) -> list[str]:
    errors = []
    if not nombres or not nombres.strip():
        errors.append("Los nombres del empleado son obligatorios.")
    elif len(nombres.strip()) < 3:
        errors.append("El nombre del empleado es muy corto.")
    return errors


def validate_salary(salary) -> list[str]:
    errors = []
    if salary is None or salary == "":
        errors.append("El salario es obligatorio.")
        return errors
    try:
        value = float(salary)
    except (TypeError, ValueError):
        errors.append("El salario debe ser un numero.")
        return errors
    if value <= 0:
        errors.append("El salario debe ser mayor a cero.")
    elif value > 100_000_000:
        errors.append("El salario es demasiado grande.")
    return errors


def validate_registration(form: dict[str, str]) -> dict[str, list[str]]:
    return {
        "username": validate_username(form.get("username", "")),
        "email": validate_email(form.get("email", "")),
        "password": validate_password(form.get("password", "")),
        "full_name": validate_full_name(form.get("full_name", "")),
    }


def validate_employee(form: dict[str, str]) -> dict[str, list[str]]:
    return {
        "nombres": validate_employee_names(form.get("nombres", "")),
        "salario_bruto": validate_salary(form.get("salario_bruto", "")),
    }


def has_errors(errors: dict[str, list[str]]) -> bool:
    return any(errs for errs in errors.values())
