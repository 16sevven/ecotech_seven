import math

import requests

# API que devuelve {"serie": [{"fecha": ..., "valor": ...}, ...]}
URL_API = "https://mindicador.cl/api/dolar"

def obtener_datos():
    respuesta = requests.get(URL_API, timeout=(3, 5))
    respuesta.raise_for_status()
    return respuesta.json()

def extraer_primero(datos):
    # Verificar que la respuesta sea un diccionario.
    if not isinstance(datos, dict):
        raise ValueError("Respuesta inesperada.")

    # Obtener la lista de registros del indicador.
    serie = datos.get("serie")

    # Comprobar que sea una lista y contenga registros.
    if not isinstance(serie, list) or not serie:
        raise ValueError("No hay valores disponibles.")

    # Seleccionar el primer registro y obtener su valor.
    registro = serie[0]
    valor = registro["valor"]

    # Aceptar solo números finitos y mayores que cero.
    if (
        type(valor) not in (int, float)
        or not math.isfinite(valor)
        or valor <= 0
    ):
        raise ValueError("Valor del indicador inválido.")

    # Devolver la fecha y el valor como una tupla.
    return registro["fecha"], valor

if __name__ == "__main__":
    try:
        datos = obtener_datos()
        fecha, valor = extraer_primero(datos)
        print(f"Fecha: {fecha} | Valor: {valor}")
    except requests.RequestException as error:
        print("Error de conexión con la API:", error)
    except (ValueError, KeyError) as error:
        print("Error al procesar los datos:", error)