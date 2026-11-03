"""Pruebas de la consulta del dolar (Clase 2). No usan internet: se simula la API.

    python tests/prueba_indicadores.py
"""
import contextlib
import io
import os
import sys
from unittest import mock

import requests

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from menus.menu_indicador import mostrar_indicador   # noqa: E402


class RespuestaFalsa:
    def __init__(self, datos=None, estado=200, json_ilegible=False):
        self.datos, self.estado, self.json_ilegible = datos, estado, json_ilegible

    def raise_for_status(self):
        if self.estado >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.estado}")

    def json(self):
        if self.json_ilegible:
            raise requests.exceptions.JSONDecodeError("no es JSON", "<html>", 0)
        return self.datos


def datos_con(serie=None, **cambios):
    datos = {"codigo": "dolar", "unidad_medida": "Pesos",
             "serie": [{"fecha": "2026-10-26T03:00:00.000Z", "valor": 945.5}]}
    if serie is not None:
        datos["serie"] = serie
    datos.update(cambios)
    return datos


def correr(**opciones_get):
    """Ejecuta mostrar_indicador() con requests.get simulado; devuelve lo impreso."""
    pantalla = io.StringIO()
    with mock.patch("requests.get", **opciones_get), contextlib.redirect_stdout(pantalla):
        mostrar_indicador()
    return pantalla.getvalue()


MENSAJE_RED = "No pudimos consultar el servicio. Reintente."
MENSAJE_DATO = "La respuesta no contiene un indicador valido."

casos = [
    ("1. Consulta exitosa",
     "Muestra valor con 2 decimales, unidad (CLP por USD), fecha y origen",
     dict(return_value=RespuestaFalsa(datos_con())),
     lambda s: all(x in s for x in ("945.50 CLP por USD", "2026-10-26", "https://mindicador.cl/api/dolar"))),
    ("2. Serie vacia (fallo controlado)",
     f"'{MENSAJE_DATO}' sin traceback",
     dict(return_value=RespuestaFalsa(datos_con(serie=[]))),
     lambda s: MENSAJE_DATO in s),
    ("3. Valor negativo",
     f"'{MENSAJE_DATO}'",
     dict(return_value=RespuestaFalsa(datos_con(serie=[{"fecha": "2026-10-26T03:00:00.000Z", "valor": -5}]))),
     lambda s: MENSAJE_DATO in s),
    ("4. Valor no numerico (texto)",
     f"'{MENSAJE_DATO}'",
     dict(return_value=RespuestaFalsa(datos_con(serie=[{"fecha": "2026-10-26T03:00:00.000Z", "valor": "abc"}]))),
     lambda s: MENSAJE_DATO in s),
    ("5. Falta la clave 'valor'",
     f"'{MENSAJE_DATO}'",
     dict(return_value=RespuestaFalsa(datos_con(serie=[{"fecha": "2026-10-26T03:00:00.000Z"}]))),
     lambda s: MENSAJE_DATO in s),
    ("6. Fecha invalida",
     f"'{MENSAJE_DATO}'",
     dict(return_value=RespuestaFalsa(datos_con(serie=[{"fecha": "ayer", "valor": 900.0}]))),
     lambda s: MENSAJE_DATO in s),
    ("7. Unidad inesperada",
     f"'{MENSAJE_DATO}'",
     dict(return_value=RespuestaFalsa(datos_con(unidad_medida="Euros"))),
     lambda s: MENSAJE_DATO in s),
    ("8. HTTP 200 pero JSON no es un diccionario",
     f"'{MENSAJE_DATO}' (200 no basta)",
     dict(return_value=RespuestaFalsa(["no", "es", "dict"])),
     lambda s: MENSAJE_DATO in s),
    ("9. Servicio caido (HTTP 500)",
     f"'{MENSAJE_RED}'",
     dict(return_value=RespuestaFalsa(estado=500)),
     lambda s: MENSAJE_RED in s),
    ("10. Tiempo de espera agotado",
     f"'{MENSAJE_RED}'",
     dict(side_effect=requests.exceptions.Timeout()),
     lambda s: MENSAJE_RED in s),
    ("11. Respuesta que no es JSON",
     f"'{MENSAJE_RED}'",
     dict(return_value=RespuestaFalsa(json_ilegible=True)),
     lambda s: MENSAJE_RED in s),
]

print("\n" + "=" * 78 + "\nRESULTADO DE LAS PRUEBAS (consulta del dolar)\n" + "=" * 78)
fallos = 0
for nombre, esperado, opciones, comprobar in casos:
    try:
        salida = correr(**opciones)
        ok = comprobar(salida)
    except Exception as error:                      # un traceback seria un fallo
        salida, ok = f"EXCEPCION SIN CONTROLAR: {error!r}", False
    fallos += not ok
    print(f"\n[{'OK' if ok else 'FALLO'}] {nombre}\n  Esperado: {esperado}\n  Obtenido: "
          + " | ".join(l for l in salida.strip().splitlines()))
print()
sys.exit(1 if fallos else 0)
