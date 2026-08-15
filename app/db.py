"""Capa de acceso a datos SQLite.

Tablas:
  - users      : usuarios que pueden iniciar sesion (login interactivo).
  - employees  : empleados registrados por cada usuario, con su calculo.

Se crea el usuario administrador por defecto (admin / admin123) la primera vez.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional

from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "planilla.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                full_name     TEXT    NOT NULL,
                created_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS employees (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id           INTEGER NOT NULL,
                nombres           TEXT    NOT NULL,
                salario_bruto     REAL    NOT NULL,
                inss              REAL    NOT NULL,
                renta_neta_mensual REAL   NOT NULL,
                renta_anual       REAL    NOT NULL,
                ir_anual          REAL    NOT NULL,
                ir_pct            REAL    NOT NULL,
                ir_mensual        REAL    NOT NULL,
                total_descuentos  REAL    NOT NULL,
                salario_neto      REAL    NOT NULL,
                created_at        TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        # Seed admin por defecto si no existe ningun usuario.
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO users (username, email, password_hash, full_name, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    "admin",
                    "admin@planilla.local",
                    generate_password_hash("admin123"),
                    "Administrador",
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                ),
            )
        conn.commit()
    finally:
        conn.close()


# ------------------- USUARIOS -------------------

def create_user(username: str, email: str, password: str, full_name: str) -> int:
    """Crea un usuario. Lanza sqlite3.IntegrityError si username/email ya existen."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, full_name, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                username,
                email,
                generate_password_hash(password),
                full_name,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def verify_user(username: str, password: str) -> Optional[dict[str, Any]]:
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


# ------------------- EMPLEADOS -------------------

def insert_employee(user_id: int, calculo: dict[str, Any]) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO employees (
                user_id, nombres, salario_bruto, inss,
                renta_neta_mensual, renta_anual,
                ir_anual, ir_pct, ir_mensual,
                total_descuentos, salario_neto, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                calculo["nombres"],
                float(calculo["salario_bruto"]),
                float(calculo["inss"]),
                float(calculo["renta_neta_mensual"]),
                float(calculo["renta_anual"]),
                float(calculo["ir_anual"]),
                float(calculo["ir_pct"]),
                float(calculo["ir_mensual"]),
                float(calculo["total_descuentos"]),
                float(calculo["salario_neto"]),
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_employees(user_id: int) -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM employees WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_employee(user_id: int, employee_id: int) -> Optional[dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM employees WHERE id = ? AND user_id = ?",
            (employee_id, user_id),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_employee(user_id: int, employee_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM employees WHERE id = ? AND user_id = ?",
            (employee_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def count_employees(user_id: int) -> int:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM employees WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
    finally:
        conn.close()


def sumary(user_id: int) -> dict[str, float]:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*)                                 AS count,
                COALESCE(SUM(salario_bruto), 0)         AS total_bruto,
                COALESCE(SUM(total_descuentos), 0)      AS total_descuentos,
                COALESCE(SUM(salario_neto), 0)          AS total_neto
            FROM employees WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
        return dict(row)
    finally:
        conn.close()
