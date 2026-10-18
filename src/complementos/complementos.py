import math
import os
import re
from datetime import date


class OperacionCancelada(Exception):
    """Se lanza cuando la persona escribe 'cancelar' dentro de un formulario."""


PALABRA_CANCELAR = "cancelar"
_PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def limpiar_pantalla():
    # "cls" en Windows, "clear" en Linux/Mac
    os.system("cls" if os.name == "nt" else "clear")


def _leer(etiqueta):
    """Lee una linea, le quita espacios y permite salir escribiendo 'cancelar'."""
    texto = input(f"{etiqueta}: ").strip()
    if texto.lower() == PALABRA_CANCELAR:
        raise OperacionCancelada()
    return texto


def pedir_texto_obligatorio(etiqueta, descripcion=None):
    """Repite la pregunta hasta recibir un texto no vacio.

    El break/return solo se ejecuta cuando el dato es valido; mientras
    tanto el ciclo vuelve a pedir EL MISMO campo sin perder los anteriores.
    """
    descripcion = descripcion or etiqueta.lower()
    while True:
        texto = _leer(etiqueta)
        if texto:
            return texto
        print(f"Ingrese {descripcion}. Es obligatorio.")


def pedir_correo(etiqueta, validar_extra=None):
    """Pide un correo con formato valido.

    validar_extra: funcion opcional que recibe el correo y devuelve un
    mensaje de error (str) o None si esta todo bien (por ejemplo, para
    rechazar un correo que ya existe en la base de datos).
    """
    while True:
        correo = _leer(etiqueta)
        if not correo:
            print("Ingrese un correo. Es obligatorio.")
        elif not _PATRON_CORREO.match(correo):
            print("El correo no es valido. Use el formato nombre@dominio.cl, "
                  "por ejemplo ana@ecotech.example.")
        else:
            error = validar_extra(correo) if validar_extra else None
            if error is None:
                return correo
            print(error)


def pedir_fecha(etiqueta):
    """Pide una fecha en formato AAAA-MM-DD y devuelve un objeto date."""
    while True:
        texto = _leer(etiqueta)
        if not texto:
            print("Ingrese una fecha. Es obligatoria.")
            continue
        try:
            return date.fromisoformat(texto)
        except ValueError:
            print("La fecha no es valida. Use el formato AAAA-MM-DD, "
                  "por ejemplo 2026-03-15.")


def pedir_numero(etiqueta, minimo=0, mensaje_minimo="El valor no puede ser negativo."):
    """Pide un numero decimal mayor o igual que 'minimo'."""
    while True:
        texto = _leer(etiqueta).replace(",", ".")
        if not texto:
            print("Ingrese un valor. Es obligatorio.")
            continue
        try:
            valor = float(texto)
        except ValueError:
            print("Ingrese solo numeros, por ejemplo 850000 o 850000.50.")
            continue
        if not math.isfinite(valor):          # rechaza "nan" e "inf"
            print("Ingrese solo numeros, por ejemplo 850000 o 850000.50.")
            continue
        if valor < minimo:
            print(mensaje_minimo)
            continue
        return valor
