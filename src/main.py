from dominio.Gestion_departamento import GestionDepartamento
from persistencia.crear_bd import crear_tablas
from persistencia.usuario_dao import UsuarioDAO
from menus.menu_usuario import solicitar_login, menu_privado


def main():
    gestion_departamentos = GestionDepartamento()

    while True:
        usuario_actual = solicitar_login()
        if usuario_actual is None:
            if input("Enter para reintentar o 0 para salir: ").strip() == "0":
                print("Hasta luego.")
                return
            continue

        opcion = menu_privado(usuario_actual, gestion_departamentos)
        usuario_actual = None            # termina el acceso de esta sesion
        if opcion == "0":
            print("Hasta luego.")
            return
        print("Sesion cerrada. Ingrese nuevamente.")


if __name__ == "__main__":
    try:
        crear_tablas()
        if not UsuarioDAO.hay_cuentas():
            print("Aun no existe ninguna cuenta. Ejecute primero: python src/semilla_bd.py")
    except Exception as error:
        print("Error al preparar la base de datos:", error)
    else:
        main()
