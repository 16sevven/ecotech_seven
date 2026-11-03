"""Lectura de datos con reintento por campo (Clase 2, desafio guiado)."""
from complementos.complementos import OperacionCancelada, PALABRA_CANCELAR


def pedir_dato(mensaje, validador, leer=None, permitir_cancelar=False):
    """Pide un dato hasta que 'validador' lo acepte.

    - validador: funcion que recibe el texto, devuelve el valor limpio o
      lanza ValueError/TypeError con un mensaje que orienta al usuario.
    - leer: funcion de lectura; por defecto input (se resuelve al llamar,
      para poder simularlo en pruebas) o getpass para contrasenas.
    - permitir_cancelar: si es True, escribir 'cancelar' lanza
      OperacionCancelada para salir del formulario sin guardar.

    El ciclo solo termina con 'return' cuando el dato es valido; un dato
    incorrecto vuelve a pedir SOLO este campo.
    """
    if leer is None:
        leer = input
    while True:
        texto = leer(mensaje)
        if permitir_cancelar and isinstance(texto, str) \
                and texto.strip().lower() == PALABRA_CANCELAR:
            raise OperacionCancelada()
        try:
            return validador(texto)
        except (TypeError, ValueError) as error:
            print(f"{error} Intenta nuevamente.")
