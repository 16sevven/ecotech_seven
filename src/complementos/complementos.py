import os


class OperacionCancelada(Exception):
    """Se lanza cuando la persona escribe 'cancelar' dentro de un formulario."""


PALABRA_CANCELAR = "cancelar"


def limpiar_pantalla():
    # "cls" en Windows, "clear" en Linux/Mac
    os.system("cls" if os.name == "nt" else "clear")
