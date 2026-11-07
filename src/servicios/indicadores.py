"""Consulta del dolar observado (Clase 2).

Este modulo SOLO obtiene y valida datos. Mostrarlos es responsabilidad
de quien lo llama (ver menus/menu_indicador.py).
"""
import math
from datetime import date, datetime

import requests

URL_DOLAR = "https://mindicador.cl/api/dolar"
TIMEOUT = (3, 5)          # (segundos para conectar, segundos para leer)
DIAS_MAX_ANTIGUEDAD = 7   # mas antiguo que esto se advierte como posiblemente desactualizado


def obtener_datos(url=URL_DOLAR):
    """GET a la API. Devuelve el JSON ya interpretado (dict/list de Python)."""
    respuesta = requests.get(url, timeout=TIMEOUT)
    respuesta.raise_for_status()      # HTTP 4xx/5xx -> excepcion
    return respuesta.json()


def _validar_fecha(texto):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Fecha del indicador invalida.")
    try:
        momento = datetime.fromisoformat(texto.strip().replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Fecha del indicador invalida.") from None
    return momento.date().isoformat()


def extraer_primero(datos):
    """Comprueba estructura, unidad, valor y fecha; devuelve (fecha, valor).

    HTTP 200 solo dice que el servicio respondio: no garantiza que
    vengan los datos esperados, por eso se valida todo antes de usarlos.
    """
    if not isinstance(datos, dict):
        raise ValueError("Respuesta inesperada.")
    if datos.get("codigo") != "dolar":
        raise ValueError("Indicador inesperado.")
    if datos.get("unidad_medida") != "Pesos":
        raise ValueError("Unidad inesperada.")

    serie = datos.get("serie")
    if not isinstance(serie, list) or not serie:
        raise ValueError("No hay valores disponibles.")

    registro = serie[0]                      # la API entrega primero el mas reciente
    if not isinstance(registro, dict):
        raise ValueError("Registro inesperado.")
    valor = registro["valor"]                # KeyError si falta (lo controla el llamador)

    if (
        type(valor) not in (int, float)
        or not math.isfinite(valor)
        or valor <= 0
    ):
        raise ValueError("Valor del indicador invalido.")
    return _validar_fecha(registro.get("fecha")), valor


def obtener_dolar():
    """Consulta la API y devuelve el dolar observado YA VALIDADO.

    Devuelve un dict con valor, fecha, unidad y origen. Puede lanzar
    requests.exceptions.RequestException (red/HTTP/JSON) o
    ValueError/KeyError/TypeError (datos invalidos): lo controla quien llama.
    """
    fecha, valor = extraer_primero(obtener_datos())
    return {"valor": valor, "fecha": fecha, "unidad": "CLP por USD", "origen": URL_DOLAR}


def dias_de_antiguedad(fecha, hoy=None):
    """Dias entre la fecha del indicador (AAAA-MM-DD) y hoy; nunca negativo."""
    hoy = hoy or date.today()
    return max((hoy - date.fromisoformat(fecha)).days, 0)
