"""Pruebas de registro, login, sesion y semilla admin (Clase 3).

    python tests/prueba_acceso.py

Usa una base SQLite TEMPORAL (no toca tu ecotech.db ni tu MariaDB) y
simula el teclado, asi que no pide nada. Requiere: pip install bcrypt
"""
import contextlib
import io
import os
import sys
import tempfile
from datetime import date
from unittest import mock

carpeta_temp = tempfile.mkdtemp()
os.environ["DB_ENGINE"] = "sqlite"
os.environ["DB_NAME"] = os.path.join(carpeta_temp, "prueba.db")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

import main as programa                                        # noqa: E402
import semilla_bd                                              # noqa: E402
from dominio.empleado import Empleado                          # noqa: E402
from menus import menu_usuario                                 # noqa: E402
from persistencia.conexion import abrir_conexion               # noqa: E402
from persistencia.crear_bd import crear_tablas                 # noqa: E402
from persistencia.empleado_dao import EmpleadoDAO              # noqa: E402
from persistencia.usuario_dao import UsuarioDAO                # noqa: E402

CLAVE_ADMIN = "clave-admin-123"


def simular(funcion, teclas=(), claves=(), modulo_getpass="menus.menu_usuario.getpass", *args):
    """Ejecuta funcion(*args) escribiendo 'teclas' (input) y 'claves' (getpass)."""
    teclas, claves = iter(teclas), iter(claves)
    pantalla = io.StringIO()
    with mock.patch("builtins.input", lambda *_: next(teclas)), \
            mock.patch(modulo_getpass, lambda *_: next(claves)), \
            mock.patch("menus.menu_usuario.limpiar_pantalla", lambda: None), \
            contextlib.redirect_stdout(pantalla):
        resultado = funcion(*args)
    return resultado, pantalla.getvalue()


def sql(consulta, parametros=()):
    conexion = abrir_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        conexion.close()


RESULTADOS = []


def anotar(nombre, esperado, obtenido, ok):
    RESULTADOS.append((nombre, esperado, obtenido, ok))


crear_tablas()

# ---------- Semilla admin (1.a ejecucion) ----------
with mock.patch("semilla_bd.getpass", side_effect=[CLAVE_ADMIN, CLAVE_ADMIN]):
    semilla_bd.cargar_cuenta_admin()
cuenta1 = UsuarioDAO.buscar_por_nombre("admin")
emp1 = EmpleadoDAO.buscar_por_correo(semilla_bd.ADMIN_CORREO)
anotar("Semilla admin (1.a vez)",
       "Crea el empleado y la cuenta 'admin' vinculada por id_empleado, con hash (no la clave)",
       f"cuenta id={cuenta1.id}, empleado_id={cuenta1.empleado_id}, hash empieza con {cuenta1.password_hash[:4]!r}",
       cuenta1.empleado_id == emp1._id and cuenta1.password_hash != CLAVE_ADMIN
       and CLAVE_ADMIN not in cuenta1.password_hash)

# ---------- Semilla admin (2.a ejecucion): no duplica ni cambia el hash ----------
filas_antes = (sql("SELECT COUNT(*) FROM empleado")[0][0], sql("SELECT COUNT(*) FROM usuario")[0][0])
with mock.patch("semilla_bd.getpass", side_effect=AssertionError("no debe pedir clave")):
    semilla_bd.cargar_cuenta_admin()
cuenta2 = UsuarioDAO.buscar_por_nombre("admin")
filas_despues = (sql("SELECT COUNT(*) FROM empleado")[0][0], sql("SELECT COUNT(*) FROM usuario")[0][0])
anotar("Semilla admin (2.a vez)",
       "Conserva empleado, cuenta (mismo ID) y hash; no pide clave ni crea filas",
       f"(empleados, usuarios) {filas_antes} -> {filas_despues}; mismo id={cuenta1.id == cuenta2.id}; mismo hash={cuenta1.password_hash == cuenta2.password_hash}",
       filas_antes == filas_despues and cuenta1.id == cuenta2.id
       and cuenta1.password_hash == cuenta2.password_hash)

# ---------- Login incorrecto ----------
r1, s1 = simular(menu_usuario.solicitar_login, ["admin"], ["clave-equivocada"])
r2, s2 = simular(menu_usuario.solicitar_login, ["noexiste"], ["lo-que-sea"])
anotar("Login incorrecto",
       "Devuelve None (sin acceso) y el MISMO mensaje para clave mala y usuario inexistente",
       f"clave mala -> {r1!r} / {s1.strip()!r}; usuario inexistente -> {r2!r} / {s2.strip()!r}",
       r1 is None and r2 is None and s1 == s2 and "Usuario o contrasena incorrectos." in s1)

# ---------- Login correcto, perfil y consulta protegida ----------
usuario, s = simular(menu_usuario.solicitar_login, [" ADMIN "], [CLAVE_ADMIN])
_, perfil = simular(menu_usuario.mostrar_perfil, (), (), "menus.menu_usuario.getpass", usuario)
datos_dolar = {"codigo": "dolar", "unidad_medida": "Pesos",
               "serie": [{"fecha": "2026-10-26T03:00:00.000Z", "valor": 945.5}]}
