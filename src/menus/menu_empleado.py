from datetime import date
from dominio.empleado import Empleado
from persistencia.empleado_dao import EmpleadoDAO
from complementos.complementos import (
    limpiar_pantalla, OperacionCancelada, pedir_texto_obligatorio,
    pedir_correo, pedir_fecha, pedir_numero,
)


def mostrar_menu_empleado():
    print("\n===== EMPLEADOS - ECOTECH =====")
    print("1. Registrar Empleado")
    print("2. Listar Empleados")
    print("3. Buscar Empleado")
    print("4. Actualizar Empleado")
    print("5. Eliminar Empleado")
    print("0. Volver al menu principal")


def _validar_correo_disponible(correo):
    """Devuelve un mensaje si el correo ya esta usado; None si esta libre."""
    if EmpleadoDAO.buscar_por_correo(correo) is not None:
        return "Ya existe un empleado con ese correo. Ingrese otro."
    return None


def registrar_empleado():
    """Formulario de registro: cada campo se valida y se repite hasta ser correcto.

    Nada se guarda hasta que TODOS los datos son validos. Escribir
    'cancelar' en cualquier campo sale del formulario sin guardar.
    """
    print("Registro de empleado (escriba 'cancelar' para salir sin guardar)")
    try:
        nombre = pedir_texto_obligatorio("Nombre", "un nombre")
        direccion = pedir_texto_obligatorio("Direccion", "una direccion")
        numero = pedir_texto_obligatorio("Numero de telefono", "un numero de telefono")
        correo = pedir_correo("Correo", _validar_correo_disponible)
        fecha_contrato = pedir_fecha("Fecha de contrato (AAAA-MM-DD)")
        salario = pedir_numero("Salario", minimo=0,
                               mensaje_minimo="El salario no puede ser negativo.")
        cargo = pedir_texto_obligatorio("Cargo", "un cargo")

        empleado = Empleado(nombre, direccion, numero, correo,
                            fecha_contrato, salario, cargo)
        EmpleadoDAO.insertar(empleado)
        print("Empleado registrado correctamente. ID:", empleado._id)
        return empleado
    except OperacionCancelada:
        print("Registro cancelado. No se guardo ningun dato.")
    except ValueError as error:
        print("Datos incorrectos:", error)
    except Exception as error:
        print("No se pudo guardar el empleado. Revise la conexion e intente de nuevo.")
        print("Detalle:", error)
    return None


def main_empleado():
    while True:
        limpiar_pantalla()
        mostrar_menu_empleado()
        opcion = input("Seleccione una opcion: ")
        limpiar_pantalla()

        if opcion == "1":
            registrar_empleado()

        elif opcion == "2":
            try:
                empleados = EmpleadoDAO.listar()
                if not empleados:
                    print("No hay empleados registrados.")
                else:
                    for empleado in empleados:
                        print(empleado.mostrar_datos())
            except Exception as error:
                print("Error al listar empleados:", error)

        elif opcion == "3":
            try:
                id_empleado = int(input("ID del empleado: "))
                empleado = EmpleadoDAO.buscar_por_id(id_empleado)
                if empleado is None:
                    print("Empleado no encontrado.")
                else:
                    print(empleado.mostrar_datos())
                    print("Telefono:", empleado._numero)
                    print("Fecha de contrato:", empleado._fecha_contrato)
                    print("Salario:", empleado.ver_salario())
            except ValueError:
                print("Debes ingresar un ID numerico.")
            except Exception as error:
                print("Error al buscar el empleado:", error)

        elif opcion == "4":
            try:
                id_empleado = int(input("ID del empleado a actualizar: "))
                empleado = EmpleadoDAO.buscar_por_id(id_empleado)
                if empleado is None:
                    print("Empleado no encontrado.")
                    input("\nPresione Enter para continuar...")
                    continue
                print("Deja el campo vacio si no quieres modificarlo.")
                nombre = input(f"Nombre [{empleado._nombre}]: ").strip()
                direccion = input(f"Direccion [{empleado._direccion}]: ").strip()
                numero = input(f"Telefono [{empleado._numero}]: ").strip()
                correo = input(f"Correo [{empleado._correo}]: ").strip()
                fecha_texto = input(f"Fecha contrato [{empleado._fecha_contrato}] (AAAA-MM-DD): ").strip()
                salario_texto = input(f"Salario [{empleado._salario}]: ").strip()
                cargo = input(f"Cargo [{empleado._cargo}]: ").strip()
                if not (nombre or direccion or numero or correo or fecha_texto or salario_texto or cargo):
                    print("No ingresaste cambios.")
                    input("\nPresione Enter para continuar...")
                    continue
                if correo:
                    otro = EmpleadoDAO.buscar_por_correo(correo)
                    if otro is not None and otro._id != empleado._id:
                        print("Ya existe otro empleado con ese correo. No se guardaron cambios.")
                        input("\nPresione Enter para continuar...")
                        continue
                fecha = date.fromisoformat(fecha_texto) if fecha_texto else empleado._fecha_contrato
                salario = float(salario_texto) if salario_texto else empleado._salario
                actualizado = Empleado(
                    nombre=nombre or empleado._nombre,
                    direccion=direccion or empleado._direccion,
                    numero=numero or empleado._numero,
                    correo=correo or empleado._correo,
                    fecha_contrato=fecha,
                    salario=salario,
                    cargo=cargo or empleado._cargo,
                    id=empleado._id
                )
                if EmpleadoDAO.actualizar(actualizado):
                    print("Empleado actualizado correctamente.")
                else:
                    print("No se detectaron cambios guardados.")
            except ValueError as error:
                print("Datos incorrectos:", error)
            except Exception as error:
                print("Error al actualizar el empleado:", error)

        elif opcion == "5":
            try:
                id_empleado = int(input("ID del empleado a eliminar: "))
                empleado = EmpleadoDAO.buscar_por_id(id_empleado)
                if empleado is None:
                    print("Empleado no encontrado.")
                    input("\nPresione Enter para continuar...")
                    continue
                print(empleado.mostrar_datos())
                confirmar = input("Confirmar eliminacion (s/n): ").lower().strip()
                if confirmar == "s":
                    if EmpleadoDAO.eliminar(id_empleado):
                        print("Empleado eliminado.")
                    else:
                        print("No se pudo eliminar el empleado.")
                else:
                    print("Eliminacion cancelada.")
            except ValueError:
                print("Debes ingresar un ID numerico.")
            except Exception as error:
                print("Error al eliminar el empleado:", error)

        elif opcion == "0":
            return
        else:
            print("Opcion no valida.")
        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main_empleado()
