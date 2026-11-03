"""Tres pruebas (vacio, invalido, valido) + una extra (correo repetido)
para la operacion 'Registrar empleado'.

Ejecutar desde la carpeta principal del proyecto:

    python tests/prueba_registrar_empleado.py

Usa una base SQLite TEMPORAL: no toca tu ecotech.db ni tu MariaDB.
"""
import contextlib
import io
import os
import sys
import tempfile
from unittest import mock

# 1) Forzar SQLite temporal ANTES de importar el proyecto.
#    (python-dotenv no pisa variables que ya existen en el entorno.)
carpeta_temp = tempfile.mkdtemp()
os.environ["DB_ENGINE"] = "sqlite"
os.environ["DB_NAME"] = os.path.join(carpeta_temp, "prueba.db")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from persistencia.conexion import abrir_conexion          # noqa: E402
from persistencia.crear_bd import crear_tablas            # noqa: E402
from menus.menu_empleado import registrar_empleado        # noqa: E402


def contar_empleados():
    conexion = abrir_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM empleado")
        return cursor.fetchone()[0]
    finally:
        conexion.close()


def simular(entradas):
    """Ejecuta registrar_empleado() escribiendo 'entradas' como si fuera el usuario."""
    pendientes = iter(entradas)
    pantalla = io.StringIO()
    with mock.patch("builtins.input", lambda *_: next(pendientes)), \
            contextlib.redirect_stdout(pantalla):
        registrar_empleado()
    return pantalla.getvalue()


# Datos validos reutilizables
VALIDOS = ["Ana Torres", "Av. del Mar 123", "+56911110001",
           "ana@ecotech.example", "2026-03-15", "850000", "Analista"]

resultados = []


def registrar(nombre, esperado, obtenido, ok):
    resultados.append((nombre, esperado, obtenido, "OK" if ok else "FALLO"))


crear_tablas()

# ---- Prueba 1: VACIO -> rechaza y explica que falta, sin guardar nada vacio
antes = contar_empleados()
salida = simular(["", "   "] + VALIDOS)          # nombre vacio, luego solo espacios, luego valido
ok = ("Ingrese un nombre. Es obligatorio." in salida
      and salida.count("Es obligatorio") == 2
      and contar_empleados() == antes + 1)
registrar("1. Vacio (nombre)",
          "Muestra 'Ingrese un nombre. Es obligatorio.' y vuelve a pedir el nombre; solo se guarda el registro final valido",
          f"Mensajes de 'obligatorio': {salida.count('Es obligatorio')}; empleados {antes} -> {contar_empleados()}",
          ok)

# ---- Prueba 2: INVALIDO -> orienta sin guardar, reintenta el mismo campo
antes = contar_empleados()
salida = simular([
    "Beatriz Vega", "Calle 1", "+56922220002",
    "beatriz.com", "beatriz@ecotech.example",   # correo sin @ -> reintenta
    "31-02-2026", "2026-02-31", "2026-02-20",   # dos fechas invalidas -> reintenta
    "abc", "-500", "900000",                    # salario no numerico y negativo
    "Disenadora",
])
ok = ("El correo no es valido" in salida
      and "La fecha no es valida" in salida
      and "Ingrese solo numeros" in salida
      and "El salario no puede ser negativo." in salida
      and contar_empleados() == antes + 1)
registrar("2. Invalido (correo, fecha, salario)",
          "Muestra un mensaje por cada dato invalido, repite solo ese campo y guarda UNA sola vez al final",
          f"Mensajes de correo/fecha/numero/negativo presentes: {ok}; empleados {antes} -> {contar_empleados()}",
          ok)

# ---- Prueba 3: VALIDO -> guarda y confirma
antes = contar_empleados()
salida = simular(["Carlos Diaz", "Pasaje 5", "+56933330003",
                  "carlos@ecotech.example", "2026-01-10", "1200000", "Tecnico"])
ok = ("Empleado registrado correctamente" in salida
      and contar_empleados() == antes + 1)
registrar("3. Valido",
          "Guarda el empleado y confirma 'Empleado registrado correctamente'",
          f"Confirmacion en pantalla: {'Empleado registrado correctamente' in salida}; empleados {antes} -> {contar_empleados()}",
          ok)

# ---- Prueba extra: correo repetido
antes = contar_empleados()
salida = simular(["Otra Persona", "Calle 9", "+56944440004",
                  "CARLOS@ecotech.example",        # repetido (otra capitalizacion)
                  "otra@ecotech.example", "2026-01-11", "1000000", "Analista"])
ok = ("Ya existe un empleado con ese correo" in salida
      and contar_empleados() == antes + 1)
registrar("Extra. Correo repetido",
          "Rechaza el correo ya usado, pide otro y guarda solo el nuevo",
          f"Mensaje de duplicado presente: {'Ya existe un empleado con ese correo' in salida}; empleados {antes} -> {contar_empleados()}",
          ok)

# ---- Informe
print("\n" + "=" * 78)
print("RESULTADO DE LAS PRUEBAS")
print("=" * 78)
for nombre, esperado, obtenido, estado in resultados:
    print(f"\n[{estado}] {nombre}")
    print(f"  Esperado: {esperado}")
    print(f"  Obtenido: {obtenido}")
print()
sys.exit(0 if all(r[3] == "OK" for r in resultados) else 1)
