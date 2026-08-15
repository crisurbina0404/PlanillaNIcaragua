"""Tests unitarios para payroll.py, validation.py y db.py.

Ejecuta con:  python -m pytest  -o  python tests/test_app.py
Si pytest no esta disponible, se pueden correr directamente:
    python tests/test_app.py
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# HACK para importar el paquete 'app'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import payroll, validation, db


# ---------------- payroll ----------------

def test_salario_bajo_no_aplica_ir():
    # 10,000 * 12 = 120000 -> tarifa 15%, base 0, exceso 20000
    r = payroll.calcular_salario(10000, "Juan")
    assert r["salario_bruto"] == 10000
    assert r["inss"] == 700
    assert r["renta_anual"] == 111600
    assert float(r["ir_anual"]) > 0
    assert r["ir_pct"] == 15


def test_salario_minimo_sin_ir():
    # Salario 8200 -> renta neta anual < 100000 -> tarifa 0%
    r = payroll.calcular_salario(8200, "Aux")
    assert r["ir_pct"] == 0
    assert r["ir_anual"] == 0
    assert r["ir_mensual"] == 0
    assert r["total_descuentos"] == r["inss"]
    assert r["salario_neto"] == r["salario_bruto"] - r["inss"]


def test_tarifa_maxima():
    # renta anual > 500000 -> 30%
    r = payroll.calcular_salario(80000, "Top")
    assert r["ir_pct"] == 30
    assert float(r["ir_anual"]) > 0


def test_inss_siempre_7_pct():
    for s in (1, 1000, 50000, 200000):
        r = payroll.calcular_salario(s, "X")
        assert float(r["inss"]) == round(s * 0.07, 2)


# ---------------- validation ----------------

def test_password_debil():
    errs = validation.validate_password("abc")
    assert errs


def test_password_fuerte():
    errs = validation.validate_password("Hola1234")
    assert errs == []


def test_username_caracteres_invalidos():
    assert validation.validate_username("a.b")
    assert validation.validate_username("ab")
    assert validation.validate_username("abc") == []


def test_email_invalido():
    assert validation.validate_email("noemail")
    assert validation.validate_email("a@b")
    assert validation.validate_email("a@b.com") == []


def test_salario_invalido():
    assert validation.validate_salary("-100")
    assert validation.validate_salary("abc")
    assert validation.validate_salary("") != []
    assert validation.validate_salary("1000") == []


# ---------------- db ----------------

def setup_tmp_db(monkeypatch):
    # dirige DB_PATH a un archivo temporal
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    monkeypatch.setattr(db, "DB_PATH", tmp.name)
    db.init_db()
    return tmp.name


import pytest

@pytest.fixture
def tmp_db(monkeypatch):
    path = setup_tmp_db(monkeypatch)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_admin_por_defecto(tmp_db):
    user = db.get_user_by_username("admin")
    assert user is not None
    assert user["email"] == "admin@planilla.local"
    # la contrasena por defecto debe verificarse
    assert db.verify_user("admin", "admin123") is not None


def test_crear_y_verificar_usuario(tmp_db):
    db.create_user("juan", "juan@x.com", "Hola1234", "Juan P")
    user = db.verify_user("juan", "Hola1234")
    assert user["full_name"] == "Juan P"
    # contrasena incorrecta
    assert db.verify_user("juan", "nope") is None


def test_usuario_duplicado_lanza(tmp_db):
    db.create_user("juan", "juan@x.com", "Hola1234", "Juan")
    with pytest.raises(sqlite3.IntegrityError):
        db.create_user("juan", "otro@x.com", "Hola1234", "Juan2")


def test_insert_y_list_empleado(tmp_db):
    uid = db.create_user("ana", "ana@x.com", "Hola1234", "Ana")
    calc = payroll.calcular_salario(15000, "Maria Lopez")
    emp_id = db.insert_employee(uid, calc)
    emps = db.list_employees(uid)
    assert len(emps) == 1
    assert emps[0]["id"] == emp_id
    assert emps[0]["nombres"] == "Maria Lopez"


def test_empleado_aislado_por_usuario(tmp_db):
    u1 = db.create_user("u1", "u1@x.com", "Hola1234", "Uno")
    u2 = db.create_user("u2", "u2@x.com", "Hola1234", "Dos")
    db.insert_employee(u1, payroll.calcular_salario(10000, "A"))
    db.insert_employee(u2, payroll.calcular_salario(20000, "B"))
    assert len(db.list_employees(u1)) == 1
    assert len(db.list_employees(u2)) == 1


def test_delete_empleado(tmp_db):
    uid = db.create_user("u", "u@x.com", "Hola1234", "X")
    eid = db.insert_employee(uid, payroll.calcular_salario(10000, "A"))
    assert db.delete_employee(uid, eid) is True
    assert db.delete_employee(uid, 999999) is False


if __name__ == "__main__":
    # correr manual sin pytest
    print("Tests basicos (sin pytest)...")
    test_salario_bajo_no_aplica_ir();    print("ok test_salario_bajo_no_aplica_ir")
    test_salario_minimo_sin_ir();        print("ok test_salario_minimo_sin_ir")
    test_tarifa_maxima();                  print("ok test_tarifa_maxima")
    test_inss_siempre_7_pct();             print("ok test_inss_siempre_7_pct")
    assert validation.validate_password("abc");  print("ok password_debil")
    assert validation.validate_password("Hola1234") == [];  print("ok password_fuerte")
    print("OK")
