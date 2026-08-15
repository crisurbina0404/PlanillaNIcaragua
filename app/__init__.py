"""Aplicacion Flask principal: Planilla Nicaragua.

Logica:
  - /            redirige a login o al menu segun sesion.
  - /login       inicio de sesion interactivo.
  - /register    registro de usuario en tiempo real (validacion AJAX).
  - /logout      cerrar sesion.
  - /dashboard   menu principal con la lista de empleados y resumen.
  - /registrar   formulario para registrar un nuevo empleado (con calculo).
  - /detalle/<id> tabla de detalle de cada empleado con graficos.
  - /api/...     endpoints usados por la validacion en tiempo real.
"""

from __future__ import annotations

import sqlite3
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
)

from app import db, payroll, validation

app = Flask(__name__)
app.secret_key = "planilla-ni-secret-key-change-in-production"

# Asegura que la base de datos exista y tenga las tablas / admin por defecto.
db.init_db()


# -------------------- DECORADORES --------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesion para continuar.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def inject_user():
    user = None
    if "user_id" in session:
        user = db.get_user_by_username(session["username"]) or None
    from datetime import datetime, timezone
    return {"current_user": user, "moment_year": datetime.now(timezone.utc).year}


app.context_processor(inject_user)


# -------------------- RUTAS PUBLICAS --------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=("GET", "POST"))
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        errors = {}
        if not username:
            errors["username"] = ["Ingresa tu usuario."]
        if not password:
            errors["password"] = ["Ingresa tu contrasena."]
        if errors:
            return render_template("auth/login.html", errors=errors, form=request.form), 400

        user = db.verify_user(username, password)
        if not user:
            return render_template(
                "auth/login.html",
                errors={"form": ["Usuario o contrasena incorrectos."]},
                form=request.form,
            ), 401

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["full_name"] = user["full_name"]
        flash(f"Bienvenido, {user['full_name']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("auth/login.html", errors={}, form={})


@app.route("/register", methods=("GET", "POST"))
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        form = {
            "username": (request.form.get("username") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "password": request.form.get("password") or "",
            "full_name": (request.form.get("full_name") or "").strip(),
        }
        errors = validation.validate_registration(form)

        # Verificar unicidad en tiempo real (tambien cubierto por la API AJAX).
        if not errors["username"] and db.get_user_by_username(form["username"]):
            errors["username"].append("Ese usuario ya esta registrado.")
        if not errors["email"] and db.get_user_by_email(form["email"]):
            errors["email"].append("Ese correo ya esta registrado.")

        if validation.has_errors(errors):
            return render_template("auth/register.html", errors=errors, form=form), 400

        try:
            db.create_user(form["username"], form["email"], form["password"], form["full_name"])
        except sqlite3.IntegrityError:
            errors["form"] = ["Error: el usuario o correo ya existen."]
            return render_template("auth/register.html", errors=errors, form=form), 400

        flash("Cuenta creada exitosamente. Ya puedes iniciar sesion.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html", errors={}, form={})


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada.", "info")
    return redirect(url_for("login"))


# -------------------- RUTAS PRIVADAS --------------------

@app.route("/dashboard")
@login_required
def dashboard():
    empleados = db.list_employees(session["user_id"])
    resumen = db.sumary(session["user_id"])
    return render_template("main/dashboard.html", empleados=empleados, resumen=resumen)


@app.route("/registrar", methods=("GET", "POST"))
@login_required
def registrar_empleado():
    if request.method == "POST":
        form = {
            "nombres": (request.form.get("nombres") or "").strip(),
            "salario_bruto": (request.form.get("salario_bruto") or "").strip(),
        }
        errors = validation.validate_employee(form)

        if validation.has_errors(errors):
            calculo = None
            if not errors["salario_bruto"]:
                calculo = payroll.calcular_salario(form["salario_bruto"], form["nombres"])
            return render_template(
                "main/registrar.html", errors=errors, form=form, calculo=calculo
            ), 400

        calculo = payroll.calcular_salario(form["salario_bruto"], form["nombres"])
        emp_id = db.insert_employee(session["user_id"], calculo)
        flash(f"Empleado '{calculo['nombres']}' registrado correctamente.", "success")
        return redirect(url_for("detalle_empleado", employee_id=emp_id))

    return render_template("main/registrar.html", errors={}, form={}, calculo=None)


@app.route("/detalle/<int:employee_id>")
@login_required
def detalle_empleado(employee_id: int):
    emp = db.get_employee(session["user_id"], employee_id)
    if not emp:
        abort(404)
    return render_template("main/detalle.html", emp=emp)


@app.route("/eliminar/<int:employee_id>", methods=("POST",))
@login_required
def eliminar_empleado(employee_id: int):
    if db.delete_employee(session["user_id"], employee_id):
        flash("Empleado eliminado.", "info")
    else:
        flash("No se encontro el empleado.", "warning")
    return redirect(url_for("dashboard"))


# -------------------- API AJAX --------------------

@app.route("/api/check/username")
def api_check_username():
    username = (request.args.get("username") or "").strip()
    errors = validation.validate_username(username)
    if not errors and db.get_user_by_username(username):
        errors.append("Ese usuario ya esta registrado.")
    return jsonify({"valid": not errors, "errors": errors})


@app.route("/api/check/email")
def api_check_email():
    email = (request.args.get("email") or "").strip()
    errors = validation.validate_email(email)
    if not errors and db.get_user_by_email(email):
        errors.append("Ese correo ya esta registrado.")
    return jsonify({"valid": not errors, "errors": errors})


@app.route("/api/calc")
def api_calc():
    """Calculo en vivo a medida que el usuario escribe el salario."""
    nombres = (request.args.get("nombres") or "").strip()
    salario = (request.args.get("salario_bruto") or "").strip()
    errors = validation.validate_salary(salario)
    if errors:
        return jsonify({"valid": False, "errors": errors})
    calculo = payroll.calcular_salario(salario, nombres)
    # convert Decimals a float para JSON
    calculo_json = {k: (float(v) if hasattr(v, "__float__") else v) for k, v in calculo.items()}
    return jsonify({"valid": True, "calculo": calculo_json})


# -------------------- ERRORES --------------------

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
