from getpass import getpass

from complementos.complementos import limpiar_pantalla, OperacionCancelada
from dominio.Gestion_departamento import GestionDepartamento
from dominio.usuario import Usuario
from entradas import pedir_dato
from menus.menu_dominio_departamento import menu_dominio_departamento
from menus.menu_dominio_empleado import menu_dominio_empleado
from menus.menu_dominio_gestionDepartamento import menu_dominio_gestionDepartamento
from menus.menu_dominio_proyecto import menu_dominio_proyecto
from menus.menu_dominio_registroTiempo import menu_dominio_registro_tiempo
from menus.menu_indicador import mostrar_indicador
from servicios.autenticacion import autenticar, registrar_usuario


def _validar_id(texto):
    texto = str(texto).strip()
    if not (texto.isascii() and texto.isdigit()) or int(texto) <= 0:
        raise ValueError("Ingrese el ID del empleado como un numero entero positivo.")
    return int(texto)


def solicitar_registro():
    """Registro de una cuenta para un empleado existente (no inicia sesion)."""
    print("Registro de cuenta (escriba 'cancelar' en ID o usuario para salir)")
    try:
        empleado_id = pedir_dato("ID del empleado: ", _validar_id, permitir_cancelar=True)
        nombre = pedir_dato("Nuevo usuario: ", Usuario.normalizar_usuario, permitir_cancelar=True)
        clave = pedir_dato("Contrasena: ", Usuario.validar_clave, getpass)
        if clave != getpass("Repita la contrasena: "):
            print("Las contrasenas no coinciden. Vuelva al registro.")
            return None
        usuario_id = registrar_usuario(empleado_id, nombre, clave)
    except OperacionCancelada:
        print("Registro cancelado. No se guardo ninguna cuenta.")
        return None
    except (TypeError, ValueError) as error:
        print(error)
        return None
    except Exception:
        print("No se pudo crear la cuenta. Intente nuevamente.")
        return None
    print(f"Cuenta creada correctamente. ID: {usuario_id}")
    return usuario_id


def solicitar_login():
    """Pide credenciales. Devuelve los datos publicos de la cuenta o None."""
    nombre = input("Usuario: ")
    clave = getpass("Contrasena: ")
    try:
        usuario = autenticar(nombre, clave)
    except (TypeError, ValueError):
        print("No se pudo validar el acceso.")
        return None
    except Exception:
        print("No se pudo validar el acceso. Intente nuevamente.")
        return None
    if usuario is None:
        print("Usuario o contrasena incorrectos.")
    else:
        print("Sesion iniciada correctamente.")
    return usuario


def mostrar_perfil(usuario_actual):
    if usuario_actual is None:
        print("Inicie sesion para ver el perfil.")
        return
    print(f"Usuario: {usuario_actual['nombre_usuario']}")
    print(f"Empleado: {usuario_actual['empleado_id']}")


def consultar_indicador(usuario_actual):
    if usuario_actual is None:
        print("Inicie sesion para consultar indicadores.")
        return
    mostrar_indicador()          # consulta de la clase 2


def _pausa():
    input("\nPresione Enter para continuar...")


def menu_privado(usuario_actual, gestion_departamentos=None):
    """Menu principal: solo se puede usar con una sesion valida.

    Devuelve "9" (cerrar sesion) o "0" (salir del programa).
    """
    if usuario_actual is None:
        print("Debe iniciar sesion.")
        return "9"
    if gestion_departamentos is None:
        gestion_departamentos = GestionDepartamento()

    while True:
        limpiar_pantalla()
        print("\n===== ECOTECH SOLUTIONS =====")
        print(f"Sesion de: {usuario_actual['nombre_usuario']}")
        print("1. Empleado")
        print("2. Departamento")
        print("3. Proyecto")
        print("4. Registro de Tiempo")
        print("5. Registrar cuenta de usuario")
        print("6. Perfil")
        print("7. Consultar dolar")
        print("8. Gestion de Departamento (demostracion)")
        print("9. Cerrar sesion")
        print("0. Salir")
        opcion = input("Seleccione una opcion: ").strip()

        if opcion in ("0", "9"):
            return opcion

        limpiar_pantalla()
        if opcion == "1":
            menu_dominio_empleado()
        elif opcion == "2":
            menu_dominio_departamento()
        elif opcion == "3":
            menu_dominio_proyecto()
        elif opcion == "4":
            menu_dominio_registro_tiempo()
        elif opcion == "5":
            solicitar_registro()
            _pausa()
        elif opcion == "6":
            mostrar_perfil(usuario_actual)
            _pausa()
        elif opcion == "7":
            consultar_indicador(usuario_actual)
            _pausa()
        elif opcion == "8":
            menu_dominio_gestionDepartamento(gestion_departamentos)
        else:
            print("Opcion no valida.")
            _pausa()