with mock.patch("menus.menu_indicador.obtener_datos", return_value=datos_dolar):
    _, consulta = simular(menu_usuario.consultar_indicador, (), (), "menus.menu_usuario.getpass", usuario)
with mock.patch("menus.menu_indicador.obtener_datos", side_effect=AssertionError("no debe consultar")):
    _, sin_sesion = simular(menu_usuario.consultar_indicador, (), (), "menus.menu_usuario.getpass", None)
anotar("Login correcto + opciones protegidas",
       "Devuelve la cuenta publica (sin hash); perfil y consulta funcionan; sin sesion se rechazan antes de consultar",
       f"login={usuario}; perfil={perfil.strip()!r}; consulta incluye valor={'945.50' in consulta}; sin sesion={sin_sesion.strip()!r}",
       usuario is not None and "password_hash" not in usuario and "admin" in perfil
       and "945.50 CLP por USD" in consulta and "Inicie sesion" in sin_sesion)

# ---------- Registro de cuenta (Ana) ----------
ana = Empleado("Ana Torres", "Calle 1", "+56911110001", "ana@ecotech.example",
               date(2026, 1, 1), 1000000, "Analista")
EmpleadoDAO.insertar(ana)
id_cuenta, s = simular(
    menu_usuario.solicitar_registro,
    teclas=["abc", str(ana._id), "A", "Ana_Torres"],              # ID invalido, ID ok, usuario corto, usuario ok
    claves=["123", "clave-ana-1", "clave-ana-1"])                 # clave corta, clave ok, confirmacion
cuenta_ana = UsuarioDAO.buscar_por_nombre("ana_torres")
anotar("Registro de cuenta",
       "Reintenta ID, usuario y clave invalidos; guarda hash bcrypt vinculado al empleado; NO inicia sesion (devuelve un ID, no una sesion)",
       f"id={id_cuenta}; mensajes: ID={'numero entero positivo' in s}, usuario={'entre 3 y 40' in s}, clave={'al menos 6' in s}; hash={cuenta_ana.password_hash[:4]!r}",
       isinstance(id_cuenta, int) and cuenta_ana.empleado_id == ana._id
       and "numero entero positivo" in s and "entre 3 y 40" in s and "al menos 6" in s
       and "clave-ana-1" not in cuenta_ana.password_hash and "Cuenta creada correctamente" in s)

# ---------- Registros rechazados ----------
_, s_dup = simular(menu_usuario.solicitar_registro, [str(ana._id), "otro_nombre"], ["clave-xyz-1", "clave-xyz-1"])
_, s_noemp = simular(menu_usuario.solicitar_registro, ["9999", "fantasma"], ["clave-xyz-1", "clave-xyz-1"])
_, s_noigual = simular(menu_usuario.solicitar_registro, [str(ana._id), "otro_nombre"], ["clave-xyz-1", "distinta-99"])
anotar("Registros rechazados",
       "Empleado con cuenta, empleado inexistente y claves que no coinciden: mensaje claro, sin guardar",
       f"ya tiene cuenta={'ya tiene una cuenta' in s_dup}; inexistente={'No existe un empleado' in s_noemp}; no coinciden={'no coinciden' in s_noigual}; usuarios en BD={sql('SELECT COUNT(*) FROM usuario')[0][0]}",
       "ya tiene una cuenta" in s_dup and "No existe un empleado" in s_noemp
       and "no coinciden" in s_noigual and sql("SELECT COUNT(*) FROM usuario")[0][0] == 2)

# ---------- Sesion completa con logout ----------
# login ok -> menu: 6 (perfil), Enter, 9 (cerrar sesion) -> vuelve a pedir login (falla) -> 0 salir
_, s = simular(programa.main,
               teclas=["ana_torres", "6", "", "9", "ana_torres", "0"],
               claves=["clave-ana-1", "mala-clave"])
anotar("Logout vuelve a pedir login",
       "Tras el logout se pide usuario y contrasena otra vez; con clave mala no hay acceso",
       f"'Sesion cerrada. Ingrese nuevamente.' presente={'Sesion cerrada. Ingrese nuevamente.' in s}; segundo login rechazado={'Usuario o contrasena incorrectos.' in s}",
       "Sesion iniciada correctamente." in s and "Usuario: ana_torres" in s
       and "Sesion cerrada. Ingrese nuevamente." in s and "Usuario o contrasena incorrectos." in s)

# ---------- Menu sin sesion ----------
r, s = simular(menu_usuario.menu_privado, (), (), "menus.menu_usuario.getpass", None)
anotar("Menu protegido sin sesion",
       "menu_privado(None) no muestra el menu y pide iniciar sesion",
       f"retorno={r!r}; mensaje={s.strip()!r}", r == "9" and "Debe iniciar sesion." in s)

print("\n" + "=" * 78 + "\nRESULTADO DE LAS PRUEBAS (registro, login y semilla)\n" + "=" * 78)
for nombre, esperado, obtenido, ok in RESULTADOS:
    print(f"\n[{'OK' if ok else 'FALLO'}] {nombre}\n  Esperado: {esperado}\n  Obtenido: {obtenido}")
print()
sys.exit(0 if all(r[3] for r in RESULTADOS) else 1)
