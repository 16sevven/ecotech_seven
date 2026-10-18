"""Semilla de datos ficticios para EcoTech.

Ejecutar desde la carpeta principal del proyecto:

    python src/semilla_bd.py

Se puede ejecutar varias veces: ANTES de insertar cada dato se comprueba
si ya existe (por correo, nombre o combinacion de campos), asi que la
segunda ejecucion no crea duplicados.
"""
from datetime import date

from persistencia.conexion import abrir_conexion
from persistencia.crear_bd import crear_tablas
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDao
from persistencia.registroTiempo_dao import RegistroTiempoDAO
from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registroTiempo import RegistroTiempo

# ---------------------------------------------------------------- datos
DEPARTAMENTOS = ["Recursos Humanos", "Desarrollo", "Operaciones"]

# (nombre, direccion, telefono, correo, fecha_contrato, salario, cargo, departamento)
EMPLEADOS = [
    ("Ana Torres", "Av. del Mar 123, La Serena", "+56911110001",
     "ana.torres@ecotech.example", date(2022, 3, 1), 1800000, "Recursos Humanos", "Recursos Humanos"),
    ("Bruno Rojas", "Calle Prat 456, Coquimbo", "+56911110002",
     "bruno.rojas@ecotech.example", date(2021, 6, 15), 2200000, "Jefe de Desarrollo", "Desarrollo"),
    ("Carla Soto", "Pasaje Los Olivos 78, La Serena", "+56911110003",
     "carla.soto@ecotech.example", date(2023, 1, 10), 1500000, "Desarrolladora", "Desarrollo"),
    ("Diego Mena", "Av. Francisco de Aguirre 900, La Serena", "+56911110004",
     "diego.mena@ecotech.example", date(2023, 8, 21), 1450000, "Analista", "Desarrollo"),
    ("Elena Paredes", "Calle Brasil 12, Ovalle", "+56911110005",
     "elena.paredes@ecotech.example", date(2020, 11, 2), 2000000, "Jefa de Operaciones", "Operaciones"),
    ("Felipe Araya", "Camino Real 340, Coquimbo", "+56911110006",
     "felipe.araya@ecotech.example", date(2024, 2, 12), 1200000, "Tecnico", "Operaciones"),
]

# departamento -> correo del empleado que lo gerencia
GERENTES = {
    "Recursos Humanos": "ana.torres@ecotech.example",
    "Desarrollo": "bruno.rojas@ecotech.example",
    "Operaciones": "elena.paredes@ecotech.example",
}

# (nombre, fecha_inicio, descripcion, departamento, correos de empleados asignados)
PROYECTOS = [
    ("Panel solar monitoreado", date(2026, 2, 1),
     "Monitoreo en linea de paneles solares de las oficinas.", "Desarrollo",
     ["bruno.rojas@ecotech.example", "carla.soto@ecotech.example", "diego.mena@ecotech.example"]),
    ("Plan de reciclaje", date(2026, 3, 15),
     "Puntos de reciclaje y reporte mensual de residuos.", "Operaciones",
     ["elena.paredes@ecotech.example", "felipe.araya@ecotech.example", "diego.mena@ecotech.example"]),
]

# (correo empleado, nombre proyecto, fecha, horas, descripcion)
REGISTROS = [
    ("bruno.rojas@ecotech.example", "Panel solar monitoreado", date(2026, 4, 6), 4, "Reunion de diseno del panel"),
    ("carla.soto@ecotech.example", "Panel solar monitoreado", date(2026, 4, 6), 6, "Desarrollo del modulo de lectura"),
    ("carla.soto@ecotech.example", "Panel solar monitoreado", date(2026, 4, 7), 7, "Pruebas del modulo de lectura"),
    ("diego.mena@ecotech.example", "Panel solar monitoreado", date(2026, 4, 7), 5, "Analisis de requisitos"),
    ("diego.mena@ecotech.example", "Plan de reciclaje", date(2026, 4, 8), 3, "Levantamiento de datos de residuos"),
    ("elena.paredes@ecotech.example", "Plan de reciclaje", date(2026, 4, 8), 8, "Planificacion de puntos de reciclaje"),
    ("felipe.araya@ecotech.example", "Plan de reciclaje", date(2026, 4, 9), 6, "Instalacion de contenedores"),
]

TABLAS = [
    "empleado", "departamento", "proyecto", "registro_tiempo",
    "departamento_empleado", "departamento_proyecto", "proyecto_empleado",
]


