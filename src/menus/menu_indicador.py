import requests

from servicios.indicadores import URL_DOLAR, extraer_primero, obtener_datos


def mostrar_indicador():
    """Presenta el dolar observado con valor, unidad, fecha y origen."""
    try:
        datos = obtener_datos()
        fecha, valor = extraer_primero(datos)
        print(f"Dolar observado: {valor:.2f} CLP por USD")
        print(f"Fecha del registro: {fecha}")
        print(f"Origen: {URL_DOLAR}")
    except requests.exceptions.RequestException:
        # conexion, tiempo de espera, estado HTTP de error o JSON ilegible
        print("No pudimos consultar el servicio. Reintente.")
    except (ValueError, KeyError, TypeError):
        # valores invalidos, claves ausentes o tipos incorrectos
        print("La respuesta no contiene un indicador valido.")
