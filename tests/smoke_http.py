"""Smoke test HTTP: prueba el flujo login -> dashboard -> registrar -> detalle.
Se debe ejecutar con el servidor corriendo en 127.0.0.1:5000.
"""
import sys
import urllib.request
import urllib.parse
import http.cookiejar
import json


def main():
    base = "http://127.0.0.1:5000"
    cookies = http.cookiejar.CookieJar()
    # NO seguir redirects automaticos: creamos un handler custom.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None  # no seguir
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies),
        NoRedirect(),
    )

    def get(path):
        try:
            r = opener.open(base + path)
            return r.status, r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace")

    def post(path, data):
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(base + path, data=body, method="POST")
        try:
            r = opener.open(req)
            return r.status, r.read().decode("utf-8", errors="replace"), r.headers.get("Location", "")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="replace"), e.headers.get("Location", "")

    failures = 0
    def check(name, cond, info=""):
        nonlocal failures
        status = "OK" if cond else "FAIL"
        if not cond:
            failures += 1
        print(f"  [{status}] {name}  {info}")

    print("== /api/calc (sin sesion, deberia responder) ==")
    code, body = get("/api/calc?nombres=Ana&salario_bruto=20000")
    obj = json.loads(body)
    check("calc responde 200", code == 200, f"code={code}")
    check("calc inss 1400", obj["calculo"]["inss"] == 1400.0, str(obj["calculo"]["inss"]))
    check("calc ir_pct 20", obj["calculo"]["ir_pct"] == 20.0, str(obj["calculo"]["ir_pct"]))
    check("calc salario_neto 16963.33", abs(obj["calculo"]["salario_neto"] - 16963.33) < 0.01,
          str(obj["calculo"]["salario_neto"]))

    print("== /api/check/username?username=admin (debe estar tomado) ==")
    code, body = get("/api/check/username?username=admin")
    obj = json.loads(body)
    check("admin ocupado", obj["valid"] is False, str(obj["valid"]))

    print("== /api/check/email invalido ==")
    code, body = get("/api/check/email?email=noemail")
    obj = json.loads(body)
    check("email invalido", obj["valid"] is False, str(obj["valid"]))

    print("== Acceso a dashboard sin login (debe redirigir a /login) ==")
    code, body = get("/dashboard")
    check("redirect 302", code == 302, f"code={code}")

    print("== Login fallido ==")
    code, body, _ = post("/login", {"username": "admin", "password": "wrong"})
    check("login fallido 401", code == 401, f"code={code}")
    check("muestra mensaje", "incorrectos" in body, "")

    print("== Login correcto (admin/admin123) ==")
    code, body, loc = post("/login", {"username": "admin", "password": "admin123"})
    check("login ok 302", code == 302, f"code={code} loc={loc}")
    check("redirect a /dashboard", loc.endswith("/dashboard"), loc)

    print("== Dashboard tras login ==")
    code, body = get("/dashboard")
    check("dashboard 200", code == 200, f"code={code}")
    check("incluye Bienvenido", "Bienvenido" in body, "")
    check("incluye lista/empty", ("empleados registrados" in body.lower()), "")

    print("== Registrar empleado Maria Jose Lopez, 25000 ==")
    code, body, loc = post("/registrar", {"nombres": "Maria Jose Lopez", "salario_bruto": "25000"})
    check("registrar 302", code == 302, f"code={code} loc={loc}")
    check("redirect a /detalle/...", "/detalle/" in loc, loc)

    # extraer id
    try:
        emp_id = int(loc.rstrip("/").rsplit("/", 1)[-1])
    except Exception:
        emp_id = 0
    check("extrae emp_id", emp_id > 0, str(emp_id))

    print("== Dashboard ahora debe mostrar al empleado ==")
    code, body = get("/dashboard")
    check("dashboard 200", code == 200)
    check("aparece Maria Jose Lopez", "Maria Jose Lopez" in body, "")
    check("aparece bruto 25000.00", "25,000.00" in body or "25000.00" in body, "")

    print("== Detalle del empleado ==")
    code, body = get(f"/detalle/{emp_id}")
    check("detalle 200", code == 200, f"code={code}")
    check("incluye INSS 1750.00", "1,750.00" in body or "1750.00" in body, "")
    check("incluye chart distChart", "distChart" in body, "")

    print("== Eliminar empleado ==")
    code, body, loc = post(f"/eliminar/{emp_id}", {})
    check("eliminar 302 a dashboard", code == 302 and loc.endswith("/dashboard"), f"code={code} loc={loc}")

    print("== Dashboard: ya sin empleado Maria Jose Lopez ==")
    code, body = get("/dashboard")
    check("empleado eliminado (Maria ya no aparece)", "Maria Jose Lopez".lower() not in body.lower(), "")

    print()
    print(f"== Resultado: {failures} fallos ==")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