# ------------------------------------------------------------- utilidades
def contar_filas():
    """Cuenta las filas de cada tabla (los nombres vienen de la lista fija TABLAS)."""
    conexion = abrir_conexion()
    try:
        cursor = conexion.cursor()
        conteo = {}
        for tabla in TABLAS:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            conteo[tabla] = cursor.fetchone()[0]
        return conteo
    finally:
        conexion.close()


# ---------------------------------------------------------------- cargas
def cargar_departamentos():
    departamentos = {}
    for nombre in DEPARTAMENTOS:
        existente = DepartamentoDAO.buscar_por_nombre(nombre)
        if existente is not None:
            print(f"Ya existe departamento: {nombre}")
            departamentos[nombre] = existente
            continue
        departamento = DepartamentoDAO.insertar(Departamento(nombre))
        print(f"Creado departamento: {nombre}")
        departamentos[nombre] = departamento
    return departamentos


def cargar_empleados(departamentos):
    empleados = {}
    for (nombre, direccion, telefono, correo, fecha, salario,
         cargo, nombre_depto) in EMPLEADOS:
        existente = EmpleadoDAO.buscar_por_correo(correo)
        if existente is not None:
            print(f"Ya existe empleado: {correo}")
            empleado = existente
        else:
            empleado = Empleado(nombre, direccion, telefono, correo,
                                fecha, salario, cargo)
            EmpleadoDAO.insertar(empleado)
            print(f"Creado empleado: {correo}")
        empleados[correo] = empleado
        # agregar_empleado devuelve False si la relacion ya existia
        if DepartamentoDAO.agregar_empleado(departamentos[nombre_depto], empleado):
            print(f"  Vinculado a {nombre_depto}: {correo}")
    return empleados


def asignar_gerentes(departamentos, empleados):
    for nombre_depto, correo in GERENTES.items():
        departamento = departamentos[nombre_depto]
        gerente = empleados[correo]
        if departamento._id_gerente == gerente._id:
            print(f"Ya tiene gerente: {nombre_depto}")
            continue
        departamento._id_gerente = gerente._id
        DepartamentoDAO.actualizar(departamento)
        print(f"Gerente asignado en {nombre_depto}: {correo}")


def cargar_proyectos(departamentos, empleados):
    proyectos = {}
    for nombre, fecha, descripcion, nombre_depto, correos in PROYECTOS:
        proyecto = ProyectoDao.buscar_por_nombre(nombre, cargar_relaciones=False)
        if proyecto is not None:
            print(f"Ya existe proyecto: {nombre}")
        else:
            proyecto = ProyectoDao.insertar(Proyecto(nombre, fecha, descripcion))
            print(f"Creado proyecto: {nombre}")
        proyectos[nombre] = proyecto
        if DepartamentoDAO.agregar_proyecto(departamentos[nombre_depto], proyecto):
            print(f"  Vinculado a {nombre_depto}: {nombre}")
        for correo in correos:
            if ProyectoDao.asignar_empleado(proyecto, empleados[correo]):
                print(f"  Asignado a {nombre}: {correo}")
    return proyectos


def cargar_registros(empleados, proyectos):
    for correo, nombre_proyecto, fecha, horas, descripcion in REGISTROS:
        empleado = empleados[correo]
        proyecto = proyectos[nombre_proyecto]
        if RegistroTiempoDAO.existe_registro(empleado._id, proyecto._id_proyecto,
                                             fecha, descripcion):
            print(f"Ya existe registro: {correo} | {fecha} | {descripcion}")
            continue
        registro = RegistroTiempo(horas, fecha, descripcion, empleado, proyecto)
        if RegistroTiempoDAO.insertar(registro):
            print(f"Creado registro: {correo} | {fecha} | {horas} h")
        else:
            print(f"No se pudo crear el registro de {correo} ({descripcion})")


def mostrar_resumen(antes, despues):
    print("\n===== RESUMEN =====")
    print(f"{'Tabla':<24}{'Antes':>7}{'Despues':>9}{'Nuevos':>8}")
    for tabla in TABLAS:
        nuevos = despues[tabla] - antes[tabla]
        print(f"{tabla:<24}{antes[tabla]:>7}{despues[tabla]:>9}{nuevos:>8}")


def main():
    crear_tablas()
    antes = contar_filas()
    departamentos = cargar_departamentos()
    empleados = cargar_empleados(departamentos)
    asignar_gerentes(departamentos, empleados)
    proyectos = cargar_proyectos(departamentos, empleados)
    cargar_registros(empleados, proyectos)
    mostrar_resumen(antes, contar_filas())


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("Error al cargar la semilla:", error)
