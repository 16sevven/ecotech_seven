"""Servicio de acceso: genera el hash, registra cuentas y verifica el login."""
import bcrypt

from dominio.usuario import Usuario
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.usuario_dao import UsuarioDAO

MAX_BYTES_BCRYPT = 72
_HASH_FALSO = None      # se crea una vez; sirve para igualar tiempos (ver autenticar)


def crear_hash(clave):
    clave = Usuario.validar_clave(clave)
    clave_bytes = clave.encode("utf-8")
    if len(clave_bytes) > MAX_BYTES_BCRYPT:
        raise ValueError("Maximo 72 bytes UTF-8 para bcrypt.")
    return bcrypt.hashpw(clave_bytes, bcrypt.gensalt()).decode("utf-8")


def registrar_usuario(empleado_id, nombre, clave):
    """Crea la cuenta de un empleado existente que aun no tiene una. Devuelve el ID."""
    nombre = Usuario.normalizar_usuario(nombre)
    if type(empleado_id) is not int or empleado_id <= 0:
        raise ValueError("El ID del empleado debe ser positivo.")
    if EmpleadoDAO.buscar_por_id(empleado_id) is None:
        raise ValueError("No existe un empleado con ese ID.")
    if UsuarioDAO.buscar_por_empleado(empleado_id) is not None:
        raise ValueError("Ese empleado ya tiene una cuenta.")
    if UsuarioDAO.buscar_por_nombre(nombre) is not None:
        raise ValueError("No se pudo crear esa cuenta.")
    hash_guardado = crear_hash(clave)
    usuario = Usuario(nombre, hash_guardado, empleado_id)
    return UsuarioDAO.insertar(usuario)


def autenticar(nombre, clave):
    """Devuelve los datos publicos de la cuenta si las credenciales son correctas; si no, None.

    No distingue 'usuario inexistente' de 'clave incorrecta' (ni en el
    mensaje ni, en lo posible, en el tiempo), para no revelar que
    usuarios existen.
    """
    global _HASH_FALSO
    nombre = Usuario.normalizar_usuario(nombre)
    if not isinstance(clave, str):
        return None
    datos = clave.encode("utf-8")
    if not 0 < len(datos) <= MAX_BYTES_BCRYPT:
        return None
    cuenta = UsuarioDAO.buscar_por_nombre(nombre)
    if cuenta is None:
        if _HASH_FALSO is None:
            _HASH_FALSO = bcrypt.hashpw(b"relleno", bcrypt.gensalt())
        bcrypt.checkpw(datos, _HASH_FALSO)       # gasta el mismo tiempo que un login real
        return None
    if not bcrypt.checkpw(datos, cuenta.password_hash.encode("utf-8")):
        return None
    return {"id": cuenta.id, "empleado_id": cuenta.empleado_id,
            "nombre_usuario": cuenta.nombre_usuario}
