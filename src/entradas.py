"""Lectura de datos con reintento por campo (Clase 2) y de contrasenas con asteriscos."""
import getpass as _getpass
import os
import sys

from complementos.complementos import OperacionCancelada, PALABRA_CANCELAR


def pedir_dato(mensaje, validador, leer=None, permitir_cancelar=False, cancelar_si_vacio=False):
    """Pide un dato hasta que 'validador' lo acepte.

    - validador: funcion que recibe el texto, devuelve el valor limpio o
      lanza ValueError/TypeError con un mensaje que orienta al usuario.
    - leer: funcion de lectura; por defecto input (se resuelve al llamar,
      para poder simularlo en pruebas) o leer_clave para contrasenas.
    - permitir_cancelar: si es True, escribir 'cancelar' lanza
      OperacionCancelada para salir del formulario sin guardar.
    - cancelar_si_vacio: si es True, dejar el campo vacio cancela
      (se usa en contrasenas, donde 'cancelar' podria ser una clave real).

    El ciclo solo termina con 'return' cuando el dato es valido; un dato
    incorrecto vuelve a pedir SOLO este campo.
    """
    if leer is None:
        leer = input
    while True:
        texto = leer(mensaje)
        if cancelar_si_vacio and texto == "":
            raise OperacionCancelada()
        if permitir_cancelar and isinstance(texto, str) \
                and texto.strip().lower() == PALABRA_CANCELAR:
            raise OperacionCancelada()
        try:
            return validador(texto)
        except (TypeError, ValueError) as error:
            print(f"{error} Intenta nuevamente.")


# ------------------------------------------------------------------ contrasenas
def _leer_clave_windows(mensaje):
    import msvcrt
    sys.stdout.write(mensaje)
    sys.stdout.flush()
    caracteres = []
    while True:
        tecla = msvcrt.getwch()
        if tecla in ("\r", "\n"):                    # Enter
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(caracteres)
        if tecla == "\x03":                          # Ctrl+C
            raise KeyboardInterrupt
        if tecla == "\b":                            # Retroceso
            if caracteres:
                caracteres.pop()
                sys.stdout.write("\b \b")
        elif tecla in ("\x00", "\xe0"):              # flechas/teclas de funcion: se ignoran
            msvcrt.getwch()
        elif tecla >= " ":                           # caracter imprimible
            caracteres.append(tecla)
            sys.stdout.write("*")
        sys.stdout.flush()


def _leer_clave_unix(mensaje):
    import termios
    import tty
    descriptor = sys.stdin.fileno()
    estado_original = termios.tcgetattr(descriptor)
    sys.stdout.write(mensaje)
    sys.stdout.flush()
    caracteres = []
    try:
        tty.setraw(descriptor)
        while True:
            tecla = sys.stdin.read(1)
            if tecla in ("\r", "\n"):
                break
            if tecla == "\x03":
                raise KeyboardInterrupt
            if tecla in ("\x7f", "\b"):
                if caracteres:
                    caracteres.pop()
                    sys.stdout.write("\b \b")
            elif tecla >= " ":
                caracteres.append(tecla)
                sys.stdout.write("*")
            sys.stdout.flush()
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, estado_original)
        sys.stdout.write("\r\n")
        sys.stdout.flush()
    return "".join(caracteres)


def leer_clave(mensaje="Contrasena: "):
    """Lee una contrasena mostrando un * por cada caracter escrito.

    Si la entrada no es una terminal real (algunos editores o consolas
    integradas), usa getpass, que no muestra nada pero es seguro.
    """
    if not sys.stdin.isatty():
        return _getpass.getpass(mensaje)
    try:
        if os.name == "nt":
            return _leer_clave_windows(mensaje)
        return _leer_clave_unix(mensaje)
    except (ImportError, OSError):
        return _getpass.getpass(mensaje)


def pedir_clave_confirmada(validador, mensaje="Contrasena: ",
                           mensaje_repetir="Repita la contrasena: ", leer=None):
    """Pide la contrasena y su confirmacion; si no coinciden, empieza de nuevo.

    Dejar la primera contrasena vacia cancela (lanza OperacionCancelada).
    """
    lector = leer or leer_clave
    print("(Deje la contrasena vacia y presione Enter para cancelar)")
    while True:
        clave = pedir_dato(mensaje, validador, lector, cancelar_si_vacio=True)
        if clave == lector(mensaje_repetir):
            return clave
        print("Las contrasenas no coinciden. Ingrese la contrasena nuevamente.")
