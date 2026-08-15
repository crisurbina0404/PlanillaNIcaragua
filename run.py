"""Punto de entrada para ejecutar la aplicacion Flask."""

from app import app

if __name__ == "__main__":
    # use_reloader=False evita que se inicie un proceso watcher extra
    # que compita por la base de datos durante las pruebas.
    app.run(debug=False, use_reloader=False, port=5000)
