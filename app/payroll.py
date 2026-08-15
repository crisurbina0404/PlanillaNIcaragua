"""Cálculo de salario neto aplicando ley tributaria de Nicaragua.

Reference logic extracted from calculadoraIR.py and calculadora_salario.cpp:
  - INSS: 7% del salario bruto mensual.
  - IR: tarifa progresiva anual aplicada sobre la renta neta anual
        (salario bruto - INSS) * 12.
"""

from decimal import Decimal, ROUND_HALF_UP

TARIFA_IR = [
    # (desde, hasta, porcentaje, base)
    (Decimal("0.01"), Decimal("100000.00"), Decimal("0.00"), Decimal("0.00")),
    (Decimal("100000.01"), Decimal("200000.00"), Decimal("0.15"), Decimal("0.00")),
    (Decimal("200000.01"), Decimal("350000.00"), Decimal("0.20"), Decimal("15000.00")),
    (Decimal("350000.01"), Decimal("500000.00"), Decimal("0.25"), Decimal("45000.00")),
    (Decimal("500000.01"), Decimal("Infinity"), Decimal("0.30"), Decimal("82500.00")),
]

INSS_PORCENTAJE = Decimal("0.07")


def _round(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_ir_anual(renta_anual: Decimal):
    """Retorna (impuesto_anual, porcentaje_aplicado)."""
    for desde, hasta, pct, base in TARIFA_IR:
        if desde <= renta_anual <= hasta:
            exceso = renta_anual - desde + Decimal("0.01")
            impuesto = base + exceso * pct
            return _round(impuesto), pct
    return Decimal("0.00"), Decimal("0.00")


def calcular_salario(salario_bruto: float | int | str, nombres: str = ""):
    """Calcula los descuentos y el salario neto de un empleado.

    Retorna un dict con todos los valores formateados como Decimal a 2 decimales.
    """
    bruto = Decimal(str(salario_bruto))
    inss = _round(bruto * INSS_PORCENTAJE)
    renta_neta_mensual = _round(bruto - inss)
    renta_anual = _round(renta_neta_mensual * 12)
    ir_anual, pct = calcular_ir_anual(renta_anual)
    ir_mensual = _round(ir_anual / 12)
    total_descuentos = _round(inss + ir_mensual)
    salario_neto = _round(bruto - total_descuentos)

    return {
        "nombres": nombres,
        "salario_bruto": bruto,
        "inss": inss,
        "renta_neta_mensual": renta_neta_mensual,
        "renta_anual": renta_anual,
        "ir_anual": ir_anual,
        "ir_pct": float(pct) * 100,
        "ir_mensual": ir_mensual,
        "total_descuentos": total_descuentos,
        "salario_neto": salario_neto,
    }
