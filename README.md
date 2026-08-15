# Planilla Nicaragua

Aplicación web para gestionar una planilla de salarios aplicando la ley
tributaria de Nicaragua (INSS 7% e IR progresivo anual). Incluye:

- Inicio de sesión interactivo con **registro de usuarios en tiempo real**
  (validación local + verificación AJAX contra la base de datos).
- Estética y animaciones inspiradas en **Office 365** (paleta morada/azul de
  Microsoft, tipografía Segoe UI, sombras suaves, ripple en botones,
  entradas `fadeUp`, tarjetas flotantes).
- Menú principal (dashboard) con resumen, tabla de empleados registrados
  y gráficos globales con Chart.js.
- Formulario para **registrar empleados** que pide nombres + salario y
  muestra el **cálculo en tiempo real** (INSS, IR mensual/anual, neto,
  tarifa aplicada). Cada empleado queda guardado en una **base de datos
  SQLite** y aparece como un registro en el menú principal.
- Página de detalle con tabla detallada y gráficos de distribución.

## Cómo ejecutar

```bash
cd PlanillaNIcaragua
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
python run.py
```

Abre <http://localhost:5000>.

### Cuenta de ejemplo (admin por defecto)

- Usuario: `admin`
- Contraseña: `admin123`

La base de datos SQLite `planilla.db` se crea automáticamente en la raíz del
proyecto al primer arranque, junto con el usuario administrador.

## Estructura

```
PlanillaNIcaragua/
├── run.py                  # entrada (python run.py)
├── requirements.txt
├── planilla.db             # base SQLite (se genera sola)
├── app/
│   ├── __init__.py         # aplicación Flask (rutas)
│   ├── payroll.py          # cálculo de salario (INSS 7% + IR tarifa)
│   ├── db.py               # acceso a SQLite (usuarios y empleados)
│   ├── validation.py       # validaciones (servidor)
│   ├── static/css/         # estilo Office 365
│   ├── static/js/          # validación en tiempo real + gráficos
│   └── templates/          # login, registro, dashboard, registrar, detalle
└── tests/
    └── test_app.py         # tests unitarios
```

## Tests

```bash
pip install pytest
pytest -v
```

O sin pytest:

```bash
python tests/test_app.py
```

## Lógica de cálculo (ley de Nicaragua)

1. **INSS**: 7 % del salario bruto mensual.
2. **Renta neta mensual** = salario bruto − INSS.
3. **Renta anual** = renta neta mensual × 12.
4. **IR anual** según tarifa progresiva:

   | Renta anual (C$)            | Tarifa | Base (C$) |
   |------------------------------|:------:|:---------:|
   | 0.01 – 100,000.00            | 0 %    | 0         |
   | 100,000.01 – 200,000.00      | 15 %   | 0         |
   | 200,000.01 – 350,000.00      | 20 %   | 15,000    |
   | 350,000.01 – 500,000.00      | 25 %   | 45,000    |
   | más de 500,000.01            | 30 %   | 82,500    |

5. **IR mensual** = IR anual ÷ 12.
6. **Total descuentos** = INSS + IR mensual.
7. **Salario neto** = salario bruto − total descuentos.
